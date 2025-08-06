from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGEmployeeCommunity(models.Model):
    _name = 'esg.employee.community'
    _description = 'ESG Employee Community'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Activity Name',
        required=True,
        tracking=True,
        help="Name of the community activity or commute record"
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
        help="Employee participating in the activity"
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    activity_type = fields.Selection([
        ('commute', 'Commute'),
        ('community_service', 'Community Service'),
        ('volunteering', 'Volunteering'),
        ('charity', 'Charity'),
        ('education', 'Education'),
        ('other', 'Other'),
    ], string='Activity Type', required=True, default='commute')
    
    commute_type = fields.Selection([
        ('car', 'Car'),
        ('public_transport', 'Public Transport'),
        ('bicycle', 'Bicycle'),
        ('walking', 'Walking'),
        ('carpool', 'Carpool'),
        ('electric_vehicle', 'Electric Vehicle'),
        ('other', 'Other'),
    ], string='Commute Type', help="Type of transportation used")
    
    distance = fields.Float(
        string='Distance (km)',
        tracking=True,
        help="Distance traveled in kilometers"
    )
    
    duration = fields.Float(
        string='Duration (hours)',
        tracking=True,
        help="Duration of the activity in hours"
    )
    
    emission_amount = fields.Float(
        string='Emission Amount (t CO2)',
        compute='_compute_emission_amount',
        store=True,
        help="Calculated emission amount from commute"
    )
    
    cost = fields.Monetary(
        string='Cost',
        currency_field='currency_id',
        tracking=True,
        help="Cost associated with the activity"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    location = fields.Char(
        string='Location',
        tracking=True,
        help="Location of the activity"
    )
    
    description = fields.Text(
        string='Description',
        tracking=True,
        help="Detailed description of the activity"
    )
    
    notes = fields.Text(
        string='Notes',
        tracking=True,
        help="Additional notes about the activity"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    
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
    
    @api.depends('distance', 'commute_type')
    def _compute_emission_amount(self):
        for record in self:
            if record.distance and record.commute_type:
                # Emission factors for different commute types (t CO2/km)
                emission_factors = {
                    'car': 0.0002,  # 0.2 kg CO2/km
                    'public_transport': 0.00005,  # 0.05 kg CO2/km
                    'bicycle': 0.0,
                    'walking': 0.0,
                    'carpool': 0.0001,  # 0.1 kg CO2/km (shared)
                    'electric_vehicle': 0.00005,  # 0.05 kg CO2/km
                    'other': 0.00015,  # 0.15 kg CO2/km
                }
                factor = emission_factors.get(record.commute_type, 0.0)
                record.emission_amount = record.distance * factor
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
    
    @api.constrains('distance')
    def _check_distance(self):
        for record in self:
            if record.distance and record.distance < 0:
                raise ValidationError(_('Distance cannot be negative.'))
    
    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration and record.duration < 0:
                raise ValidationError(_('Duration cannot be negative.'))
    
    def action_submit(self):
        self.write({'state': 'submitted'})
    
    def action_approve(self):
        self.write({'state': 'approved'})
    
    def action_reject(self):
        self.write({'state': 'rejected'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_community_summary(self, date_from=None, date_to=None):
        """Get community activity summary for reporting"""
        domain = [('state', '=', 'approved')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        activities = self.search(domain)
        
        return {
            'total_emissions': sum(activities.mapped('emission_amount')),
            'total_cost': sum(activities.mapped('cost')),
            'total_distance': sum(activities.mapped('distance')),
            'count': len(activities),
            'by_type': activities.read_group(
                domain, 
                ['activity_type', 'emission_amount:sum'], 
                ['activity_type']
            ),
            'by_commute': activities.read_group(
                domain, 
                ['commute_type', 'emission_amount:sum'], 
                ['commute_type']
            ),
        }


class ESGCommunityInitiative(models.Model):
    _name = 'esg.community.initiative'
    _description = 'ESG Community Initiative'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Initiative Name',
        required=True,
        tracking=True
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    initiative_type = fields.Selection([
        ('volunteering', 'Volunteering'),
        ('charity', 'Charity'),
        ('education', 'Education'),
        ('health', 'Health'),
        ('environment', 'Environment'),
        ('social', 'Social'),
        ('other', 'Other'),
    ], string='Initiative Type', required=True, default='volunteering')
    
    description = fields.Text(
        string='Description',
        tracking=True
    )
    
    participants_count = fields.Integer(
        string='Number of Participants',
        tracking=True,
        help="Number of employees participating"
    )
    
    hours_spent = fields.Float(
        string='Hours Spent',
        tracking=True,
        help="Total hours spent on the initiative"
    )
    
    impact_score = fields.Selection([
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Exceptional'),
    ], string='Impact Score', default='3')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    def action_activate(self):
        self.write({'state': 'active'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})