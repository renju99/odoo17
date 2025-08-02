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