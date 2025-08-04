# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EnhancedEsgWizard(models.TransientModel):
    _name = 'enhanced.esg.wizard'
    _description = 'Enhanced ESG Wizard'

    name = fields.Char(string='Report Name', required=True)
    report_type = fields.Selection([
        ('sustainability', 'Sustainability Report'),
        ('compliance', 'Compliance Report'),
        ('risk_assessment', 'Risk Assessment'),
        ('performance', 'Performance Report')
    ], string='Report Type', required=True)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    include_charts = fields.Boolean(string='Include Charts', default=True)
    include_analytics = fields.Boolean(string='Include Analytics', default=True)
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
        ('json', 'JSON'),
        ('csv', 'CSV')
    ], string='Output Format', default='pdf', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated')
    ], string='Status', default='draft')

    def generate_report(self):
        self.ensure_one()
        self.state = 'generated'
        return {
            'type': 'ir.actions.act_window',
            'name': 'ESG Report Generated',
            'res_model': 'enhanced.esg.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }