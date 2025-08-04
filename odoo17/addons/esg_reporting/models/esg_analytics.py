from odoo import models, fields, api
from datetime import datetime, timedelta
import json
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ESGAnalytics(models.Model):
    _name = 'esg.analytics'
    _description = 'ESG Analytics'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Analytics Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Analytics Configuration
    analytics_type = fields.Selection([
        ('performance', 'Performance Analytics'),
        ('risk', 'Risk Analytics'),
        ('trend', 'Trend Analytics'),
        ('predictive', 'Predictive Analytics'),
        ('benchmark', 'Benchmark Analytics'),
        ('correlation', 'Correlation Analytics')
    ], string='Analytics Type', required=True, default='performance')

    # Date Range
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    
    # Single date field for view compatibility
    date = fields.Date(string='Date', compute='_compute_date', store=True)

    # Analytics Parameters
    include_environmental = fields.Boolean(string='Include Environmental', default=True)
    include_social = fields.Boolean(string='Include Social', default=True)
    include_governance = fields.Boolean(string='Include Governance', default=True)

    # Advanced Analytics Options
    include_correlation_analysis = fields.Boolean(string='Include Correlation Analysis', default=False)
    include_anomaly_detection = fields.Boolean(string='Include Anomaly Detection', default=False)
    include_predictive_modeling = fields.Boolean(string='Include Predictive Modeling', default=False)
    include_risk_scoring = fields.Boolean(string='Include Risk Scoring', default=False)

    # Results
    analytics_results = fields.Text(string='Analytics Results (JSON)', compute='_compute_analytics_results')
    
    # ESG Metrics for Dashboard
    total_emissions = fields.Float(string='Total Emissions (t CO2)', compute='_compute_esg_metrics', store=True)
    total_offset = fields.Float(string='Total Offset (t CO2)', compute='_compute_esg_metrics', store=True)
    net_emissions = fields.Float(string='Net Emissions (t CO2)', compute='_compute_esg_metrics', store=True)
    overall_score = fields.Float(string='Overall ESG Score', compute='_compute_esg_metrics', store=True)
    
    # State field for workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='draft', tracking=True)

    @api.depends('date_from')
    def _compute_date(self):
        """Compute the date field from date_from for view compatibility"""
        for record in self:
            record.date = record.date_from

    @api.depends('analytics_results', 'state')
    def _compute_esg_metrics(self):
        """Compute ESG metrics from analytics results"""
        for record in self:
            if record.state == 'completed' and record.analytics_results:
                try:
                    results = json.loads(record.analytics_results)
                    record.total_emissions = results.get('total_emissions', 0.0)
                    record.total_offset = results.get('total_offset', 0.0)
                    record.net_emissions = results.get('net_emissions', 0.0)
                    record.overall_score = results.get('overall_score', 0.0)
                except (json.JSONDecodeError, TypeError):
                    record.total_emissions = 0.0
                    record.total_offset = 0.0
                    record.net_emissions = 0.0
                    record.overall_score = 0.0
            else:
                record.total_emissions = 0.0
                record.total_offset = 0.0
                record.net_emissions = 0.0
                record.overall_score = 0.0

    @api.depends('analytics_type', 'date_from', 'date_to', 'include_environmental', 
                 'include_social', 'include_governance', 'include_correlation_analysis',
                 'include_anomaly_detection', 'include_predictive_modeling', 'include_risk_scoring')
    def _compute_analytics_results(self):
        """Compute analytics results based on configuration"""
        for record in self:
            if record.state == 'completed':
                # This would contain the actual analytics computation logic
                # For now, we'll create a basic structure
                results = {
                    'total_emissions': 0.0,
                    'total_offset': 0.0,
                    'net_emissions': 0.0,
                    'overall_score': 0.0,
                    'analytics_type': record.analytics_type,
                    'date_range': {
                        'from': record.date_from.isoformat() if record.date_from else None,
                        'to': record.date_to.isoformat() if record.date_to else None
                    }
                }
                record.analytics_results = json.dumps(results)
            else:
                record.analytics_results = ''

    @api.model
    def create(self, vals):
        """Override create to set initial state"""
        vals['state'] = 'draft'
        return super().create(vals)

    def action_process(self):
        """Process the analytics"""
        self.ensure_one()
        self.state = 'processing'
        # Here you would implement the actual analytics processing
        # For now, we'll simulate completion
        self.state = 'completed'
        self._compute_analytics_results()
        self._compute_esg_metrics()

    def action_reset(self):
        """Reset to draft state"""
        self.ensure_one()
        self.state = 'draft'
        self.analytics_results = ''

    def action_draft(self):
        """Reset to draft state"""
        self.write({'state': 'draft'})

    @api.model
    def get_comprehensive_dashboard_data(self, company_id=None, **kwargs):
        """
        Gathers and formats a comprehensive set of data for the advanced ESG dashboard.
        """
        # If no company_id is provided, use the current user's company
        if not company_id:
            company_id = self.env.company.id

        # Helper function to generate dummy chart data
        def get_chart_data(labels, datasets_config):
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': config['label'],
                        'data': [self.env['ir.qweb.field.float'].value_to_html(d, {}) for d in config['data']],
                        'backgroundColor': config.get('backgroundColor', '#875A7B'),
                        'borderColor': config.get('borderColor', '#875A7B'),
                        'fill': config.get('fill', False),
                    } for config in datasets_config
                ]
            }

        # --- KPIs ---
        kpis = [
            {'name': 'Overall ESG Score', 'value': '82', 'unit': '/100', 'icon': 'fa-star'},
            {'name': 'Net Emissions', 'value': '1,250', 'unit': 'tCO2e', 'icon': 'fa-leaf'},
            {'name': 'Gender Pay Gap', 'value': '12%', 'unit': '', 'icon': 'fa-percent'},
            {'name': 'Community Investment', 'value': '$50k', 'unit': '', 'icon': 'fa-users'},
        ]

        # --- Chart Data ---
        # 1. Emissions Trend (Line Chart)
        emissions_trend_chart = get_chart_data(
            labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets_config=[
                {'label': 'Scope 1 Emissions', 'data': [120, 150, 130, 180, 200, 220], 'backgroundColor': 'rgba(255, 99, 132, 0.2)', 'borderColor': 'rgba(255, 99, 132, 1)'},
                {'label': 'Scope 2 Emissions', 'data': [80, 90, 85, 100, 110, 105], 'backgroundColor': 'rgba(54, 162, 235, 0.2)', 'borderColor': 'rgba(54, 162, 235, 1)'},
            ]
        )

        # 2. Gender Diversity (Doughnut Chart)
        gender_diversity_chart = get_chart_data(
            labels=['Female', 'Male', 'Non-Binary'],
            datasets_config=[
                {'label': 'Workforce Diversity', 'data': [45, 53, 2], 'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56']},
            ]
        )
        
        # 3. Governance Compliance (Bar chart)
        governance_compliance_chart = get_chart_data(
            labels=['Policy A', 'Policy B', 'Standard C', 'Regulation D'],
             datasets_config=[
                {'label': 'Compliance Status (%)', 'data': [95, 88, 100, 92], 'backgroundColor': ['#4BC0C0', '#FF9F40', '#9966FF', '#FFCD56']},
            ]
        )

        # --- Tabular Data ---
        initiatives_data = [
            {'name': 'Solar Panel Installation', 'category': 'Environmental', 'status': 'Completed', 'impact_score': 8},
            {'name': 'Diversity & Inclusion Training', 'category': 'Social', 'status': 'In Progress', 'impact_score': 7},
            {'name': 'Ethical Supply Chain Audit', 'category': 'Governance', 'status': 'Planned', 'impact_score': 9},
            {'name': 'Community Volunteering Program', 'category': 'Social', 'status': 'Completed', 'impact_score': 6},
        ]

        return {
            'kpis': kpis,
            'charts': {
                'emissions_trend': emissions_trend_chart,
                'gender_diversity': gender_diversity_chart,
                'governance_compliance': governance_compliance_chart,
            },
            'tables': {
                'initiatives': initiatives_data,
            },
            'company_name': self.env['res.company'].browse(company_id).name,
        }
    def get_comprehensive_dashboard_data(self, period=None, category=None):
        """Get comprehensive dashboard data for the frontend"""
        try:
            # Set default values if None
            if period is None:
                period = 'current_year'
            if category is None:
                category = 'all'
            
            # Calculate date range based on period
            today = fields.Date.today()
            if period == 'current_year':
                date_from = today.replace(month=1, day=1)
                date_to = today
            elif period == 'last_year':
                date_from = today.replace(year=today.year-1, month=1, day=1)
                date_to = today.replace(year=today.year-1, month=12, day=31)
            elif period == 'last_quarter':
                # Calculate last quarter
                current_quarter = (today.month - 1) // 3
                if current_quarter == 0:
                    date_from = today.replace(year=today.year-1, month=10, day=1)
                    date_to = today.replace(year=today.year-1, month=12, day=31)
                else:
                    start_month = (current_quarter - 1) * 3 + 1
                    date_from = today.replace(month=start_month, day=1)
                    date_to = today.replace(month=start_month+2, day=28)
            else:
                date_from = today - timedelta(days=30)
                date_to = today

            # Get ESG data based on category
            data = {
                'period': period,
                'category': category,
                'date_range': {
                    'from': date_from.isoformat(),
                    'to': date_to.isoformat()
                },
                'overall_score': 0,
                'carbon_reduction': 0,
                'diversity_score': 0,
                'target_progress': 0
            }

            if category in ['all', 'environmental']:
                data['emissions'] = self._get_emission_data(date_from, date_to)
                data['environmental_score'] = self._calculate_environmental_score(date_from, date_to)

            if category in ['all', 'social']:
                data['diversity'] = self._get_diversity_data(date_from, date_to)
                data['social_score'] = self._calculate_social_score(date_from, date_to)

            if category in ['all', 'governance']:
                data['governance_score'] = self._calculate_governance_score(date_from, date_to)

            if category in ['all', 'risk']:
                data['risk_assessment'] = self._get_risk_assessment_data(date_from, date_to)

            if category in ['all', 'targets']:
                data['targets'] = self._get_target_progress_data(date_from, date_to)

            # Calculate overall ESG score
            data['overall_score'] = self._calculate_overall_esg_score(data)

            # Add trend data
            data['esg_scores'] = self._get_esg_trend_data(date_from, date_to)

            # Calculate additional metrics
            data['carbon_reduction'] = self._calculate_carbon_reduction(data)
            data['diversity_score'] = self._calculate_diversity_score(data)
            data['target_progress'] = self._calculate_target_progress(data)

            return data

        except Exception as e:
            # Return default data structure in case of error
            return {
                'period': period or 'current_year',
                'category': category or 'all',
                'date_range': {
                    'from': fields.Date.today().isoformat(),
                    'to': fields.Date.today().isoformat()
                },
                'overall_score': 0,
                'carbon_reduction': 0,
                'diversity_score': 0,
                'target_progress': 0,
                'emissions': {'scope1': 0, 'scope2': 0, 'scope3': 0, 'offset': 0},
                'diversity': {'male_count': 0, 'female_count': 0, 'other_count': 0},
                'risk_assessment': {},
                'targets': [],
                'esg_scores': []
            }

    @api.model
    def get_predictive_analytics(self):
        """Get predictive analytics data"""
        try:
            # Mock predictive data - in real implementation, this would use ML models
            return {
                'insights': [
                    {
                        'title': 'Emission Reduction Trend',
                        'description': 'Emissions are expected to decrease by 15% in the next quarter',
                        'icon': 'trending-down',
                        'confidence': 85
                    },
                    {
                        'title': 'Diversity Improvement',
                        'description': 'Workforce diversity is improving steadily',
                        'icon': 'users',
                        'confidence': 92
                    },
                    {
                        'title': 'Risk Assessment',
                        'description': 'Environmental risks remain moderate',
                        'icon': 'shield-alt',
                        'confidence': 78
                    }
                ],
                'emission_forecast': {
                    'next_month': 1250.5,
                    'next_quarter': 3800.2,
                    'next_year': 14500.8
                },
                'risk_predictions': {
                    'environmental_risk': 'medium',
                    'social_risk': 'low',
                    'governance_risk': 'low'
                },
                'target_achievement_probability': {
                    'emission_reduction': 0.85,
                    'diversity_improvement': 0.92,
                    'governance_compliance': 0.78
                }
            }
        except Exception as e:
            return {
                'insights': [],
                'emission_forecast': {},
                'risk_predictions': {},
                'target_achievement_probability': {}
            }

    @api.model
    def get_esg_alerts(self):
        """Get ESG alerts and notifications"""
        try:
            alerts = []
            
            # Check for emission threshold alerts
            emissions = self._get_emission_data(fields.Date.today() - timedelta(days=30), fields.Date.today())
            if emissions.get('total', 0) > 1000:
                alerts.append({
                    'level': 'warning',
                    'title': 'High Emissions Alert',
                    'message': 'Emissions have exceeded the monthly threshold',
                    'date': fields.Date.today().isoformat()
                })

            # Check for diversity alerts
            diversity = self._get_diversity_data(fields.Date.today() - timedelta(days=30), fields.Date.today())
            if diversity.get('female_percentage', 0) < 30:
                alerts.append({
                    'level': 'info',
                    'title': 'Diversity Improvement Needed',
                    'message': 'Female representation is below target',
                    'date': fields.Date.today().isoformat()
                })

            return alerts
        except Exception as e:
            return []

    @api.model
    def generate_comprehensive_report(self, period=None, category=None):
        """Generate comprehensive ESG report"""
        try:
            # Set default values if None
            if period is None:
                period = 'current_year'
            if category is None:
                category = 'all'
            
            # This would generate a PDF report
            # For now, return mock data
            return {
                'report_url': '/esg/report/download',
                'report_id': 1,  # Use a default ID since this is a class method
                'generated_at': fields.Datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'report_url': None,
                'report_id': None,
                'generated_at': fields.Datetime.now().isoformat()
            }

    @api.model
    def export_dashboard_data(self, period=None, category=None):
        """Export dashboard data as CSV"""
        try:
            # Set default values if None
            if period is None:
                period = 'current_year'
            if category is None:
                category = 'all'
            
            dashboard_data = self.get_comprehensive_dashboard_data(period, category)
            
            # Convert to CSV format
            csv_data = []
            
            # Add ESG scores
            for score_data in dashboard_data.get('esg_scores', []):
                csv_data.append({
                    'Date': score_data.get('month'),
                    'Environmental_Score': score_data.get('environmental'),
                    'Social_Score': score_data.get('social'),
                    'Governance_Score': score_data.get('governance'),
                    'Overall_Score': score_data.get('overall')
                })
            
            return csv_data
        except Exception as e:
            return []

    @api.model
    def _get_emission_data(self, date_from, date_to):
        """Get emission data for the specified date range"""
        try:
            # Mock data - in real implementation, this would query actual emission records
            return {
                'scope1': 450.5,
                'scope2': 320.8,
                'scope3': 180.2,
                'offset': 150.0,
                'total': 950.5,
                'net': 800.5
            }
        except Exception as e:
            return {
                'scope1': 0,
                'scope2': 0,
                'scope3': 0,
                'offset': 0,
                'total': 0,
                'net': 0
            }

    @api.model
    def _get_diversity_data(self, date_from, date_to):
        """Get diversity data for the specified date range"""
        try:
            # Mock data - in real implementation, this would query actual employee records
            return {
                'male_count': 120,
                'female_count': 85,
                'other_count': 5,
                'male_leaders': 15,
                'female_leaders': 8,
                'other_leaders': 1,
                'female_percentage': 40.5,
                'leadership_diversity': 42.1
            }
        except Exception as e:
            return {
                'male_count': 0,
                'female_count': 0,
                'other_count': 0,
                'male_leaders': 0,
                'female_leaders': 0,
                'other_leaders': 0,
                'female_percentage': 0,
                'leadership_diversity': 0
            }

    @api.model
    def _get_risk_assessment_data(self, date_from, date_to):
        """Get risk assessment data"""
        try:
            # Mock data - in real implementation, this would calculate actual risk scores
            return {
                'environmental_high': 2,
                'environmental_medium': 5,
                'environmental_low': 8,
                'social_high': 1,
                'social_medium': 3,
                'social_low': 10,
                'governance_high': 0,
                'governance_medium': 2,
                'governance_low': 12
            }
        except Exception as e:
            return {
                'environmental_high': 0,
                'environmental_medium': 0,
                'environmental_low': 0,
                'social_high': 0,
                'social_medium': 0,
                'social_low': 0,
                'governance_high': 0,
                'governance_medium': 0,
                'governance_low': 0
            }

    @api.model
    def _get_target_progress_data(self, date_from, date_to):
        """Get target progress data"""
        try:
            # Mock data - in real implementation, this would query actual target records
            return [
                {
                    'name': 'Emission Reduction',
                    'target': 20,
                    'current': 15,
                    'progress_percentage': 75
                },
                {
                    'name': 'Diversity Improvement',
                    'target': 50,
                    'current': 40.5,
                    'progress_percentage': 81
                },
                {
                    'name': 'Governance Compliance',
                    'target': 100,
                    'current': 95,
                    'progress_percentage': 95
                }
            ]
        except Exception as e:
            return []

    @api.model
    def _get_esg_trend_data(self, date_from, date_to):
        """Get ESG trend data for charts"""
        try:
            # Mock monthly data for the last 12 months
            trend_data = []
            for i in range(12):
                month_date = date_from - timedelta(days=30*i)
                trend_data.append({
                    'month': month_date.strftime('%Y-%m'),
                    'environmental': 75 + (i * 2),
                    'social': 80 + (i * 1.5),
                    'governance': 85 + (i * 1),
                    'overall': 80 + (i * 1.5)
                })
            return trend_data
        except Exception as e:
            return []

    @api.model
    def _calculate_environmental_score(self, date_from, date_to):
        """Calculate environmental score"""
        try:
            # Mock calculation - in real implementation, this would use actual metrics
            return 78.5
        except Exception as e:
            return 0

    @api.model
    def _calculate_social_score(self, date_from, date_to):
        """Calculate social score"""
        try:
            # Mock calculation - in real implementation, this would use actual metrics
            return 82.3
        except Exception as e:
            return 0

    @api.model
    def _calculate_governance_score(self, date_from, date_to):
        """Calculate governance score"""
        try:
            # Mock calculation - in real implementation, this would use actual metrics
            return 88.7
        except Exception as e:
            return 0

    @api.model
    def _calculate_overall_esg_score(self, data):
        """Calculate overall ESG score"""
<<<<<<< HEAD
        environmental = data.get('environmental_score', 0)
        social = data.get('social_score', 0)
        governance = data.get('governance_score', 0)
        
        # Weighted average
        return (environmental * 0.4 + social * 0.3 + governance * 0.3)
=======
        try:
            environmental = data.get('environmental_score', 0)
            social = data.get('social_score', 0)
            governance = data.get('governance_score', 0)
            
            # Weighted average
            return (environmental * 0.4 + social * 0.3 + governance * 0.3)
        except Exception as e:
            return 0

    @api.model
    def _calculate_carbon_reduction(self, data):
        """Calculate carbon reduction percentage"""
        try:
            emissions = data.get('emissions', {})
            if emissions.get('total', 0) > 0:
                return ((emissions.get('offset', 0) / emissions.get('total', 1)) * 100)
            return 0
        except Exception as e:
            return 0

    @api.model
    def _calculate_diversity_score(self, data):
        """Calculate diversity score"""
        try:
            diversity = data.get('diversity', {})
            if diversity.get('female_percentage', 0) > 0:
                return diversity.get('female_percentage', 0)
            return 0
        except Exception as e:
            return 0

    @api.model
    def _calculate_target_progress(self, data):
        """Calculate overall target progress"""
        try:
            targets = data.get('targets', [])
            if targets:
                total_progress = sum(target.get('progress_percentage', 0) for target in targets)
                return total_progress / len(targets)
            return 0
        except Exception as e:
            return 0
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
