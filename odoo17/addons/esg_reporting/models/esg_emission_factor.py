# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EsgEmissionFactor(models.Model):
    _name = 'esg.emission.factor'
    _description = 'ESG Emission Factor'

    name = fields.Char(string='Name', required=True)
    factor_type = fields.Selection([
        ('scope1', 'Scope 1'),
        ('scope2', 'Scope 2'),
        ('scope3', 'Scope 3')
    ], string='Factor Type', required=True)
    value = fields.Float(string='Factor Value', required=True)
    unit = fields.Char(string='Unit', default='tCO2e')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)