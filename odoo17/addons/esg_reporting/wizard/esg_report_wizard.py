# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class EnhancedESGWizard(models.TransientModel):
    _name = 'enhanced.esg.wizard'
    _description = 'Enhanced ESG Report Wizard'

    # Basic report configuration
    report_name = fields.Char(string='Report Name', required=True, default='Enhanced ESG Report')
    report_type = fields.Selection([
        ('comprehensive', 'Comprehensive'),
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
        ('custom', 'Custom')
    ], string='Report Type', default='comprehensive', required=True)
    company_name = fields.Char(string='Company Name', default=lambda self: self.env.company.name)
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
        ('csv', 'CSV')
    ], string='Output Format', default='pdf', required=True)
    
    # Date and granularity
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    granularity = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Granularity', default='monthly', required=True)
    report_theme = fields.Selection([
        ('default', 'Default'),
        ('corporate', 'Corporate'),
        ('modern', 'Modern'),
        ('classic', 'Classic')
    ], string='Report Theme', default='default')
    
    # Asset filtering
    asset_type = fields.Selection([
        ('all', 'All Assets'),
        ('buildings', 'Buildings'),
        ('equipment', 'Equipment'),
        ('vehicles', 'Vehicles'),
        ('technology', 'Technology')
    ], string='Asset Type', default='all')
    include_compliance_only = fields.Boolean(string='Include Compliance Only', default=False)
    comparison_period = fields.Selection([
        ('none', 'No Comparison'),
        ('previous_period', 'Previous Period'),
        ('previous_year', 'Previous Year'),
        ('custom', 'Custom Period')
    ], string='Comparison Period', default='none')
    custom_comparison_from = fields.Date(string='Custom Comparison From')
    custom_comparison_to = fields.Date(string='Custom Comparison To')
    
    # Advanced analytics
    include_predictive_analysis = fields.Boolean(string='Include Predictive Analysis', default=False)
    include_correlation_analysis = fields.Boolean(string='Include Correlation Analysis', default=False)
    include_anomaly_detection = fields.Boolean(string='Include Anomaly Detection', default=False)
    include_advanced_analytics = fields.Boolean(string='Include Advanced Analytics', default=False)
    
    # Report content
    include_charts = fields.Boolean(string='Include Charts', default=True)
    include_executive_summary = fields.Boolean(string='Include Executive Summary', default=True)
    include_recommendations = fields.Boolean(string='Include Recommendations', default=True)
    include_benchmarks = fields.Boolean(string='Include Benchmarks', default=False)
    include_risk_analysis = fields.Boolean(string='Include Risk Analysis', default=True)
    include_trends = fields.Boolean(string='Include Trends', default=True)
    include_forecasting = fields.Boolean(string='Include Forecasting', default=False)
    
    # Data inclusion
    include_emissions_data = fields.Boolean(string='Include Emissions Data', default=True)
    include_offset_data = fields.Boolean(string='Include Offset Data', default=True)
    include_community_data = fields.Boolean(string='Include Community Data', default=True)
    include_initiatives_data = fields.Boolean(string='Include Initiatives Data', default=True)
    include_gender_parity_data = fields.Boolean(string='Include Gender Parity Data', default=True)
    include_pay_gap_data = fields.Boolean(string='Include Pay Gap Data', default=True)
    include_analytics_data = fields.Boolean(string='Include Analytics Data', default=True)
    
    # Report sections
    include_section_environmental = fields.Boolean(string='Include Environmental Section', default=True)
    include_section_social = fields.Boolean(string='Include Social Section', default=True)
    include_section_governance = fields.Boolean(string='Include Governance Section', default=True)
    include_section_analytics = fields.Boolean(string='Include Analytics Section', default=True)
    include_section_recommendations = fields.Boolean(string='Include Recommendations Section', default=True)
    
    # Thresholds and alerts
    include_thresholds = fields.Boolean(string='Include Thresholds', default=True)
    carbon_threshold = fields.Float(string='Carbon Threshold', default=1000.0)
    compliance_threshold = fields.Float(string='Compliance Threshold', default=95.0)
    social_impact_threshold = fields.Float(string='Social Impact Threshold', default=80.0)
    
    # Report styling
    include_logo = fields.Boolean(string='Include Logo', default=True)
    include_footer = fields.Boolean(string='Include Footer', default=True)
    
    # Custom configuration
    custom_metrics = fields.Text(string='Custom Metrics (JSON)', default='{}')
    custom_charts = fields.Text(string='Custom Charts (JSON)', default='{}')
    
    # Company reference
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_generate_enhanced_esg_report(self):
        """Generate enhanced ESG report based on the new esg.asset model."""
        _logger.info(f"ESG REPORT: Starting report generation: {self.report_name}")

        domain = [
            ('purchase_date', '>=', self.date_from),
            ('purchase_date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        assets = self.env['esg.asset'].search(domain)

        if not assets:
            raise UserError(_('No ESG assets found for the selected period. Please create some assets first or adjust the date range.'))

        _logger.info(f"ESG REPORT: Found {len(assets)} assets to process.")

        report_data = self._prepare_report_data(assets)
        return self.env.ref('esg_reporting.action_enhanced_esg_report_pdf').report_action(self, data=report_data)

    def _prepare_report_data(self, assets):
        """Prepare the data dictionary for the report template."""
        return {
            'report_info': {
                'name': self.report_name,
                'date_from': self.date_from.isoformat(),
                'date_to': self.date_to.isoformat(),
                'company': self.company_id.name,
                'total_assets': len(assets),
            },
            'environmental_metrics': self._calculate_environmental_metrics(assets),
            'social_metrics': self._calculate_social_metrics(assets),
            'governance_metrics': self._calculate_governance_metrics(assets),
            'assets': assets.read([]) # Pass asset data to template if needed
        }

    def _calculate_environmental_metrics(self, assets):
        total_energy = sum(assets.mapped('energy_consumption'))
        total_water = sum(assets.mapped('water_consumption'))
        total_carbon = sum(assets.mapped('carbon_footprint'))
        total_waste = sum(assets.mapped('waste_generated'))
        avg_recycling = sum(assets.mapped('recycling_rate')) / len(assets) if assets else 0
        return {
            'total_energy_consumption': round(total_energy, 2),
            'total_water_consumption': round(total_water, 2),
            'total_carbon_footprint': round(total_carbon, 2),
            'total_waste_generated': round(total_waste, 2),
            'average_recycling_rate': round(avg_recycling, 2),
        }

    def _calculate_social_metrics(self, assets):
        total_employees = sum(assets.mapped('number_of_employees'))
        total_training = sum(assets.mapped('training_hours'))
        total_incidents = sum(assets.mapped('safety_incidents'))
        total_investment = sum(assets.mapped('community_investment'))
        avg_diversity = sum(assets.mapped('diversity_ratio')) / len(assets) if assets else 0
        return {
            'total_employees': total_employees,
            'total_training_hours': round(total_training, 2),
            'total_safety_incidents': total_incidents,
            'total_community_investment': round(total_investment, 2),
            'average_diversity_ratio': round(avg_diversity, 2),
        }

    def _calculate_governance_metrics(self, assets):
        total_violations = sum(assets.mapped('ethical_violations'))
        avg_score = sum(assets.mapped('governance_score')) / len(assets) if assets else 0
        return {
            'total_ethical_violations': total_violations,
            'average_governance_score': round(avg_score, 2),
        }
