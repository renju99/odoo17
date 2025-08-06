from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SLADeactivationWizard(models.TransientModel):
    _name = 'facilities.sla.deactivation.wizard'
    _description = 'SLA Deactivation Wizard'

    sla_id = fields.Many2one('facilities.sla', string='SLA', required=True, readonly=True)
    deactivation_reason = fields.Text(string='Deactivation Reason', required=True, 
                                     help="Please provide a reason for deactivating this SLA")
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)
        if self.env.context.get('default_sla_id'):
            res['sla_id'] = self.env.context.get('default_sla_id')
            _logger.info(f"Initialized SLA deactivation wizard for SLA ID: {res['sla_id']}")
        return res

    def action_confirm_deactivation(self):
        """Confirm SLA deactivation with reason"""
        self.ensure_one()
        if not self.deactivation_reason.strip():
            raise UserError(_('Please provide a reason for deactivating this SLA.'))
        
        try:
            _logger.info(f"User {self.env.user.name} confirming deactivation for SLA: {self.sla_id.name}")
            
            # Call the SLA model's deactivation method
            result = self.sla_id._deactivate_sla_with_reason(self.deactivation_reason)
            
            _logger.info(f"SLA '{self.sla_id.name}' deactivation confirmed by user {self.env.user.name}")
            
            return result
        except Exception as e:
            _logger.error(f"Error in SLA deactivation wizard for SLA '{self.sla_id.name}': {str(e)}")
            raise UserError(_('Failed to deactivate SLA: %s') % str(e))