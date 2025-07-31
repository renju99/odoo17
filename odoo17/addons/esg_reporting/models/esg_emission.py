from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGEmissions(models.Model):
    _name = 'esg.emission'
    _description = 'ESG Emissions'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Emission Name',
        required=True,
        tracking=True,
        help="Name of the emission source (e.g., Electricity, Transportation)"
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        tracking=True,
        help="Partner responsible for this emission"
    )
    
    emission_factor_id = fields.Many2one(
        'esg.emission.factor',
        string='Emission Factor',
        required=True,
        tracking=True,
        help="Type of emission factor (e.g., Grid Electricity, Transportation)"
    )
    
    quantity = fields.Float(
        string='Quantity',
        required=True,
        tracking=True,
        help="Quantity of the emission source used"
    )
    
    unit = fields.Selection([
        ('kwh', 'kWh'),
        ('km', 'km'),
        ('kg', 'kg'),
        ('liter', 'Liter'),
        ('ton', 'Ton'),
        ('m3', 'm³'),
    ], string='Unit', required=True, default='kwh')
    
    emission_amount = fields.Float(
        string='Emission Amount (t CO2)',
        compute='_compute_emission_amount',
        store=True,
        help="Calculated emission amount in tons of CO2"
    )
    
    amount = fields.Monetary(
        string='Cost',
        currency_field='currency_id',
        tracking=True,
        help="Cost associated with this emission"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        tracking=True,
        help="Journal for accounting entries"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(
        string='Notes',
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed fields for reporting
    month = fields.Char(
        string='Month',
        compute='_compute_period_fields',
        store=True
    )
    
    year = fields.Integer(
        string='Year',
        compute='_compute_period_fields',
        store=True
    )
    
    @api.depends('quantity', 'emission_factor_id')
    def _compute_emission_amount(self):
        for record in self:
            if record.quantity and record.emission_factor_id:
                record.emission_amount = record.quantity * record.emission_factor_id.factor
            else:
                record.emission_amount = 0.0
    
    @api.depends('date')
    def _compute_period_fields(self):
        for record in self:
            if record.date:
                record.month = record.date.strftime('%B %Y')
                record.year = record.date.year
            else:
                record.month = ''
                record.year = 0
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than zero.'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_validate(self):
        self.write({'state': 'validated'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_emission_summary(self, date_from=None, date_to=None):
        """Get emission summary for reporting"""
        domain = [('state', '=', 'validated')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        emissions = self.search(domain)
        
        return {
            'total_emissions': sum(emissions.mapped('emission_amount')),
            'total_cost': sum(emissions.mapped('amount')),
            'count': len(emissions),
            'by_factor': emissions.read_group(
                domain, 
                ['emission_factor_id', 'emission_amount:sum'], 
                ['emission_factor_id']
            ),
        }


class ESGEmissionFactor(models.Model):
    _name = 'esg.emission.factor'
    _description = 'ESG Emission Factor'
    _order = 'name'

    name = fields.Char(
        string='Factor Name',
        required=True,
        help="Name of the emission factor (e.g., Grid Electricity, Car Transportation)"
    )
    
    factor = fields.Float(
        string='Emission Factor (t CO2/unit)',
        required=True,
        help="Emission factor in tons of CO2 per unit"
    )
    
    unit = fields.Selection([
        ('kwh', 'kWh'),
        ('km', 'km'),
        ('kg', 'kg'),
        ('liter', 'Liter'),
        ('ton', 'Ton'),
        ('m3', 'm³'),
    ], string='Unit', required=True, default='kwh')
    
    category = fields.Selection([
        ('electricity', 'Electricity'),
        ('transportation', 'Transportation'),
        ('heating', 'Heating'),
        ('waste', 'Waste'),
        ('water', 'Water'),
        ('other', 'Other'),
    ], string='Category', required=True, default='electricity')
    
    description = fields.Text(
        string='Description',
        help="Detailed description of the emission factor"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    @api.constrains('factor')
    def _check_factor(self):
        for record in self:
            if record.factor < 0:
                raise ValidationError(_('Emission factor cannot be negative.'))