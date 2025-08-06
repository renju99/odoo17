# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class EnhancedESGWizard(models.TransientModel):
    _name = 'enhanced.esg.wizard'
    _description = 'Enhanced ESG Report Wizard'

    report_name = fields.Char(string='Report Name', required=True, default='Enhanced ESG Report')
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
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
