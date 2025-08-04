# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EsgMaterialityAssessment(models.Model):
    _name = 'esg.materiality.assessment'
    _description = 'ESG Materiality Assessment'

    name = fields.Char(string='Assessment Name', required=True)
    assessment_date = fields.Date(string='Assessment Date', required=True)
    stakeholder_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('both', 'Both')
    ], string='Stakeholder Type', required=True)
    materiality_level = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], string='Materiality Level', required=True)
    description = fields.Text(string='Description')
    findings = fields.Text(string='Key Findings')
    recommendations = fields.Text(string='Recommendations')
    active = fields.Boolean(default=True)