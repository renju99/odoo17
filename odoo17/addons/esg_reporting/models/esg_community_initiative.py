# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EsgCommunityInitiative(models.Model):
    _name = 'esg.community.initiative'
    _description = 'ESG Community Initiative'

    name = fields.Char(string='Initiative Name', required=True)
    description = fields.Text(string='Description')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    budget = fields.Monetary(string='Budget', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='planned')
    impact_metrics = fields.Text(string='Impact Metrics')
    active = fields.Boolean(default=True)