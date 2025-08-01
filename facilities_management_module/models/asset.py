from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Asset(models.Model):
    _name = 'facility.asset'
    _description = 'Facility Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    code = fields.Char(string='Asset Code', tracking=True)
    asset_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('building', 'Building'),
        ('other', 'Other')
    ], string='Asset Type', required=True, default='equipment', tracking=True)
    
    purchase_date = fields.Date(string='Purchase Date', tracking=True)
    purchase_cost = fields.Float(string='Purchase Cost', tracking=True)
    current_value = fields.Float(string='Current Value', tracking=True)
    
    location = fields.Char(string='Location', tracking=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed')
    ], string='Status', default='active', tracking=True)
    
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    
    disposal_date = fields.Date(string='Disposal Date', tracking=True)
    disposal_reason = fields.Text(string='Disposal Reason')
    disposal_method = fields.Selection([
        ('sale', 'Sale'),
        ('donation', 'Donation'),
        ('scrap', 'Scrap'),
        ('other', 'Other')
    ], string='Disposal Method')
    
    @api.constrains('purchase_date', 'disposal_date')
    def _check_dates(self):
        for record in self:
            if record.purchase_date and record.disposal_date:
                if record.disposal_date < record.purchase_date:
                    raise ValidationError(_('Disposal date cannot be earlier than purchase date.'))
    
    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'disposed' and not self.disposal_date:
            self.disposal_date = fields.Date.today()