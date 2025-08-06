# -*- coding: utf-8 -*-
from odoo import models, fields

class EsgAsset(models.Model):
    _name = 'esg.asset'
    _description = 'ESG Asset'

    name = fields.Char(string='Asset Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    category_id = fields.Many2one('esg.asset.category', string='Category')
    purchase_date = fields.Date(string='Purchase Date')
    asset_value = fields.Float(string='Asset Value')

    # Environmental
    energy_consumption = fields.Float(string='Energy Consumption (kWh)')
    water_consumption = fields.Float(string='Water Consumption (m³)')
    carbon_footprint = fields.Float(string='Carbon Footprint (tCO2e)')
    waste_generated = fields.Float(string='Waste Generated (kg)')
    recycling_rate = fields.Float(string='Recycling Rate (%)')

    # Social
    number_of_employees = fields.Integer(string='Number of Employees')
    training_hours = fields.Float(string='Training Hours per Employee')
    safety_incidents = fields.Integer(string='Safety Incidents')
    community_investment = fields.Float(string='Community Investment ($)')
    diversity_ratio = fields.Float(string='Diversity Ratio (%)')
    gender_pay_gap = fields.Float(string='Gender Pay Gap (%)')

    # Governance
    ethical_violations = fields.Integer(string='Ethical Violations')
    governance_score = fields.Float(string='Governance Score (1-100)')

class EsgAssetCategory(models.Model):
    _name = 'esg.asset.category'
    _description = 'ESG Asset Category'

    name = fields.Char(string='Category Name', required=True)
    category_type = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance')
    ], string='Category Type', required=True)
