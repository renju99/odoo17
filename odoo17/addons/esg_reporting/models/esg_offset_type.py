# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EsgOffsetType(models.Model):
    _name = 'esg.offset.type'
    _description = 'ESG Offset Type'

    name = fields.Char(string='Offset Type Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    category = fields.Selection([
        ('renewable_energy', 'Renewable Energy'),
        ('forestry', 'Forestry'),
        ('ocean_conservation', 'Ocean Conservation'),
        ('clean_technology', 'Clean Technology'),
        ('other', 'Other')
    ], string='Category', required=True)
    verification_standard = fields.Char(string='Verification Standard')
    active = fields.Boolean(default=True)