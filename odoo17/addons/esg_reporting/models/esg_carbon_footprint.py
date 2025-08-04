from odoo import models, fields

class ESGCarbonFootprint(models.Model):
    _name = 'esg.carbon.footprint'
    _description = 'ESG Carbon Footprint'

    name = fields.Char(string='Name', required=True)
    value = fields.Float(string='Value', required=True)
