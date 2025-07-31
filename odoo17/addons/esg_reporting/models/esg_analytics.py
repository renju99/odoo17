from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGAnalytics(models.Model):
    _name = 'esg.analytics'
    _description = 'ESG Analytics'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Analytics Name',
        required=True,
        tracking=True,
        help="Name of the analytics report"
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    analytics_type = fields.Selection([
        ('carbon_analytics', 'Carbon Analytics'),
        ('carbon_footprint', 'Carbon Footprint'),
        ('emission_trends', 'Emission Trends'),
        ('offset_analysis', 'Offset Analysis'),
        ('sustainability_score', 'Sustainability Score'),
        ('esg_performance', 'ESG Performance'),
        ('compliance_report', 'Compliance Report'),
    ], string='Analytics Type', required=True, default='carbon_analytics')
    
    period_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period Type', required=True, default='monthly')
    
    date_from = fields.Date(
        string='Date From',
        required=True,
        tracking=True
    )
    
    date_to = fields.Date(
        string='Date To',
        required=True,
        tracking=True
    )
    
    # Carbon Analytics Fields
    total_emissions = fields.Float(
        string='Total Emissions (t CO2)',
        compute='_compute_carbon_metrics',
        store=True
    )
    
    total_offset = fields.Float(
        string='Total Offset (t CO2)',
        compute='_compute_carbon_metrics',
        store=True
    )
    
    net_emissions = fields.Float(
        string='Net Emissions (t CO2)',
        compute='_compute_carbon_metrics',
        store=True
    )
    
    emission_intensity = fields.Float(
        string='Emission Intensity (t CO2/employee)',
        compute='_compute_carbon_metrics',
        store=True
    )
    
    # ESG Performance Fields
    environmental_score = fields.Float(
        string='Environmental Score',
        default=0.0,
        tracking=True,
        help="Environmental performance score (0-100)"
    )
    
    social_score = fields.Float(
        string='Social Score',
        default=0.0,
        tracking=True,
        help="Social performance score (0-100)"
    )
    
    governance_score = fields.Float(
        string='Governance Score',
        default=0.0,
        tracking=True,
        help="Governance performance score (0-100)"
    )
    
    overall_score = fields.Float(
        string='Overall ESG Score',
        compute='_compute_overall_score',
        store=True,
        help="Overall ESG performance score"
    )
    
    # Compliance Fields
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partial', 'Partially Compliant'),
        ('pending', 'Pending Review'),
    ], string='Compliance Status', default='pending', tracking=True)
    
    compliance_notes = fields.Text(
        string='Compliance Notes',
        tracking=True
    )
    
    # Reporting Fields
    report_data = fields.Text(
        string='Report Data (JSON)',
        tracking=True,
        help="Structured data for reporting"
    )
    
    chart_type = fields.Selection([
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
    ], string='Chart Type', default='bar')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.depends('date_from', 'date_to')
    def _compute_carbon_metrics(self):
        for record in self:
            if record.date_from and record.date_to:
                # Get emissions data
                emissions = self.env['esg.emission'].get_emission_summary(
                    record.date_from, record.date_to
                )
                record.total_emissions = emissions.get('total_emissions', 0.0)
                
                # Get offset data
                offsets = self.env['esg.offset'].get_offset_summary(
                    record.date_from, record.date_to
                )
                record.total_offset = offsets.get('total_offset', 0.0)
                
                # Calculate net emissions
                record.net_emissions = record.total_emissions - record.total_offset
                
                # Calculate emission intensity
                employee_count = self.env['hr.employee'].search_count([
                    ('company_id', '=', record.company_id.id),
                    ('active', '=', True)
                ])
                if employee_count > 0:
                    record.emission_intensity = record.total_emissions / employee_count
                else:
                    record.emission_intensity = 0.0
            else:
                record.total_emissions = 0.0
                record.total_offset = 0.0
                record.net_emissions = 0.0
                record.emission_intensity = 0.0
    
    @api.depends('environmental_score', 'social_score', 'governance_score')
    def _compute_overall_score(self):
        for record in self:
            scores = [
                record.environmental_score,
                record.social_score,
                record.governance_score
            ]
            valid_scores = [s for s in scores if s > 0]
            if valid_scores:
                record.overall_score = sum(valid_scores) / len(valid_scores)
            else:
                record.overall_score = 0.0
    
    @api.constrains('environmental_score', 'social_score', 'governance_score')
    def _check_scores(self):
        for record in self:
            for field in ['environmental_score', 'social_score', 'governance_score']:
                score = getattr(record, field)
                if score < 0 or score > 100:
                    raise ValidationError(_('Scores must be between 0 and 100.'))
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_('Date From cannot be after Date To.'))
    
    def action_process(self):
        self.write({'state': 'processing'})
        try:
            # Process analytics data
            self._compute_carbon_metrics()
            self.write({'state': 'completed'})
        except Exception as e:
            _logger.error(f"Error processing analytics: {e}")
            self.write({'state': 'error'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_analytics_summary(self, date_from=None, date_to=None):
        """Get analytics summary for dashboard"""
        domain = [('state', '=', 'completed')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        analytics = self.search(domain)
        
        return {
            'total_emissions': sum(analytics.mapped('total_emissions')),
            'total_offset': sum(analytics.mapped('total_offset')),
            'net_emissions': sum(analytics.mapped('net_emissions')),
            'avg_environmental_score': sum(analytics.mapped('environmental_score')) / len(analytics) if analytics else 0,
            'avg_social_score': sum(analytics.mapped('social_score')) / len(analytics) if analytics else 0,
            'avg_governance_score': sum(analytics.mapped('governance_score')) / len(analytics) if analytics else 0,
            'avg_overall_score': sum(analytics.mapped('overall_score')) / len(analytics) if analytics else 0,
            'count': len(analytics),
        }


class ESGCarbonFootprint(models.Model):
    _name = 'esg.carbon.footprint'
    _description = 'ESG Carbon Footprint'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Footprint Name',
        required=True,
        tracking=True
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    scope = fields.Selection([
        ('scope1', 'Scope 1'),
        ('scope2', 'Scope 2'),
        ('scope3', 'Scope 3'),
        ('total', 'Total'),
    ], string='Scope', required=True, default='total')
    
    emission_source = fields.Selection([
        ('electricity', 'Electricity'),
        ('transportation', 'Transportation'),
        ('heating', 'Heating'),
        ('waste', 'Waste'),
        ('water', 'Water'),
        ('business_travel', 'Business Travel'),
        ('employee_commute', 'Employee Commute'),
        ('supply_chain', 'Supply Chain'),
        ('other', 'Other'),
    ], string='Emission Source', required=True, default='electricity')
    
    emission_amount = fields.Float(
        string='Emission Amount (t CO2)',
        required=True,
        tracking=True
    )
    
    uncertainty = fields.Float(
        string='Uncertainty (%)',
        default=0.0,
        tracking=True,
        help="Uncertainty in the emission calculation"
    )
    
    methodology = fields.Text(
        string='Methodology',
        tracking=True,
        help="Methodology used for calculation"
    )
    
    verification_status = fields.Selection([
        ('not_verified', 'Not Verified'),
        ('self_verified', 'Self Verified'),
        ('third_party_verified', 'Third Party Verified'),
    ], string='Verification Status', default='not_verified', tracking=True)
    
    verified_by = fields.Char(
        string='Verified By',
        tracking=True
    )
    
    verification_date = fields.Date(
        string='Verification Date',
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.constrains('emission_amount')
    def _check_emission_amount(self):
        for record in self:
            if record.emission_amount < 0:
                raise ValidationError(_('Emission amount cannot be negative.'))
    
    @api.constrains('uncertainty')
    def _check_uncertainty(self):
        for record in self:
            if record.uncertainty < 0 or record.uncertainty > 100:
                raise ValidationError(_('Uncertainty must be between 0 and 100.'))