# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.exceptions import UserError, RedirectWarning


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_in_edi_username = fields.Char("Indian EDI username", related="company_id.l10n_in_edi_username", readonly=False)
    l10n_in_edi_password = fields.Char("Indian EDI password", related="company_id.l10n_in_edi_password", readonly=False)
    l10n_in_edi_production_env = fields.Boolean(
        string="Indian EDI Testing Environment",
        related="company_id.l10n_in_edi_production_env",
        readonly=False
    )

    def l10n_in_check_gst_number(self):
        if not self.company_id.vat:
            action = {
                    "view_mode": "form",
                    "res_model": "res.company",
                    "type": "ir.actions.act_window",
                    "res_id" : self.company_id.id,
                    "views": [[self.env.ref("base.view_company_form").id, "form"]],
            }
            raise RedirectWarning(_("Please enter a GST number in company."), action, _('Go to Company'))

    def l10n_in_edi_test(self):
        self.l10n_in_check_gst_number()
        response = self.env['account.edi.format']._l10n_in_edi_authenticate(self.company_id)
        if response.get('error'):
            raise UserError("\n".join(["[%s] %s" % (e.get('code'), (e.get('message'))) for e in response['error']]))
        elif not self.company_id.sudo()._l10n_in_edi_token_is_valid():
            raise UserError(_("Incorrect username or password, or the GST number on company does not match."))
        return {
              'type': 'ir.actions.client',
              'tag': 'display_notification',
              'params': {
                  'type': 'info',
                  'sticky': False,
                  'message': _("API credentials validated successfully"),
              }
          }

    def l10n_in_edi_buy_iap(self):
        if not self.l10n_in_edi_production_env:
            raise UserError(_("You must enable production environment to buy credits"))
        return {
            'type': 'ir.actions.act_url',
            'url': self.env["iap.account"].get_credits_url(service_name="l10n_in_edi", base_url=''),
            'target': '_new'
        }
