# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EsgInitiativeTag(models.Model):
    _name = 'esg.initiative.tag'
    _description = 'ESG Initiative Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)