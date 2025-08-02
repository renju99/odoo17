from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AssetCertification(models.Model):
    _name = 'asset.certification'
    _description = 'Asset Certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Certification Name', required=True, tracking=True)
    code = fields.Char(string='Certification Code', tracking=True)
    certification_type = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
        ('safety', 'Safety'),
        ('quality', 'Quality'),
        ('other', 'Other')
    ], string='Certification Type', required=True, default='environmental', tracking=True)
    
    issuing_body = fields.Char(string='Issuing Body', tracking=True)
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    is_active = fields.Boolean(string='Active', default=True, tracking=True)
    
    description = fields.Text(string='Description')
    requirements = fields.Text(string='Requirements')
    
    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for record in self:
            if record.issue_date and record.expiry_date:
                if record.expiry_date < record.issue_date:
                    raise ValidationError(_('Expiry date cannot be earlier than issue date.'))
    
    @api.onchange('expiry_date')
    def _onchange_expiry_date(self):
        if self.expiry_date and self.expiry_date < fields.Date.today():
            self.is_active = False