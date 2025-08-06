from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGGenderParity(models.Model):
    _name = 'esg.gender.parity'
    _description = 'ESG Gender Parity'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Report Name',
        required=True,
        tracking=True,
        help="Name of the gender parity report"
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
        help="Department for this gender parity report"
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        tracking=True,
        help="Job position for this gender parity report"
    )
    
    # Gender Counts
    male_count = fields.Integer(
        string='Male Count',
        default=0,
        tracking=True,
        help="Number of male employees"
    )
    
    female_count = fields.Integer(
        string='Female Count',
        default=0,
        tracking=True,
        help="Number of female employees"
    )
    
    other_count = fields.Integer(
        string='Other Count',
        default=0,
        tracking=True,
        help="Number of employees identifying as other"
    )
    
    total_count = fields.Integer(
        string='Total Count',
        compute='_compute_total_count',
        store=True,
        help="Total number of employees"
    )
    
    # Gender Ratios
    male_ratio = fields.Float(
        string='Male Ratio (%)',
        compute='_compute_gender_ratios',
        store=True,
        help="Percentage of male employees"
    )
    
    female_ratio = fields.Float(
        string='Female Ratio (%)',
        compute='_compute_gender_ratios',
        store=True,
        help="Percentage of female employees"
    )
    
    other_ratio = fields.Float(
        string='Other Ratio (%)',
        compute='_compute_gender_ratios',
        store=True,
        help="Percentage of other employees"
    )
    
    # Leadership Metrics
    male_leaders = fields.Integer(
        string='Male Leaders',
        default=0,
        tracking=True,
        help="Number of male employees in leadership positions"
    )
    
    female_leaders = fields.Integer(
        string='Female Leaders',
        default=0,
        tracking=True,
        help="Number of female employees in leadership positions"
    )
    
    other_leaders = fields.Integer(
        string='Other Leaders',
        default=0,
        tracking=True,
        help="Number of other employees in leadership positions"
    )
    
    leadership_gender_ratio = fields.Float(
        string='Leadership Gender Ratio',
        compute='_compute_leadership_ratio',
        store=True,
        help="Ratio of female to male leaders"
    )
    
    # Diversity Metrics
    diversity_score = fields.Float(
        string='Diversity Score',
        compute='_compute_diversity_score',
        store=True,
        help="Overall diversity score (0-100)"
    )
    
    # Reporting Fields
    period_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period Type', required=True, default='monthly')
    
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
    
    @api.depends('male_count', 'female_count', 'other_count')
    def _compute_total_count(self):
        for record in self:
            record.total_count = record.male_count + record.female_count + record.other_count
    
    @api.depends('male_count', 'female_count', 'other_count', 'total_count')
    def _compute_gender_ratios(self):
        for record in self:
            if record.total_count > 0:
                record.male_ratio = (record.male_count / record.total_count) * 100
                record.female_ratio = (record.female_count / record.total_count) * 100
                record.other_ratio = (record.other_count / record.total_count) * 100
            else:
                record.male_ratio = 0.0
                record.female_ratio = 0.0
                record.other_ratio = 0.0
    
    @api.depends('male_leaders', 'female_leaders')
    def _compute_leadership_ratio(self):
        for record in self:
            if record.male_leaders > 0:
                record.leadership_gender_ratio = record.female_leaders / record.male_leaders
            else:
                record.leadership_gender_ratio = 0.0
    
    @api.depends('male_ratio', 'female_ratio', 'other_ratio', 'leadership_gender_ratio')
    def _compute_diversity_score(self):
        for record in self:
            # Calculate diversity score based on gender balance and leadership representation
            gender_balance = min(record.male_ratio, record.female_ratio) * 2  # Max 100 if 50/50
            leadership_score = min(record.leadership_gender_ratio, 1.0) * 50  # Max 50 if 1:1 ratio
            
            record.diversity_score = min(gender_balance + leadership_score, 100.0)
    
    @api.constrains('male_count', 'female_count', 'other_count')
    def _check_counts(self):
        for record in self:
            if record.male_count < 0 or record.female_count < 0 or record.other_count < 0:
                raise ValidationError(_('Counts cannot be negative.'))
    
    @api.constrains('male_leaders', 'female_leaders', 'other_leaders')
    def _check_leader_counts(self):
        for record in self:
            if record.male_leaders < 0 or record.female_leaders < 0 or record.other_leaders < 0:
                raise ValidationError(_('Leader counts cannot be negative.'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_validate(self):
        self.write({'state': 'validated'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_gender_parity_summary(self, date_from=None, date_to=None):
        """Get gender parity summary for reporting"""
        domain = [('state', '=', 'validated')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        reports = self.search(domain)
        
        if not reports:
            return {
                'total_male': 0,
                'total_female': 0,
                'total_other': 0,
                'avg_diversity_score': 0,
                'avg_leadership_ratio': 0,
                'count': 0,
            }
        
        return {
            'total_male': sum(reports.mapped('male_count')),
            'total_female': sum(reports.mapped('female_count')),
            'total_other': sum(reports.mapped('other_count')),
            'avg_diversity_score': sum(reports.mapped('diversity_score')) / len(reports),
            'avg_leadership_ratio': sum(reports.mapped('leadership_gender_ratio')) / len(reports),
            'count': len(reports),
        }
    
    @api.model
    def auto_collect_social_data(self):
        """Automatically collect social data from HR module"""
        _logger.info("Starting automatic social data collection")
        
        collected_data = {
            'gender_parity': {},
            'employee_diversity': {},
            'leadership_diversity': {},
            'records_created': 0
        }
        
        try:
            # 1. Collect Gender Parity Data
            gender_data = self._collect_gender_parity_data()
            collected_data['gender_parity'] = gender_data
            
            # 2. Collect Employee Diversity Data
            diversity_data = self._collect_employee_diversity_data()
            collected_data['employee_diversity'] = diversity_data
            
            # 3. Collect Leadership Diversity Data
            leadership_data = self._collect_leadership_diversity_data()
            collected_data['leadership_diversity'] = leadership_data
            
            _logger.info(f"Social data collection completed: {collected_data}")
            return collected_data
            
        except Exception as e:
            _logger.error(f"Error in automatic social data collection: {e}")
            return collected_data
    
    def _collect_gender_parity_data(self):
        """Collect gender parity data from HR employees"""
        hr_employee = self.env.get('hr.employee')
        
        if not hr_employee:
            return {}
        
        # Get all active employees
        employees = hr_employee.search([
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ])
        
        # Count by gender
        male_count = 0
        female_count = 0
        other_count = 0
        
        for employee in employees:
            gender = getattr(employee, 'gender', 'male')
            if gender == 'male':
                male_count += 1
            elif gender == 'female':
                female_count += 1
            else:
                other_count += 1
        
        # Create gender parity record
        gender_parity_record = self.create({
            'name': f'Gender Parity Report - {fields.Date.today().strftime("%B %Y")}',
            'date': fields.Date.today(),
            'male_count': male_count,
            'female_count': female_count,
            'other_count': other_count,
            'period_type': 'monthly',
            'state': 'draft',
            'notes': 'Automatically collected from HR employee data'
        })
        
        return {
            'male_count': male_count,
            'female_count': female_count,
            'other_count': other_count,
            'total_count': male_count + female_count + other_count,
            'record_id': gender_parity_record.id
        }
    
    def _collect_employee_diversity_data(self):
        """Collect employee diversity data"""
        hr_employee = self.env.get('hr.employee')
        
        if not hr_employee:
            return {}
        
        # Get employees by department
        departments = self.env['hr.department'].search([
            ('company_id', '=', self.env.company.id)
        ])
        
        diversity_data = {}
        
        for dept in departments:
            employees = hr_employee.search([
                ('department_id', '=', dept.id),
                ('active', '=', True)
            ])
            
            if employees:
                male_count = len(employees.filtered(lambda e: getattr(e, 'gender', 'male') == 'male'))
                female_count = len(employees.filtered(lambda e: getattr(e, 'gender', 'female') == 'female'))
                other_count = len(employees) - male_count - female_count
                
                diversity_data[dept.name] = {
                    'total': len(employees),
                    'male': male_count,
                    'female': female_count,
                    'other': other_count,
                    'diversity_ratio': (min(male_count, female_count) / len(employees)) * 100 if len(employees) > 0 else 0
                }
        
        return diversity_data
    
    def _collect_leadership_diversity_data(self):
        """Collect leadership diversity data"""
        hr_employee = self.env.get('hr.employee')
        
        if not hr_employee:
            return {}
        
        # Define leadership job titles (this would be configurable)
        leadership_titles = [
            'manager', 'director', 'executive', 'chief', 'president', 'ceo', 'cfo', 'cto',
            'vp', 'vice president', 'head of', 'lead', 'senior'
        ]
        
        # Get employees in leadership positions
        leadership_employees = hr_employee.search([
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ])
        
        # Filter for leadership positions
        leaders = leadership_employees.filtered(lambda e: 
            any(title in (e.job_title or '').lower() for title in leadership_titles) or
            any(title in (e.job_id.name or '').lower() for title in leadership_titles)
        )
        
        male_leaders = len(leaders.filtered(lambda e: getattr(e, 'gender', 'male') == 'male'))
        female_leaders = len(leaders.filtered(lambda e: getattr(e, 'gender', 'female') == 'female'))
        other_leaders = len(leaders) - male_leaders - female_leaders
        
        # Update the gender parity record with leadership data
        latest_record = self.search([], order='date desc', limit=1)
        if latest_record:
            latest_record.write({
                'male_leaders': male_leaders,
                'female_leaders': female_leaders,
                'other_leaders': other_leaders
            })
        
        return {
            'total_leaders': len(leaders),
            'male_leaders': male_leaders,
            'female_leaders': female_leaders,
            'other_leaders': other_leaders,
            'leadership_ratio': (female_leaders / len(leaders)) * 100 if len(leaders) > 0 else 0
        }