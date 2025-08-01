from odoo import models, fields, api
from datetime import datetime, timedelta


class ESGReportWizard(models.TransientModel):
    _name = 'esg.report.wizard'
    _description = 'ESG Report Wizard'

    report_type = fields.Selection([
        ('environmental', 'Environmental Report'),
        ('social', 'Social Impact Report'),
        ('governance', 'Governance Report'),
        ('comprehensive', 'Comprehensive ESG Report')
    ], string='Report Type', required=True, default='comprehensive')
    
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    
    asset_type = fields.Selection([
        ('all', 'All Assets'),
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('building', 'Building'),
        ('other', 'Other')
    ], string='Asset Type', default='all')
    
    include_compliance_only = fields.Boolean(string='Include ESG Compliance Assets Only', default=False)
    include_charts = fields.Boolean(string='Include Charts and Graphs', default=True)
    include_recommendations = fields.Boolean(string='Include Recommendations', default=True)
    
    def action_generate_esg_report(self):
        """Generate ESG report based on selected criteria"""
        # Get assets based on filters
        domain = [
            ('purchase_date', '>=', self.date_from),
            ('purchase_date', '<=', self.date_to)
        ]
        
        if self.asset_type != 'all':
            domain.append(('asset_type', '=', self.asset_type))
        
        if self.include_compliance_only:
            domain.append(('esg_compliance', '=', True))
        
        assets = self.env['facility.asset'].search(domain)
        
        # Prepare report data
        report_data = {
            'wizard': self,
            'assets': assets,
            'total_assets': len(assets),
            'environmental_assets': assets.filtered(lambda a: a.environmental_impact),
            'social_assets': assets.filtered(lambda a: a.safety_compliance or a.accessibility_compliant),
            'governance_assets': assets.filtered(lambda a: a.regulatory_compliance),
            'compliance_rate': self._calculate_compliance_rate(assets),
            'environmental_metrics': self._calculate_environmental_metrics(assets),
            'social_metrics': self._calculate_social_metrics(assets),
            'governance_metrics': self._calculate_governance_metrics(assets),
            'generation_date': fields.Date.today(),
        }
        
        # Return report action
        return self.env.ref('facilities_management_module.action_esg_report_pdf').report_action(self, data=report_data)
    
    def _calculate_compliance_rate(self, assets):
        """Calculate overall ESG compliance rate"""
        if not assets:
            return 0
        
        compliant_assets = assets.filtered(lambda a: a.esg_compliance)
        return (len(compliant_assets) / len(assets)) * 100
    
    def _calculate_environmental_metrics(self, assets):
        """Calculate environmental metrics"""
        env_assets = assets.filtered(lambda a: a.environmental_impact)
        
        metrics = {
            'total_carbon_footprint': sum(env_assets.mapped('carbon_footprint') or [0]),
            'renewable_energy_assets': len(env_assets.filtered(lambda a: a.renewable_energy)),
            'energy_efficiency_distribution': {},
            'environmental_impact_distribution': {}
        }
        
        # Calculate energy efficiency distribution
        for asset in env_assets:
            rating = asset.energy_efficiency_rating
            if rating:
                metrics['energy_efficiency_distribution'][rating] = metrics['energy_efficiency_distribution'].get(rating, 0) + 1
        
        # Calculate environmental impact distribution
        for asset in env_assets:
            impact = asset.environmental_impact
            if impact:
                metrics['environmental_impact_distribution'][impact] = metrics['environmental_impact_distribution'].get(impact, 0) + 1
        
        return metrics
    
    def _calculate_social_metrics(self, assets):
        """Calculate social impact metrics"""
        social_assets = assets.filtered(lambda a: a.safety_compliance or a.accessibility_compliant)
        
        metrics = {
            'safety_compliant_assets': len(assets.filtered(lambda a: a.safety_compliance)),
            'accessibility_compliant_assets': len(assets.filtered(lambda a: a.accessibility_compliant)),
            'average_social_impact_score': 0,
            'total_social_impact_score': 0
        }
        
        # Calculate average social impact score
        scored_assets = assets.filtered(lambda a: a.social_impact_score)
        if scored_assets:
            total_score = sum(scored_assets.mapped('social_impact_score'))
            metrics['total_social_impact_score'] = total_score
            metrics['average_social_impact_score'] = total_score / len(scored_assets)
        
        return metrics
    
    def _calculate_governance_metrics(self, assets):
        """Calculate governance metrics"""
        gov_assets = assets.filtered(lambda a: a.regulatory_compliance)
        
        metrics = {
            'regulatory_compliant_assets': len(gov_assets),
            'assets_with_certifications': len(assets.filtered(lambda a: a.certification_ids)),
            'total_certifications': sum(assets.mapped(lambda a: len(a.certification_ids))),
            'audits_due_soon': len(assets.filtered(lambda a: a.next_audit_date and a.next_audit_date <= fields.Date.today() + timedelta(days=30)))
        }
        
        return metrics