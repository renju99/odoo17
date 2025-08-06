from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGInitiative(models.Model):
    _name = 'esg.initiative'
    _description = 'ESG Initiative'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Initiative Name',
        required=True,
        tracking=True,
        help="Name of the ESG initiative"
    )
    
    date = fields.Date(
        string='Start Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    end_date = fields.Date(
        string='End Date',
        tracking=True,
        help="Expected end date of the initiative"
    )
    
    initiative_type = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
        ('sustainability', 'Sustainability'),
        ('carbon_reduction', 'Carbon Reduction'),
        ('energy_efficiency', 'Energy Efficiency'),
        ('waste_reduction', 'Waste Reduction'),
        ('water_conservation', 'Water Conservation'),
        ('biodiversity', 'Biodiversity'),
        ('community_development', 'Community Development'),
        ('employee_wellbeing', 'Employee Wellbeing'),
        ('diversity_inclusion', 'Diversity & Inclusion'),
        ('ethical_sourcing', 'Ethical Sourcing'),
        ('transparency', 'Transparency'),
        ('compliance', 'Compliance'),
        ('other', 'Other'),
    ], string='Initiative Type', required=True, default='environmental')
    
    category = fields.Selection([
        ('e', 'Environmental'),
        ('s', 'Social'),
        ('g', 'Governance'),
    ], string='ESG Category', required=True, default='e')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='1', tracking=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
        help="Person responsible for this initiative"
    )
    
    team_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
        help="Department responsible for this initiative"
    )
    
    description = fields.Text(
        string='Description',
        tracking=True,
        help="Detailed description of the initiative"
    )
    
    objectives = fields.Text(
        string='Objectives',
        tracking=True,
        help="Specific objectives of this initiative"
    )
    
    expected_impact = fields.Text(
        string='Expected Impact',
        tracking=True,
        help="Expected environmental, social, or governance impact"
    )
    
    budget = fields.Monetary(
        string='Budget',
        currency_field='currency_id',
        tracking=True,
        help="Budget allocated for this initiative"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    actual_cost = fields.Monetary(
        string='Actual Cost',
        currency_field='currency_id',
        tracking=True,
        help="Actual cost incurred for this initiative"
    )
    
    progress = fields.Float(
        string='Progress (%)',
        default=0.0,
        tracking=True,
        help="Progress percentage of the initiative"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    tags = fields.Many2many(
        'esg.initiative.tag',
        string='Tags',
        help="Tags to categorize the initiative"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed fields
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration',
        store=True
    )
    
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_overdue',
        store=True
    )
    
    @api.depends('date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.date and record.end_date:
                delta = record.end_date - record.date
                record.duration_days = delta.days
            else:
                record.duration_days = 0
    
    @api.depends('end_date', 'state')
    def _compute_overdue(self):
        for record in self:
            if record.end_date and record.state in ['active', 'on_hold']:
                record.is_overdue = fields.Date.today() > record.end_date
            else:
                record.is_overdue = False
    
    @api.constrains('progress')
    def _check_progress(self):
        for record in self:
            if record.progress < 0 or record.progress > 100:
                raise ValidationError(_('Progress must be between 0 and 100.'))
    
    @api.constrains('end_date')
    def _check_end_date(self):
        for record in self:
            if record.end_date and record.date and record.end_date < record.date:
                raise ValidationError(_('End date cannot be before start date.'))
    
    def action_activate(self):
        self.write({'state': 'active'})
    
    def action_hold(self):
        self.write({'state': 'on_hold'})
    
    def action_complete(self):
        self.write({'state': 'completed', 'progress': 100.0})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_initiative_summary(self, date_from=None, date_to=None):
        """Get initiative summary for reporting"""
        domain = []
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        initiatives = self.search(domain)
        
        return {
            'total_budget': sum(initiatives.mapped('budget')),
            'total_cost': sum(initiatives.mapped('actual_cost')),
            'count': len(initiatives),
            'by_type': initiatives.read_group(
                domain, 
                ['initiative_type', 'budget:sum'], 
                ['initiative_type']
            ),
            'by_category': initiatives.read_group(
                domain, 
                ['category', 'budget:sum'], 
                ['category']
            ),
            'by_state': initiatives.read_group(
                domain, 
                ['state', 'budget:sum'], 
                ['state']
            ),
        }


class ESGInitiativeTag(models.Model):
    _name = 'esg.initiative.tag'
    _description = 'ESG Initiative Tag'
    _order = 'name'

    name = fields.Char(
        string='Tag Name',
        required=True,
        help="Name of the tag"
    )
    
    color = fields.Integer(
        string='Color Index',
        help="Color index for the tag"
    )
    
    description = fields.Text(
        string='Description',
        help="Description of the tag"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )