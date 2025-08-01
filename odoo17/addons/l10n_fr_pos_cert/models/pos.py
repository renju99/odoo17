# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from hashlib import sha256
from json import dumps, loads
import logging

from odoo import models, api, fields
from odoo.fields import Datetime
from odoo.tools.translate import _, _lt
from odoo.exceptions import UserError
from collections import defaultdict

_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    _inherit = 'pos.config'

    def open_ui(self):
        for config in self:
            if not config.company_id.country_id:
                raise UserError(_("You have to set a country in your company setting."))
            if config.company_id._is_accounting_unalterable():
                if config.current_session_id:
                    config.current_session_id._check_session_timing()
        return super(pos_config, self).open_ui()

    def _config_sequence_implementation(self):
        return 'no_gap' if self.env.company._is_accounting_unalterable() else super()._config_sequence_implementation()


class pos_session(models.Model):
    _inherit = 'pos.session'

    def _check_session_timing(self):
        self.ensure_one()
        return True

    def open_frontend_cb(self):
        sessions_to_check = self.filtered(lambda s: s.config_id.company_id._is_accounting_unalterable())
        sessions_to_check.filtered(lambda s: s.state == 'opening_control').start_at = fields.Datetime.now()
        for session in sessions_to_check:
            session._check_session_timing()
        return super(pos_session, self).open_frontend_cb()


ORDER_FIELDS = ['date_order', 'user_id', 'lines', 'payment_ids', 'pricelist_id', 'partner_id', 'session_id', 'pos_reference', 'sale_journal', 'fiscal_position_id']
LINE_FIELDS = ['notice', 'product_id', 'qty', 'price_unit', 'discount', 'tax_ids', 'tax_ids_after_fiscal_position']
ERR_MSG = _lt('According to the French law, you cannot modify a %s. Forbidden fields: %s.')


class pos_order(models.Model):
    _inherit = 'pos.order'

    l10n_fr_hash = fields.Char(string="Inalteralbility Hash", readonly=True, copy=False)
    l10n_fr_secure_sequence_number = fields.Integer(string="Inalteralbility No Gap Sequence #", readonly=True, copy=False)
    l10n_fr_string_to_hash = fields.Char(compute='_compute_string_to_hash', readonly=True, store=False)

    def _get_new_hash(self, secure_seq_number):
        """ Returns the hash to write on pos orders when they get posted"""
        self.ensure_one()
        #get the only one exact previous order in the securisation sequence
        prev_order = self.search([('state', 'in', ['paid', 'done', 'invoiced']),
                                 ('company_id', '=', self.company_id.id),
                                 ('l10n_fr_secure_sequence_number', '!=', 0),
                                 ('l10n_fr_secure_sequence_number', '=', int(secure_seq_number) - 1)])
        if prev_order and len(prev_order) != 1:
            raise UserError(
               _('An error occurred when computing the inalterability. Impossible to get the unique previous posted point of sale order.'))

        #build and return the hash
        computed_hash = self._compute_hash(prev_order.l10n_fr_hash if prev_order else '')
        _logger.info(
            'Computed hash for order ID %s: %s \n String to hash: %s \n Previous hash: %s',
            self.id,
            computed_hash,
            dumps(loads(self.l10n_fr_string_to_hash), indent=2),
            prev_order.l10n_fr_hash
        )
        return computed_hash

    def _compute_hash(self, previous_hash):
        """ Computes the hash of the browse_record given as self, based on the hash
        of the previous record in the company's securisation sequence given as parameter"""
        self.ensure_one()
        hash_string = sha256((previous_hash + self.l10n_fr_string_to_hash).encode('utf-8'))
        return hash_string.hexdigest()

    def _compute_string_to_hash(self):
        def _getattrstring(field_value, field_type, model_name=None):
            if field_type in ('many2many', 'one2many'):
                if field_value:
                    sorted_ids = sorted_relational_ids.get(model_name, [])
                    value_set = set(field_value)
                    field_value = [id for id in sorted_ids if id in value_set]
                else:
                    field_value = []
            return str(field_value)

        def collect_sorted_relational_ids(orders_data, lines_data, order_field_defs, line_field_defs):
            relational_ids = defaultdict(set)

            for data_list, field_names, field_defs in (
                (orders_data, ORDER_FIELDS, order_field_defs),
                (lines_data, LINE_FIELDS, line_field_defs),
            ):
                for record in data_list:
                    for field in field_names:
                        field_def = field_defs.get(field)
                        if field_def and field_def['type'] in ('many2many', 'one2many'):
                            ids = record.get(field) or []
                            relational_ids[field_def['comodel']].update(ids)

            sorted_relational_ids = {}
            for model_name, ids in relational_ids.items():
                if ids:
                    # Use search() to get IDs sorted by _order the same way Odoo ORM does for relational fields
                    sorted_relational_ids[model_name] = self.env[model_name].search([('id', 'in', list(ids))]).ids

            return sorted_relational_ids

        orders_data = self.read(ORDER_FIELDS + ['id'], load='')
        lines_data = self.lines.read(LINE_FIELDS + ['id', 'order_id'], load='')

        orders_by_id = {order['id']: order for order in orders_data}
        lines_by_order = defaultdict(list)
        for line in lines_data:
            lines_by_order[line['order_id']].append(line)
        order_field_defs = {
            field: {
                'type': self._fields[field].type,
                'comodel': self._fields[field].comodel_name if hasattr(self._fields[field], 'comodel_name') else None
            }
            for field in ORDER_FIELDS
        }
        line_field_defs = {
            field: {
                'type': self.lines._fields[field].type,
                'comodel': self.lines._fields[field].comodel_name if hasattr(self.lines._fields[field], 'comodel_name') else None
            }
            for field in LINE_FIELDS
        }

        sorted_relational_ids = collect_sorted_relational_ids(orders_data, lines_data, order_field_defs, line_field_defs)

        for order in self:
            values = {}
            order_data = orders_by_id[order.id]

            for field in ORDER_FIELDS:
                field_def = order_field_defs[field]
                values[field] = _getattrstring(order_data.get(field), field_def['type'], field_def['comodel'])

            for line in lines_by_order[order.id]:
                for field in LINE_FIELDS:
                    k = 'line_%d_%s' % (line['id'], field)
                    field_def = line_field_defs[field]
                    values[k] = _getattrstring(line.get(field), field_def['type'], field_def['comodel'])

            #make the json serialization canonical
            #  (https://tools.ietf.org/html/draft-staykov-hu-json-canonical-form-00)
            order.l10n_fr_string_to_hash = dumps(values, sort_keys=True,
                                                ensure_ascii=True, indent=None,
                                                separators=(',',':'))

    def write(self, vals):
        has_been_posted = False
        for order in self:
            if order.company_id._is_accounting_unalterable():
                # write the hash and the secure_sequence_number when posting or invoicing an pos.order
                if vals.get('state') in ['paid', 'done', 'invoiced']:
                    has_been_posted = True

                # restrict the operation in case we are trying to write a forbidden field
                if (order.state in ['paid', 'done', 'invoiced'] and set(vals).intersection(ORDER_FIELDS)):
                    raise UserError(_('According to the French law, you cannot modify a point of sale order. Forbidden fields: %s.') % ', '.join(ORDER_FIELDS))
                # restrict the operation in case we are trying to overwrite existing hash
                if (order.l10n_fr_hash and 'l10n_fr_hash' in vals) or (order.l10n_fr_secure_sequence_number and 'l10n_fr_secure_sequence_number' in vals):
                    raise UserError(_('You cannot overwrite the values ensuring the inalterability of the point of sale.'))
        res = super(pos_order, self).write(vals)
        # write the hash and the secure_sequence_number when posting or invoicing a pos order
        if has_been_posted:
            for order in self.filtered(lambda o: o.company_id._is_accounting_unalterable() and
                                                not (o.l10n_fr_secure_sequence_number or o.l10n_fr_hash)):
                new_number = order.company_id.l10n_fr_pos_cert_sequence_id.next_by_id()
                vals_hashing = {'l10n_fr_secure_sequence_number': new_number,
                                'l10n_fr_hash': order._get_new_hash(new_number)}
                res |= super(pos_order, order).write(vals_hashing)
        return res

    @api.ondelete(at_uninstall=True)
    def _unlink_except_pos_so(self):
        for order in self:
            if order.company_id._is_accounting_unalterable():
                raise UserError(_("According to French law, you cannot delete a point of sale order."))

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        res['l10n_fr_hash'] = order.l10n_fr_hash
        return res

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def write(self, vals):
        # restrict the operation in case we are trying to write a forbidden field
        if set(vals).intersection(LINE_FIELDS):
            if any(l.company_id._is_accounting_unalterable() and l.order_id.state in ['done', 'invoiced'] for l in self):
                raise UserError(_('According to the French law, you cannot modify a point of sale order line. Forbidden fields: %s.') % ', '.join(LINE_FIELDS))
        return super(PosOrderLine, self).write(vals)
