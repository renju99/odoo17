from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AssetDisposalWizard(models.TransientModel):
    _name = 'asset.disposal.wizard'
    _description = 'Asset Disposal Wizard'

    asset_id = fields.Many2one('facility.asset', string='Asset', required=True)
    disposal_reason = fields.Text(string='Disposal Reason', required=True)
    disposal_date = fields.Date(string='Disposal Date', required=True, default=fields.Date.today)
    disposal_method = fields.Selection([
        ('sale', 'Sale'),
        ('donation', 'Donation'),
        ('scrap', 'Scrap'),
        ('other', 'Other')
    ], string='Disposal Method', required=True)
    notes = fields.Text(string='Additional Notes')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_asset_id'):
            asset = self.env['facility.asset'].browse(self.env.context.get('default_asset_id'))
            res['asset_id'] = asset.id
        return res

    def action_dispose_asset(self):
        """Dispose the selected asset"""
        self.ensure_one()
        
        if not self.asset_id:
            raise ValidationError(_('Please select an asset to dispose.'))
        
        if self.asset_id.status == 'disposed':
            raise ValidationError(_('This asset is already disposed.'))
        
        # Update the asset with disposal information
        self.asset_id.write({
            'status': 'disposed',
            'disposal_date': self.disposal_date,
            'disposal_reason': self.disposal_reason,
            'disposal_method': self.disposal_method,
            'notes': self.notes or self.asset_id.notes,
        })
        
        # Log the disposal action
        self.asset_id.message_post(
            body=_('Asset disposed via wizard. Reason: %s, Method: %s') % (
                self.disposal_reason, dict(self._fields['disposal_method'].selection).get(self.disposal_method)
            )
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Asset "%s" has been successfully disposed.') % self.asset_id.name,
                'type': 'success',
            }
        }