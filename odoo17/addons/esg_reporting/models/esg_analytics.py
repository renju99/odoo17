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
    
    notes = fields.Text(
        string='Notes',
        tracking=True,
        help="Additional notes about the analytics report"
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
    
    @api.model
    def get_comprehensive_dashboard_data(self, period='current_year', category='all'):
        """Get comprehensive dashboard data for advanced dashboard"""
        _logger.info(f"Getting comprehensive dashboard data for period: {period}, category: {category}")
        
        # Calculate date range based on period
        today = fields.Date.today()
        if period == 'current_month':
            date_from = today.replace(day=1)
            date_to = today
        elif period == 'current_quarter':
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            date_from = today.replace(month=quarter_start_month, day=1)
            date_to = today
        else:  # current_year
            date_from = today.replace(month=1, day=1)
            date_to = today
        
        # Get ESG scores trend
        esg_scores = self._get_esg_scores_trend(date_from, date_to)
        
        # Get emissions data
        emissions = self._get_emissions_breakdown(date_from, date_to)
        
        # Get diversity data
        diversity = self._get_diversity_data(date_from, date_to)
        
        # Get risk assessment
        risk_assessment = self._get_risk_assessment(date_from, date_to)
        
        # Get targets data
        targets = self._get_targets_data(date_from, date_to)
        
        # Calculate overall metrics
        overall_score = self._calculate_overall_esg_score(esg_scores)
        carbon_reduction = self._calculate_carbon_reduction(emissions)
        diversity_score = self._calculate_diversity_score(diversity)
        target_progress = self._calculate_target_progress(targets)
        
        return {
            'esg_scores': esg_scores,
            'emissions': emissions,
            'diversity': diversity,
            'risk_assessment': risk_assessment,
            'targets': targets,
            'overall_score': overall_score,
            'carbon_reduction': carbon_reduction,
            'diversity_score': diversity_score,
            'target_progress': target_progress,
            'period': period,
            'category': category
        }
    
    def _get_esg_scores_trend(self, date_from, date_to):
        """Get ESG scores trend over time"""
        analytics = self.search([
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'completed')
        ], order='date')
        
        trend_data = []
        for record in analytics:
            trend_data.append({
                'month': record.date.strftime('%B %Y'),
                'environmental': record.environmental_score,
                'social': record.social_score,
                'governance': record.governance_score,
                'overall': record.overall_score
            })
        
        return trend_data
    
    def _get_emissions_breakdown(self, date_from, date_to):
        """Get emissions breakdown by scope"""
        emissions = self.env['esg.emission'].search([
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'validated')
        ])
        
        # Group by emission factor category
        scope1 = sum(emissions.filtered(lambda e: e.emission_factor_id.category == 'transportation').mapped('emission_amount'))
        scope2 = sum(emissions.filtered(lambda e: e.emission_factor_id.category == 'electricity').mapped('emission_amount'))
        scope3 = sum(emissions.filtered(lambda e: e.emission_factor_id.category in ['waste', 'water', 'other']).mapped('emission_amount'))
        
        # Get offset data
        offsets = self.env['esg.offset'].search([
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'validated')
        ])
        offset_amount = sum(offsets.mapped('offset_amount'))
        
        return {
            'scope1': scope1,
            'scope2': scope2,
            'scope3': scope3,
            'offset': offset_amount,
            'total': scope1 + scope2 + scope3 - offset_amount
        }
    
    def _get_diversity_data(self, date_from, date_to):
        """Get diversity data"""
        gender_parity = self.env['esg.gender.parity'].search([
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'validated')
        ], order='date desc', limit=1)
        
        if gender_parity:
            return {
                'male_count': gender_parity.male_count,
                'female_count': gender_parity.female_count,
                'other_count': gender_parity.other_count,
                'male_leaders': gender_parity.male_leaders,
                'female_leaders': gender_parity.female_leaders,
                'other_leaders': gender_parity.other_leaders,
                'diversity_score': gender_parity.diversity_score
            }
        
        return {
            'male_count': 0,
            'female_count': 0,
            'other_count': 0,
            'male_leaders': 0,
            'female_leaders': 0,
            'other_leaders': 0,
            'diversity_score': 0
        }
    
    def _get_risk_assessment(self, date_from, date_to):
        """Get risk assessment data"""
        # This would integrate with risk assessment models
        # For now, return placeholder data
        return {
            'environmental_high': 2,
            'environmental_medium': 5,
            'environmental_low': 8,
            'social_high': 1,
            'social_medium': 3,
            'social_low': 6,
            'governance_high': 0,
            'governance_medium': 2,
            'governance_low': 4
        }
    
    def _get_targets_data(self, date_from, date_to):
        """Get targets progress data"""
        targets = self.env['esg.target'].search([
            ('state', 'in', ['active', 'achieved'])
        ])
        
        targets_data = []
        for target in targets:
            targets_data.append({
                'name': target.name,
                'progress_percentage': target.progress_percentage,
                'category': target.category,
                'is_on_track': target.is_on_track
            })
        
        return targets_data
    
    def _calculate_overall_esg_score(self, esg_scores):
        """Calculate overall ESG score"""
        if not esg_scores:
            return 0
        
        latest_scores = esg_scores[-1]
        return latest_scores.get('overall', 0)
    
    def _calculate_carbon_reduction(self, emissions):
        """Calculate carbon reduction percentage"""
        if not emissions or emissions['total'] == 0:
            return 0
        
        # This would compare with baseline year
        # For now, return a placeholder
        return 15.5
    
    def _calculate_diversity_score(self, diversity):
        """Calculate diversity score"""
        return diversity.get('diversity_score', 0)
    
    def _calculate_target_progress(self, targets):
        """Calculate average target progress"""
        if not targets:
            return 0
        
        total_progress = sum(target['progress_percentage'] for target in targets)
        return total_progress / len(targets)
    
    @api.model
    def get_predictive_analytics(self):
        """Get predictive analytics insights"""
        # This would integrate with ML models
        # For now, return placeholder insights
        return {
            'insights': [
                {
                    'title': 'Carbon Reduction Trend',
                    'description': 'Based on current trends, you are likely to achieve 85% of your carbon reduction target by year-end.',
                    'icon': 'trending-up',
                    'confidence': 85
                },
                {
                    'title': 'Diversity Improvement',
                    'description': 'Leadership diversity is expected to improve by 12% in the next quarter.',
                    'icon': 'users',
                    'confidence': 78
                },
                {
                    'title': 'Risk Alert',
                    'description': 'Supply chain ESG risks are increasing. Consider reviewing supplier assessments.',
                    'icon': 'exclamation-triangle',
                    'confidence': 92
                }
            ]
        }
    
    @api.model
    def get_esg_alerts(self):
        """Get ESG alerts and notifications"""
        alerts = []
        
        # Check for targets at risk
        at_risk_targets = self.env['esg.target'].search([
            ('state', '=', 'active'),
            ('is_on_track', '=', False)
        ])
        
        for target in at_risk_targets:
            alerts.append({
                'title': f'Target at Risk: {target.name}',
                'message': f'Target is {target.progress_percentage:.1f}% complete but expected {target.progress_percentage + 10:.1f}%',
                'level': 'warning',
                'date': fields.Date.today().strftime('%Y-%m-%d')
            })
        
        # Check for compliance deadlines
        frameworks = self.env['esg.framework'].search([
            ('next_assessment_date', '<=', fields.Date.today() + timedelta(days=30))
        ])
        
        for framework in frameworks:
            alerts.append({
                'title': f'Compliance Deadline: {framework.name}',
                'message': f'Assessment due on {framework.next_assessment_date}',
                'level': 'info',
                'date': fields.Date.today().strftime('%Y-%m-%d')
            })
        
        return alerts
    
    @api.model
    def generate_comprehensive_report(self, period='current_year', category='all'):
        """Generate comprehensive ESG report"""
        # This would generate a comprehensive report
        # For now, return placeholder data
        return {
            'report_url': '/esg/report/generate',
            'status': 'success',
            'message': 'Report generation started'
        }
    
    @api.model
    def export_dashboard_data(self, period='current_year', category='all'):
        """Export dashboard data for external analysis"""
        data = self.get_comprehensive_dashboard_data(period, category)
        
        # Convert to exportable format
        export_data = []
        
        # Add ESG scores
        for score in data['esg_scores']:
            export_data.append({
                'date': score['month'],
                'environmental_score': score['environmental'],
                'social_score': score['social'],
                'governance_score': score['governance'],
                'overall_score': score['overall']
            })
        
        return export_data


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
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
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
    
    def action_confirm(self):
        """Confirm the carbon footprint record"""
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'
        return True
    
    def action_validate(self):
        """Validate the carbon footprint record"""
        for record in self:
            if record.state == 'confirmed':
                record.state = 'validated'
        return True
    
    def action_cancel(self):
        """Cancel the carbon footprint record"""
        for record in self:
            if record.state in ['draft', 'confirmed']:
                record.state = 'cancelled'
        return True
    
    def action_draft(self):
        """Reset the carbon footprint record to draft"""
        for record in self:
            if record.state == 'cancelled':
                record.state = 'draft'
        return True