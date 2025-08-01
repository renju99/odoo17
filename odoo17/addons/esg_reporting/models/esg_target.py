from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGTarget(models.Model):
    _name = 'esg.target'
    _description = 'ESG Target'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Target Name',
        required=True,
        tracking=True,
        help="Name of the ESG target"
    )
    
    target_type = fields.Selection([
        ('emission_reduction', 'Emission Reduction'),
        ('energy_efficiency', 'Energy Efficiency'),
        ('renewable_energy', 'Renewable Energy'),
        ('waste_reduction', 'Waste Reduction'),
        ('water_conservation', 'Water Conservation'),
        ('diversity_inclusion', 'Diversity & Inclusion'),
        ('employee_satisfaction', 'Employee Satisfaction'),
        ('community_impact', 'Community Impact'),
        ('supply_chain_sustainability', 'Supply Chain Sustainability'),
        ('governance_improvement', 'Governance Improvement'),
        ('custom', 'Custom Target'),
    ], string='Target Type', required=True, default='emission_reduction')
    
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
        ('economic', 'Economic'),
    ], string='Category', required=True, default='environmental')
    
    # Target Setting
    baseline_year = fields.Integer(
        string='Baseline Year',
        required=True,
        default=lambda self: fields.Date.today().year - 1,
        tracking=True
    )
    
    baseline_value = fields.Float(
        string='Baseline Value',
        required=True,
        tracking=True,
        help="Baseline value for the target metric"
    )
    
    baseline_unit = fields.Selection([
        ('t_co2', 't CO2'),
        ('kwh', 'kWh'),
        ('mwh', 'MWh'),
        ('kg', 'kg'),
        ('ton', 'ton'),
        ('liter', 'liter'),
        ('m3', 'm³'),
        ('percent', '%'),
        ('number', 'Number'),
        ('currency', 'Currency'),
    ], string='Baseline Unit', required=True, default='t_co2')
    
    target_year = fields.Integer(
        string='Target Year',
        required=True,
        default=lambda self: fields.Date.today().year + 5,
        tracking=True
    )
    
    target_value = fields.Float(
        string='Target Value',
        required=True,
        tracking=True,
        help="Target value to achieve by target year"
    )
    
    target_unit = fields.Selection([
        ('t_co2', 't CO2'),
        ('kwh', 'kWh'),
        ('mwh', 'MWh'),
        ('kg', 'kg'),
        ('ton', 'ton'),
        ('liter', 'liter'),
        ('m3', 'm³'),
        ('percent', '%'),
        ('number', 'Number'),
        ('currency', 'Currency'),
    ], string='Target Unit', required=True, default='t_co2')
    
    reduction_percentage = fields.Float(
        string='Reduction Percentage (%)',
        compute='_compute_reduction_percentage',
        store=True,
        help="Percentage reduction from baseline to target"
    )
    
    # Science-Based Target Settings
    is_science_based = fields.Boolean(
        string='Science-Based Target',
        default=False,
        tracking=True,
        help="Whether this target follows SBTi methodology"
    )
    
    sbti_category = fields.Selection([
        ('well_below_2c', 'Well Below 2°C'),
        ('below_2c', 'Below 2°C'),
        ('below_1_5c', 'Below 1.5°C'),
        ('custom', 'Custom'),
    ], string='SBTi Category', tracking=True)
    
    sbti_approved = fields.Boolean(
        string='SBTi Approved',
        default=False,
        tracking=True
    )
    
    approval_date = fields.Date(
        string='Approval Date',
        tracking=True
    )
    
    # Progress Tracking
    current_value = fields.Float(
        string='Current Value',
        compute='_compute_current_value',
        store=True,
        help="Current value of the target metric"
    )
    
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True,
        help="Progress towards target as percentage"
    )
    
    is_on_track = fields.Boolean(
        string='On Track',
        compute='_compute_on_track',
        store=True,
        help="Whether the target is on track to be achieved"
    )
    
    # Milestones
    milestone_ids = fields.One2many(
        'esg.target.milestone',
        'target_id',
        string='Milestones',
        help="Intermediate milestones for the target"
    )
    
    # Risk Assessment
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Risk Level', default='medium', tracking=True)
    
    risk_factors = fields.Text(
        string='Risk Factors',
        tracking=True,
        help="Factors that may prevent target achievement"
    )
    
    mitigation_strategies = fields.Text(
        string='Mitigation Strategies',
        tracking=True,
        help="Strategies to mitigate risks"
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('at_risk', 'At Risk'),
        ('missed', 'Missed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Integration
    data_source_model = fields.Char(
        string='Data Source Model',
        tracking=True,
        help="Odoo model that provides data for this target"
    )
    
    data_source_field = fields.Char(
        string='Data Source Field',
        tracking=True,
        help="Field in the model that provides data"
    )
    
    calculation_method = fields.Text(
        string='Calculation Method',
        tracking=True,
        help="Method for calculating current value"
    )
    
    # Additional Fields
    description = fields.Text(
        string='Description',
        tracking=True
    )
    
    rationale = fields.Text(
        string='Rationale',
        tracking=True,
        help="Rationale for setting this target"
    )
    
    stakeholders = fields.Text(
        string='Stakeholders',
        tracking=True,
        help="Key stakeholders involved in target achievement"
    )
    
    budget = fields.Monetary(
        string='Budget',
        currency_field='currency_id',
        tracking=True,
        help="Budget allocated for target achievement"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.depends('baseline_value', 'target_value')
    def _compute_reduction_percentage(self):
        for record in self:
            if record.baseline_value and record.target_value:
                if record.baseline_value > 0:
                    reduction = ((record.baseline_value - record.target_value) / record.baseline_value) * 100
                    record.reduction_percentage = max(0, reduction)
                else:
                    record.reduction_percentage = 0.0
            else:
                record.reduction_percentage = 0.0
    
    @api.depends('data_source_model', 'data_source_field')
    def _compute_current_value(self):
        for record in self:
            if record.data_source_model and record.data_source_field:
                model = self.env.get(record.data_source_model)
                if model:
                    # Get current year data
                    current_year = fields.Date.today().year
                    domain = []
                    if hasattr(model, 'company_id'):
                        domain.append(('company_id', '=', record.company_id.id))
                    if hasattr(model, 'date'):
                        domain.append(('date', '>=', f'{current_year}-01-01'))
                        domain.append(('date', '<=', f'{current_year}-12-31'))
                    
                    records = model.search(domain)
                    if records:
                        if record.data_source_field in records[0]._fields:
                            current_value = sum(records.mapped(record.data_source_field))
                            record.current_value = current_value
                        else:
                            record.current_value = 0.0
                    else:
                        record.current_value = 0.0
                else:
                    record.current_value = 0.0
            else:
                record.current_value = 0.0
    
    @api.depends('current_value', 'baseline_value', 'target_value')
    def _compute_progress(self):
        for record in self:
            if record.baseline_value and record.target_value and record.current_value is not None:
                if record.baseline_value != record.target_value:
                    # Calculate progress based on reduction/increase
                    total_change = record.baseline_value - record.target_value
                    current_change = record.baseline_value - record.current_value
                    
                    if total_change != 0:
                        progress = (current_change / total_change) * 100
                        record.progress_percentage = max(0, min(100, progress))
                    else:
                        record.progress_percentage = 0.0
                else:
                    record.progress_percentage = 0.0
            else:
                record.progress_percentage = 0.0
    
    @api.depends('progress_percentage', 'target_year')
    def _compute_on_track(self):
        for record in self:
            current_year = fields.Date.today().year
            years_elapsed = current_year - record.baseline_year
            total_years = record.target_year - record.baseline_year
            
            if total_years > 0:
                expected_progress = (years_elapsed / total_years) * 100
                record.is_on_track = record.progress_percentage >= expected_progress
            else:
                record.is_on_track = True
    
    @api.constrains('baseline_year', 'target_year')
    def _check_years(self):
        for record in self:
            if record.baseline_year >= record.target_year:
                raise ValidationError(_('Target year must be after baseline year.'))
    
    @api.constrains('baseline_value', 'target_value')
    def _check_values(self):
        for record in self:
            if record.baseline_value < 0 or record.target_value < 0:
                raise ValidationError(_('Baseline and target values cannot be negative.'))
    
    def action_activate(self):
        self.write({'state': 'active'})
    
    def action_achieve(self):
        self.write({'state': 'achieved'})
    
    def action_at_risk(self):
        self.write({'state': 'at_risk'})
    
    def action_missed(self):
        self.write({'state': 'missed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_targets_summary(self, category=None):
        """Get summary of all targets"""
        domain = [('state', 'in', ['active', 'achieved'])]
        if category:
            domain.append(('category', '=', category))
        
        targets = self.search(domain)
        
        return {
            'total_targets': len(targets),
            'active_targets': len(targets.filtered(lambda t: t.state == 'active')),
            'achieved_targets': len(targets.filtered(lambda t: t.state == 'achieved')),
            'on_track_targets': len(targets.filtered(lambda t: t.is_on_track)),
            'at_risk_targets': len(targets.filtered(lambda t: not t.is_on_track)),
            'avg_progress': sum(targets.mapped('progress_percentage')) / len(targets) if targets else 0,
        }


class ESGTargetMilestone(models.Model):
    _name = 'esg.target.milestone'
    _description = 'ESG Target Milestone'
    _order = 'target_id, date'

    name = fields.Char(
        string='Milestone Name',
        required=True
    )
    
    target_id = fields.Many2one(
        'esg.target',
        string='Target',
        required=True,
        ondelete='cascade'
    )
    
    date = fields.Date(
        string='Milestone Date',
        required=True
    )
    
    expected_value = fields.Float(
        string='Expected Value',
        required=True,
        help="Expected value at this milestone"
    )
    
    actual_value = fields.Float(
        string='Actual Value',
        help="Actual value achieved at this milestone"
    )
    
    achieved = fields.Boolean(
        string='Achieved',
        compute='_compute_achieved',
        store=True
    )
    
    variance = fields.Float(
        string='Variance',
        compute='_compute_variance',
        store=True,
        help="Difference between expected and actual value"
    )
    
    variance_percentage = fields.Float(
        string='Variance (%)',
        compute='_compute_variance_percentage',
        store=True
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')
    
    @api.depends('actual_value', 'expected_value')
    def _compute_achieved(self):
        for record in self:
            if record.actual_value is not None and record.expected_value is not None:
                # For reduction targets, actual should be <= expected
                # For increase targets, actual should be >= expected
                if record.target_id.target_value < record.target_id.baseline_value:
                    # Reduction target
                    record.achieved = record.actual_value <= record.expected_value
                else:
                    # Increase target
                    record.achieved = record.actual_value >= record.expected_value
            else:
                record.achieved = False
    
    @api.depends('actual_value', 'expected_value')
    def _compute_variance(self):
        for record in self:
            if record.actual_value is not None and record.expected_value is not None:
                record.variance = record.actual_value - record.expected_value
            else:
                record.variance = 0.0
    
    @api.depends('variance', 'expected_value')
    def _compute_variance_percentage(self):
        for record in self:
            if record.expected_value and record.expected_value != 0:
                record.variance_percentage = (record.variance / record.expected_value) * 100
            else:
                record.variance_percentage = 0.0
    
    def action_achieve(self):
        self.write({'state': 'achieved'})
    
    def action_miss(self):
        self.write({'state': 'missed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_pending(self):
        self.write({'state': 'pending'})