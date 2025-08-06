from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGPayGap(models.Model):
    _name = 'esg.pay.gap'
    _description = 'ESG Pay Gap'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Report Name',
        required=True,
        tracking=True,
        help="Name of the pay gap report"
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
        help="Department for this pay gap analysis"
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        tracking=True,
        help="Job position for this pay gap analysis"
    )
    
    # Pay Data
    male_count = fields.Integer(
        string='Male Count',
        default=0,
        tracking=True,
        help="Number of male employees in the analysis"
    )
    
    female_count = fields.Integer(
        string='Female Count',
        default=0,
        tracking=True,
        help="Number of female employees in the analysis"
    )
    
    other_count = fields.Integer(
        string='Other Count',
        default=0,
        tracking=True,
        help="Number of other employees in the analysis"
    )
    
    # Salary Data
    male_avg_salary = fields.Monetary(
        string='Male Average Salary',
        currency_field='currency_id',
        tracking=True,
        help="Average salary of male employees"
    )
    
    female_avg_salary = fields.Monetary(
        string='Female Average Salary',
        currency_field='currency_id',
        tracking=True,
        help="Average salary of female employees"
    )
    
    other_avg_salary = fields.Monetary(
        string='Other Average Salary',
        currency_field='currency_id',
        tracking=True,
        help="Average salary of other employees"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Pay Gap Calculations
    mean_pay_gap = fields.Float(
        string='Mean Pay Gap (%)',
        compute='_compute_pay_gaps',
        store=True,
        help="Mean pay gap between men and women"
    )
    
    median_pay_gap = fields.Float(
        string='Median Pay Gap (%)',
        compute='_compute_pay_gaps',
        store=True,
        help="Median pay gap between men and women"
    )
    
    # Leadership Pay Gap
    male_leaders_avg_salary = fields.Monetary(
        string='Male Leaders Average Salary',
        currency_field='currency_id',
        tracking=True,
        help="Average salary of male leaders"
    )
    
    female_leaders_avg_salary = fields.Monetary(
        string='Female Leaders Average Salary',
        currency_field='currency_id',
        tracking=True,
        help="Average salary of female leaders"
    )
    
    leadership_pay_gap = fields.Float(
        string='Leadership Pay Gap (%)',
        compute='_compute_leadership_pay_gap',
        store=True,
        help="Pay gap in leadership positions"
    )
    
    # Experience Level Analysis
    experience_level = fields.Selection([
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
        ('all', 'All Levels'),
    ], string='Experience Level', required=True, default='all')
    
    # Pay Gap Categories
    pay_gap_category = fields.Selection([
        ('low', 'Low (< 5%)'),
        ('moderate', 'Moderate (5-15%)'),
        ('high', 'High (15-25%)'),
        ('very_high', 'Very High (> 25%)'),
    ], string='Pay Gap Category', compute='_compute_pay_gap_category', store=True)
    
    # Compliance Fields
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('requires_action', 'Requires Action'),
        ('under_review', 'Under Review'),
    ], string='Compliance Status', default='under_review', tracking=True)
    
    action_required = fields.Text(
        string='Action Required',
        tracking=True,
        help="Actions required to address pay gap issues"
    )
    
    # Reporting Fields
    period_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period Type', required=True, default='yearly')
    
    notes = fields.Text(
        string='Notes',
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.depends('male_avg_salary', 'female_avg_salary')
    def _compute_pay_gaps(self):
        for record in self:
            if record.male_avg_salary > 0 and record.female_avg_salary > 0:
                # Mean pay gap calculation
                record.mean_pay_gap = ((record.male_avg_salary - record.female_avg_salary) / record.male_avg_salary) * 100
                # For median, we'll use the same calculation as a proxy
                record.median_pay_gap = record.mean_pay_gap
            else:
                record.mean_pay_gap = 0.0
                record.median_pay_gap = 0.0
    
    @api.depends('male_leaders_avg_salary', 'female_leaders_avg_salary')
    def _compute_leadership_pay_gap(self):
        for record in self:
            if record.male_leaders_avg_salary > 0 and record.female_leaders_avg_salary > 0:
                record.leadership_pay_gap = ((record.male_leaders_avg_salary - record.female_leaders_avg_salary) / record.male_leaders_avg_salary) * 100
            else:
                record.leadership_pay_gap = 0.0
    
    @api.depends('mean_pay_gap')
    def _compute_pay_gap_category(self):
        for record in self:
            if record.mean_pay_gap < 5:
                record.pay_gap_category = 'low'
            elif record.mean_pay_gap < 15:
                record.pay_gap_category = 'moderate'
            elif record.mean_pay_gap < 25:
                record.pay_gap_category = 'high'
            else:
                record.pay_gap_category = 'very_high'
    
    @api.constrains('male_count', 'female_count', 'other_count')
    def _check_counts(self):
        for record in self:
            if record.male_count < 0 or record.female_count < 0 or record.other_count < 0:
                raise ValidationError(_('Counts cannot be negative.'))
    
    @api.constrains('male_avg_salary', 'female_avg_salary', 'other_avg_salary')
    def _check_salaries(self):
        for record in self:
            if record.male_avg_salary < 0 or record.female_avg_salary < 0 or record.other_avg_salary < 0:
                raise ValidationError(_('Salaries cannot be negative.'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_validate(self):
        self.write({'state': 'validated'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_pay_gap_summary(self, date_from=None, date_to=None):
        """Get pay gap summary for reporting"""
        domain = [('state', '=', 'validated')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        reports = self.search(domain)
        
        if not reports:
            return {
                'avg_mean_pay_gap': 0,
                'avg_median_pay_gap': 0,
                'avg_leadership_pay_gap': 0,
                'total_reports': 0,
                'by_category': [],
            }
        
        return {
            'avg_mean_pay_gap': sum(reports.mapped('mean_pay_gap')) / len(reports),
            'avg_median_pay_gap': sum(reports.mapped('median_pay_gap')) / len(reports),
            'avg_leadership_pay_gap': sum(reports.mapped('leadership_pay_gap')) / len(reports),
            'total_reports': len(reports),
            'by_category': reports.read_group(
                domain, 
                ['pay_gap_category', 'mean_pay_gap:avg'], 
                ['pay_gap_category']
            ),
        }