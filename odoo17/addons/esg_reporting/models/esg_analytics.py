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
