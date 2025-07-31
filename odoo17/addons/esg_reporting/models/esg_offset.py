from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGOffset(models.Model):
    _name = 'esg.offset'
    _description = 'ESG Offset Emissions'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Offset Name',
        required=True,
        tracking=True,
        help="Name of the offset activity (e.g., Tree Planting, Renewable Energy)"
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
        help="Partner providing the offset service"
    )
    
    offset_type_id = fields.Many2one(
        'esg.offset.type',
        string='Offset Type',
        required=True,
        tracking=True,
        help="Type of offset activity"
    )
    
    quantity = fields.Float(
        string='Quantity',
        required=True,
        tracking=True,
        help="Quantity of offset units"
    )
    
    unit = fields.Selection([
        ('t_co2', 't CO2'),
        ('tree', 'Tree'),
        ('kwh', 'kWh'),
        ('acre', 'Acre'),
        ('hectare', 'Hectare'),
        ('kg', 'kg'),
    ], string='Unit', required=True, default='t_co2')
    
    offset_amount = fields.Float(
        string='Offset Amount (t CO2)',
        compute='_compute_offset_amount',
        store=True,
        help="Calculated offset amount in tons of CO2"
    )
    
    amount = fields.Monetary(
        string='Cost',
        currency_field='currency_id',
        tracking=True,
        help="Cost of the offset activity"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    certificate_number = fields.Char(
        string='Certificate Number',
        tracking=True,
        help="Certificate number for the offset activity"
    )
    
    certificate_date = fields.Date(
        string='Certificate Date',
        tracking=True
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
    
    @api.depends('quantity', 'offset_type_id')
    def _compute_offset_amount(self):
        for record in self:
            if record.quantity and record.offset_type_id:
                record.offset_amount = record.quantity * record.offset_type_id.factor
            else:
                record.offset_amount = 0.0
    
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
    def get_offset_summary(self, date_from=None, date_to=None):
        """Get offset summary for reporting"""
        domain = [('state', '=', 'validated')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        offsets = self.search(domain)
        
        return {
            'total_offset': sum(offsets.mapped('offset_amount')),
            'total_cost': sum(offsets.mapped('amount')),
            'count': len(offsets),
            'by_type': offsets.read_group(
                domain, 
                ['offset_type_id', 'offset_amount:sum'], 
                ['offset_type_id']
            ),
        }


class ESGOffsetType(models.Model):
    _name = 'esg.offset.type'
    _description = 'ESG Offset Type'
    _order = 'name'

    name = fields.Char(
        string='Type Name',
        required=True,
        help="Name of the offset type (e.g., Tree Planting, Renewable Energy)"
    )
    
    factor = fields.Float(
        string='Offset Factor (t CO2/unit)',
        required=True,
        help="Offset factor in tons of CO2 per unit"
    )
    
    unit = fields.Selection([
        ('t_co2', 't CO2'),
        ('tree', 'Tree'),
        ('kwh', 'kWh'),
        ('acre', 'Acre'),
        ('kg', 'kg'),
        ('hectare', 'Hectare'),
    ], string='Unit', required=True, default='t_co2')
    
    category = fields.Selection([
        ('reforestation', 'Reforestation'),
        ('renewable_energy', 'Renewable Energy'),
        ('energy_efficiency', 'Energy Efficiency'),
        ('methane_capture', 'Methane Capture'),
        ('ocean_cleanup', 'Ocean Cleanup'),
        ('other', 'Other'),
    ], string='Category', required=True, default='reforestation')
    
    description = fields.Text(
        string='Description',
        help="Detailed description of the offset type"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    @api.constrains('factor')
    def _check_factor(self):
        for record in self:
            if record.factor < 0:
                raise ValidationError(_('Offset factor cannot be negative.'))
