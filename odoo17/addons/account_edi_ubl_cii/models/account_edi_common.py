from odoo import _, models, Command
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_repr, find_xml_value
from odoo.tools.float_utils import float_round
from odoo.tools.misc import clean_context, formatLang
from odoo.tools.zeep import Client

from markupsafe import Markup

# -------------------------------------------------------------------------
# UNIT OF MEASURE
# -------------------------------------------------------------------------
UOM_TO_UNECE_CODE = {
    'uom.product_uom_unit': 'C62',
    'uom.product_uom_dozen': 'DZN',
    'uom.product_uom_kgm': 'KGM',
    'uom.product_uom_gram': 'GRM',
    'uom.product_uom_day': 'DAY',
    'uom.product_uom_hour': 'HUR',
    'uom.product_uom_ton': 'TNE',
    'uom.product_uom_meter': 'MTR',
    'uom.product_uom_km': 'KMT',
    'uom.product_uom_cm': 'CMT',
    'uom.product_uom_litre': 'LTR',
    'uom.product_uom_cubic_meter': 'MTQ',
    'uom.product_uom_lb': 'LBR',
    'uom.product_uom_oz': 'ONZ',
    'uom.product_uom_inch': 'INH',
    'uom.product_uom_foot': 'FOT',
    'uom.product_uom_mile': 'SMI',
    'uom.product_uom_floz': 'OZA',
    'uom.product_uom_qt': 'QT',
    'uom.product_uom_gal': 'GLL',
    'uom.product_uom_cubic_inch': 'INQ',
    'uom.product_uom_cubic_foot': 'FTQ',
    'uom.uom_square_meter': 'MTK',
    'uom.uom_square_foot': 'FTK',
    'uom.product_uom_yard': 'YRD',
    'uom.product_uom_millimeter': 'MMT',
}

# -------------------------------------------------------------------------
# ELECTRONIC ADDRESS SCHEME (EAS), see https://docs.peppol.eu/poacc/billing/3.0/codelist/eas/
# -------------------------------------------------------------------------
EAS_MAPPING = {
    'AD': {'9922': 'vat'},
    'AE': {'0235': 'vat'},
    'AL': {'9923': 'vat'},
    'AT': {'9915': 'vat'},
    'AU': {'0151': 'vat'},
    'BA': {'9924': 'vat'},
    'BE': {'0208': 'company_registry'},
    'BG': {'9926': 'vat'},
    'CH': {'9927': 'vat'},
    'CY': {'9928': 'vat'},
    'CZ': {'9929': 'vat'},
    'DE': {'9930': 'vat'},
    'DK': {'0184': 'company_registry', '0198': 'vat'},
    'EE': {'9931': 'vat'},
    'ES': {'9920': 'vat'},
    'FI': {'0216': None},
    'FR': {'0009': 'siret', '9957': 'vat'},
    'SG': {'0195': 'l10n_sg_unique_entity_number'},
    'GB': {'9932': 'vat'},
    'GR': {'9933': 'vat'},
    'HR': {'9934': 'vat'},
    'HU': {'9910': 'l10n_hu_eu_vat'},
    'IE': {'9935': 'vat'},
    'IS': {'0196': 'vat'},
    'IT': {'0211': 'vat', '0210': 'l10n_it_codice_fiscale'},
    'JP': {'0221': 'vat'},
    'LI': {'9936': 'vat'},
    'LT': {'9937': 'vat'},
    'LU': {'9938': 'vat'},
    'LV': {'0218': 'company_registry', '9939': 'vat'},
    'MC': {'9940': 'vat'},
    'ME': {'9941': 'vat'},
    'MK': {'9942': 'vat'},
    'MT': {'9943': 'vat'},
    # Do not add the vat for NL, since: "[NL-R-003] For suppliers in the Netherlands, the legal entity identifier
    # MUST be either a KVK or OIN number (schemeID 0106 or 0190)" in the Bis 3 rules (in PartyLegalEntity/CompanyID).
    'NL': {'0106': None, '0190': None},
    'NO': {'0192': 'l10n_no_bronnoysund_number'},
    'NZ': {'0088': 'company_registry'},
    'PL': {'9945': 'vat'},
    'PT': {'9946': 'vat'},
    'RO': {'9947': 'vat'},
    'RS': {'9948': 'vat'},
    'SE': {'0007': 'company_registry'},
    'SI': {'9949': 'vat'},
    'SK': {'9950': 'vat'},
    'SM': {'9951': 'vat'},
    'TR': {'9952': 'vat'},
    'VA': {'9953': 'vat'},
}


class AccountEdiCommon(models.AbstractModel):
    _name = "account.edi.common"
    _description = "Common functions for EDI documents: generate the data, the constraints, etc"

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def format_float(self, amount, precision_digits):
        if amount is None:
            return None
        return float_repr(float_round(amount, precision_digits), precision_digits)

    def _get_currency_decimal_places(self, currency_id):
        # Allows other documents to easily override in case there is a flat max precision number
        return currency_id.decimal_places

    def _get_uom_unece_code(self, line):
        """
        list of codes: https://docs.peppol.eu/poacc/billing/3.0/codelist/UNECERec20/
        or https://unece.org/fileadmin/DAM/cefact/recommendations/bkup_htm/add2c.htm (sorted by letter)
        """
        xmlid = line.product_uom_id.get_external_id()
        if xmlid and line.product_uom_id.id in xmlid:
            return UOM_TO_UNECE_CODE.get(xmlid[line.product_uom_id.id], 'C62')
        return 'C62'

    def _find_value(self, xpath, tree, nsmap=False):
        # avoid 'TypeError: empty namespace prefix is not supported in XPath'
        nsmap = nsmap or {k: v for k, v in tree.nsmap.items() if k is not None}
        return find_xml_value(xpath, tree, nsmap)

    # -------------------------------------------------------------------------
    # TAXES
    # -------------------------------------------------------------------------

    def _validate_taxes(self, invoice):
        """ Validate the structure of the tax repartition lines (invalid structure could lead to unexpected results)
        """
        for tax in invoice.invoice_line_ids.tax_ids:
            try:
                tax._validate_repartition_lines()
            except ValidationError as e:
                error_msg = _("Tax '%s' is invalid: %s", tax.name, e.args[0])  # args[0] gives the error message
                raise ValidationError(error_msg)

    def _get_tax_unece_codes(self, invoice, tax):
        """
        Source: doc of Peppol (but the CEF norm is also used by factur-x, yet not detailed)
        https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-TaxTotal/cac-TaxSubtotal/cac-TaxCategory/cbc-TaxExemptionReasonCode/
        https://docs.peppol.eu/poacc/billing/3.0/codelist/vatex/
        https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305/
        :returns: {
            tax_category_code: str,
            tax_exemption_reason_code: str,
            tax_exemption_reason: str,
        }
        """
        def create_dict(tax_category_code=None, tax_exemption_reason_code=None, tax_exemption_reason=None):
            return {
                'tax_category_code': tax_category_code,
                'tax_exemption_reason_code': tax_exemption_reason_code,
                'tax_exemption_reason': tax_exemption_reason,
            }

        supplier = invoice.company_id.partner_id.commercial_partner_id
        customer = invoice.commercial_partner_id

        # add Norway, Iceland, Liechtenstein
        european_economic_area = self.env.ref('base.europe').country_ids.mapped('code') + ['NO', 'IS', 'LI']

        if customer.country_id.code == 'ES' and customer.zip:
            if customer.zip[:2] in ('35', '38'):  # Canary
                # [BR-IG-10]-A VAT breakdown (BG-23) with VAT Category code (BT-118) "IGIC" shall not have a VAT
                # exemption reason code (BT-121) or VAT exemption reason text (BT-120).
                return create_dict(tax_category_code='L')
            if customer.zip[:2] in ('51', '52'):
                return create_dict(tax_category_code='M')  # Ceuta & Mellila

        if supplier.country_id == customer.country_id:
            if not tax or tax.amount == 0:
                # in theory, you should indicate the precise law article
                return create_dict(tax_category_code='E', tax_exemption_reason=_('Articles 226 items 11 to 15 Directive 2006/112/EN'))
            else:
                return create_dict(tax_category_code='S')  # standard VAT

        if supplier.country_id.code in european_economic_area and supplier.vat:
            if tax.amount != 0:
                # otherwise, the validator will complain because G and K code should be used with 0% tax
                return create_dict(tax_category_code='S')
            if customer.country_id.code not in european_economic_area:
                return create_dict(
                    tax_category_code='G',
                    tax_exemption_reason_code='VATEX-EU-G',
                    tax_exemption_reason=_('Export outside the EU'),
                )
            if customer.country_id.code in european_economic_area:
                return create_dict(
                    tax_category_code='K',
                    tax_exemption_reason_code='VATEX-EU-IC',
                    tax_exemption_reason=_('Intra-Community supply'),
                )

        if tax.amount != 0:
            return create_dict(tax_category_code='S')
        else:
            return create_dict(tax_category_code='E', tax_exemption_reason=_('Articles 226 items 11 to 15 Directive 2006/112/EN'))

    def _get_tax_category_list(self, invoice, taxes):
        """ Full list: https://unece.org/fileadmin/DAM/trade/untdid/d16b/tred/tred5305.htm
        Subset: https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305/

        :param taxes:   account.tax records.
        :return:        A list of values to fill the TaxCategory foreach template.
        """
        res = []
        for tax in taxes:
            tax_unece_codes = self._get_tax_unece_codes(invoice, tax)
            res.append({
                'id': tax_unece_codes.get('tax_category_code'),
                'percent': tax.amount if tax.amount_type == 'percent' else False,
                'name': tax_unece_codes.get('tax_exemption_reason'),
                'tax_scheme_vals': {'id': 'VAT'},
                **tax_unece_codes,
            })
        return res

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------

    def _check_required_fields(self, record, field_names, custom_warning_message=""):
        """Check if at least one of the field_names are set on the record/dict

        :param record: either a recordSet or a dict
        :param field_names: The field name or list of field name that has to
                            be checked. If a list is provided, check that at
                            least one of them is set.
        :return: an Error message or None
        """
        if not record:
            return custom_warning_message or _("The element %s is required on %s.", record, ', '.join(field_names))

        if not isinstance(field_names, (list, tuple)):
            field_names = (field_names,)

        has_values = any((field_name in record and record[field_name]) for field_name in field_names)
        # field is present
        if has_values:
            return

        # field is not present
        if custom_warning_message or isinstance(record, dict):
            return custom_warning_message or _("The element %s is required on %s.", record, ', '.join(field_names))

        display_field_names = record.fields_get(field_names)
        if len(field_names) == 1:
            display_field = f"'{display_field_names[field_names[0]]['string']}'"
            return _("The field %s is required on %s.", display_field, record.display_name)
        else:
            display_fields = ', '.join(f"'{display_field_names[x]['string']}'" for x in display_field_names)
            return _("At least one of the following fields %s is required on %s.", display_fields, record.display_name)

    # -------------------------------------------------------------------------
    # COMMON CONSTRAINTS
    # -------------------------------------------------------------------------

    def _invoice_constraints_common(self, invoice):
        # check that there is a tax on each line
        for line in invoice.invoice_line_ids.filtered(lambda x: x.display_type not in ('line_note', 'line_section') and x._check_edi_line_tax_required()):
            if not line.tax_ids:
                return {'tax_on_line': _("Each invoice line should have at least one tax.")}
        return {}

    # -------------------------------------------------------------------------
    # Import invoice
    # -------------------------------------------------------------------------

    def _import_invoice_ubl_cii(self, invoice, file_data, new=False):
        tree = file_data['xml_tree']

        # Not able to decode the move_type from the xml.
        move_type, qty_factor = self._get_import_document_amount_sign(tree)
        if not move_type:
            return

        # Check for inconsistent move_type.
        journal = invoice.journal_id
        if journal.type == 'sale':
            move_type = 'out_' + move_type
        elif journal.type == 'purchase':
            move_type = 'in_' + move_type
        else:
            return
        if not new and invoice.move_type != move_type:
            # with an email alias to create account_move, first the move is created (using alias_defaults, which
            # contains move_type = 'out_invoice') then the attachment is decoded, if it represents a credit note,
            # the move type needs to be changed to 'out_refund'
            types = {move_type, invoice.move_type}
            if types == {'out_invoice', 'out_refund'} or types == {'in_invoice', 'in_refund'}:
                invoice.move_type = move_type
            else:
                return

        # Update the invoice.
        invoice.move_type = move_type
        with invoice._get_edi_creation() as invoice:
            logs = self._import_fill_invoice_form(invoice, tree, qty_factor)
        if invoice:
            body = Markup("<strong>%s</strong>") % \
                _("Format used to import the invoice: %s",
                  self.env['ir.model']._get(self._name).name)

            if logs:
                body += Markup("<ul>%s</ul>") % \
                    Markup().join(Markup("<li>%s</li>") % l for l in logs)

            invoice.message_post(body=body)

        # For UBL, we should override the computed tax amount if it is less than 0.05 different of the one in the xml.
        # In order to support use case where the tax total is adapted for rounding purpose.
        # This has to be done after the first import in order to let Odoo compute the taxes before overriding if needed.
        with invoice._get_edi_creation() as invoice:
            self._correct_invoice_tax_amount(tree, invoice)

        # === Import the embedded PDF in the xml if some are found ===

        attachments = self.env['ir.attachment']
        additional_docs = tree.findall('./{*}AdditionalDocumentReference')
        for document in additional_docs:
            attachment_name = document.find('{*}ID')
            attachment_data = document.find('{*}Attachment/{*}EmbeddedDocumentBinaryObject')
            if attachment_name is not None \
                    and attachment_data is not None \
                    and attachment_data.attrib.get('mimeCode') == 'application/pdf':
                text = attachment_data.text
                # Normalize the name of the file : some e-fff emitters put the full path of the file
                # (Windows or Linux style) and/or the name of the xml instead of the pdf.
                # Get only the filename with a pdf extension.
                name = (attachment_name.text or 'invoice').split('\\')[-1].split('/')[-1].split('.')[0] + '.pdf'
                attachment = self.env['ir.attachment'].create({
                    'name': name,
                    'res_id': invoice.id,
                    'res_model': 'account.move',
                    'datas': text + '=' * (len(text) % 3),  # Fix incorrect padding
                    'type': 'binary',
                    'mimetype': 'application/pdf',
                })
                # Upon receiving an email (containing an xml) with a configured alias to create invoice, the xml is
                # set as the main_attachment. To be rendered in the form view, the pdf should be the main_attachment.
                if invoice.message_main_attachment_id and \
                        invoice.message_main_attachment_id.name.endswith('.xml') and \
                        'pdf' not in invoice.message_main_attachment_id.mimetype:
                    invoice.message_main_attachment_id = attachment
                attachments |= attachment
        if attachments:
            invoice.with_context(no_new_invoice=True).message_post(attachment_ids=attachments.ids)

        return True

    def _import_retrieve_and_fill_partner(self, invoice, name, phone, mail, vat, country_code=False, peppol_eas=False, peppol_endpoint=False, street=False, street2=False, city=False, zip_code=False):
        """ Retrieve the partner, if no matching partner is found, create it (only if he has a vat and a name) """
        if peppol_eas and peppol_endpoint:
            domain = [('peppol_eas', '=', peppol_eas), ('peppol_endpoint', '=', peppol_endpoint)]
        else:
            domain = False
        invoice.partner_id = self.env['res.partner'] \
            .with_company(invoice.company_id) \
            ._retrieve_partner(name=name, phone=phone, mail=mail, vat=vat, domain=domain)
        if not invoice.partner_id and name and vat:
            partner_vals = {'name': name, 'email': mail, 'phone': phone, 'street': street, 'street2': street2, 'zip': zip_code, 'city': city}
            if peppol_eas and peppol_endpoint:
                partner_vals.update({'peppol_eas': peppol_eas, 'peppol_endpoint': peppol_endpoint})
            country = self.env.ref(f'base.{country_code.lower()}', raise_if_not_found=False) if country_code else False
            if country:
                partner_vals['country_id'] = country.id
            invoice.partner_id = self.env['res.partner'].create(partner_vals)
            if vat and self.env['res.partner']._run_vat_test(vat, country, invoice.partner_id.is_company):
                invoice.partner_id.vat = vat

    def _import_retrieve_and_fill_partner_bank_details(self, invoice, bank_details):
        """ Retrieve the bank account, if no matching bank account is found, create it
        """

        # clear the context, because creation of partner when importing should not depend on the context default values
        ResPartnerBank = self.env['res.partner.bank'].with_env(self.env(context=clean_context(self.env.context)))
        bank_details = list(map(sanitize_account_number, bank_details))

        if invoice.move_type in ('out_refund', 'in_invoice'):
            partner = invoice.partner_id
        elif invoice.move_type in ('out_invoice', 'in_refund'):
            partner = self.env.company.partner_id
        else:
            return

        banks_to_create = []
        acc_number_partner_bank_dict = {
            bank.sanitized_acc_number: bank
            for bank in ResPartnerBank.search(
                [('company_id', 'in', [False, invoice.company_id.id]), ('acc_number', 'in', bank_details)]
            )
        }

        for account_number in bank_details:
            partner_bank = acc_number_partner_bank_dict.get(account_number, ResPartnerBank)

            if partner_bank.partner_id == partner:
                invoice.partner_bank_id = partner_bank
                return
            elif not partner_bank and account_number:
                banks_to_create.append({
                    'acc_number': account_number,
                    'partner_id': partner.id,
                })

        if banks_to_create:
            invoice.partner_bank_id = ResPartnerBank.create(banks_to_create)[0]

    def _import_fill_invoice_allowance_charge(self, tree, invoice, qty_factor):
        logs = []
        if '{urn:oasis:names:specification:ubl:schema:xsd' in tree.tag:
            is_ubl = True
        elif '{urn:un:unece:uncefact:data:standard:' in tree.tag:
            is_ubl = False
        else:
            return

        xpath = './{*}AllowanceCharge' if is_ubl else './{*}SupplyChainTradeTransaction/{*}ApplicableHeaderTradeSettlement/{*}SpecifiedTradeAllowanceCharge'
        allowance_charge_nodes = tree.findall(xpath)
        line_vals = []
        for allow_el in allowance_charge_nodes:
            # get the charge factor
            charge_factor = -1  # factor is -1 for discount, 1 for charge
            if is_ubl:
                charge_indicator_node = allow_el.find('./{*}ChargeIndicator')
            else:
                charge_indicator_node = allow_el.find('./{*}ChargeIndicator/{*}Indicator')
            if charge_indicator_node is not None:
                charge_factor = -1 if charge_indicator_node.text == 'false' else 1

            # get the name
            name = ""
            reason_node = allow_el.find('./{*}AllowanceChargeReason' if is_ubl else './{*}Reason')
            if reason_node is not None:
                name = reason_node.text

            # get quantity and price unit
            quantity = 1
            price_unit = 0
            amount_node = allow_el.find('./{*}Amount' if is_ubl else './{*}ActualAmount')
            base_amount_node = allow_el.find('./{*}BaseAmount' if is_ubl else './{*}BasisAmount')
            # Since there is no quantity associated for the allowance/charge on document level,
            # if we have an invoice with negative amounts, the price was multiplied by -1 and not the quantity
            # See the file in test_files: 'base-negative-inv-correction.xml' VS 'base-example.xml' for 'Insurance'
            if base_amount_node is not None:
                price_unit = float(base_amount_node.text) * charge_factor * qty_factor
                percent_node = allow_el.find('./{*}MultiplierFactorNumeric' if is_ubl else './{*}CalculationPercent')
                if percent_node is not None:
                    quantity = float(percent_node.text) / 100
            elif amount_node is not None:
                price_unit = float(amount_node.text) * charge_factor * qty_factor

            # get taxes
            tax_xpath = './{*}TaxCategory/{*}Percent' if is_ubl else './{*}CategoryTradeTax/{*}RateApplicablePercent'
            tax_ids = []
            for tax_categ_percent_el in allow_el.findall(tax_xpath):
                tax = self.env['account.tax'].search([
                    *self.env['account.tax']._check_company_domain(invoice.company_id),
                    ('amount', '=', float(tax_categ_percent_el.text)),
                    ('amount_type', '=', 'percent'),
                    ('type_tax_use', '=', invoice.journal_id.type),  # Journal type is ensured by _create_invoice_from_xml_tree to be either 'sale' or 'purchase'
                ], limit=1)
                if tax:
                    tax_ids += tax.ids
                else:
                    logs.append(
                        _("Could not retrieve the tax: %s %% for line '%s'.",
                            float(tax_categ_percent_el.text),
                            name)
                    )

            line_vals += [Command.create({
                'sequence': 0,  # be sure to put these lines above the 'real' invoice lines
                'name': name,
                'quantity': quantity,
                'price_unit': price_unit,
                'tax_ids': [Command.set(tax_ids)],
            })]

        invoice.write({'invoice_line_ids': line_vals})
        return logs

    def _import_log_prepaid_amount(self, invoice_form, prepaid_node, qty_factor):
        """
        Log a message in the chatter at import if prepaid_node (TotalPrepaidAmount in CII, PrepaidAmount in UBL) exists.
        """
        prepaid_amount = float(prepaid_node.text) if prepaid_node is not None else 0.0
        if not invoice_form.currency_id.is_zero(prepaid_amount):
            amount = prepaid_amount * qty_factor
            formatted_amount = formatLang(self.env, amount, currency_obj=invoice_form.currency_id)
            return [
                _("A payment of %s was detected.", formatted_amount)
            ]
        return []

    def _import_rounding_amount(self, invoice, rounding_node, qty_factor):
        """
        Add an invoice line representing the rounding amount given in the document.
        - The amount is assumed to be in document currency
        """
        currency = invoice.currency_id
        rounding_amount_currency = currency.round(qty_factor * float(rounding_node.text) if rounding_node is not None else 0.0)

        if invoice.currency_id.is_zero(rounding_amount_currency):
            return []

        inverse_rate = abs(invoice.amount_total_signed) / invoice.amount_total if invoice.amount_total else 0
        rounding_amount = invoice.company_id.currency_id.round(rounding_amount_currency * inverse_rate)

        invoice.line_ids.create([{
            'display_type': 'product',
            'name': _('Rounding'),
            'quantity': 1,
            'product_id': False,
            'price_unit': rounding_amount_currency,
            'balance': invoice.direction_sign * rounding_amount,
            'company_id': invoice.company_id.id,
            'move_id': invoice.id,
            'tax_ids': False,
        }])

        formatted_amount = formatLang(self.env, rounding_amount_currency, currency_obj=currency)
        return [
            _("A rounding amount of %s was detected.", formatted_amount),
        ]

    def _import_fill_invoice_line_values(self, tree, xpath_dict, invoice_line, qty_factor):
        """
        Read the xml invoice, extract the invoice line values, compute the odoo values
        to fill an invoice line form: quantity, price_unit, discount, product_uom_id.

        The way of computing invoice line is quite complicated:
        https://docs.peppol.eu/poacc/billing/3.0/bis/#_calculation_on_line_level (same as in factur-x documentation)

        line_net_subtotal = ( gross_unit_price - rebate ) * (billed_qty / basis_qty) - allow_charge_amount

        with (UBL | CII):
            * net_unit_price = 'Price/PriceAmount' | 'NetPriceProductTradePrice' (mandatory) (BT-146)
            * gross_unit_price = 'Price/AllowanceCharge/BaseAmount' | 'GrossPriceProductTradePrice' (optional) (BT-148)
            * basis_qty = 'Price/BaseQuantity' | 'BasisQuantity' (optional, either below net_price node or
                gross_price node) (BT-149)
            * billed_qty = 'InvoicedQuantity' | 'BilledQuantity' (mandatory) (BT-129)
            * allow_charge_amount = sum of 'AllowanceCharge' | 'SpecifiedTradeAllowanceCharge' (same level as Price)
                ON THE LINE level (optional) (BT-136 / BT-141)
            * line_net_subtotal = 'LineExtensionAmount' | 'LineTotalAmount' (mandatory) (BT-131)
            * rebate = 'Price/AllowanceCharge' | 'AppliedTradeAllowanceCharge' below gross_price node ! (BT-147)
                "item price discount" which is different from the usual allow_charge_amount
                gross_unit_price (BT-148) - rebate (BT-147) = net_unit_price (BT-146)

        In Odoo, we obtain:
        (1) = price_unit  =  gross_price_unit / basis_qty  =  (net_price_unit + rebate) / basis_qty
        (2) = quantity  =  billed_qty
        (3) = discount (converted into a percentage)  =  100 * (1 - price_subtotal / (billed_qty * price_unit))
        (4) = price_subtotal

        Alternatively, we could also set: quantity = billed_qty/basis_qty

        WARNING, the basis quantity parameter is annoying, for instance, an invoice with a line:
            item A  | price per unit of measure/unit price: 30  | uom = 3 pieces | billed qty = 3 | rebate = 2  | untaxed total = 28
        Indeed, 30 $ / 3 pieces = 10 $ / piece => 10 * 3 (billed quantity) - 2 (rebate) = 28

        UBL ROUNDING: "the result of Item line net
            amount = ((Item net price (BT-146)÷Item price base quantity (BT-149))×(Invoiced Quantity (BT-129))
        must be rounded to two decimals, and the allowance/charge amounts are also rounded separately."
        It is not possible to do it in Odoo.

        :params tree
        :params xpath_dict dict: {
            'basis_qty': list of str,
            'gross_price_unit': str,
            'rebate': str,
            'net_price_unit': str,
            'billed_qty': str,
            'allowance_charge': str, to be used in a findall !,
            'allowance_charge_indicator': str, relative xpath from allowance_charge,
            'allowance_charge_amount': str, relative xpath from allowance_charge,
            'line_total_amount': str,
        }
        :params: invoice_line
        :params: qty_factor
        :returns: {
            'quantity': float,
            'product_uom_id': (optional) uom.uom,
            'price_unit': float,
            'discount': float,
        }
        """
        # basis_qty (optional)
        basis_qty = 1
        for xpath in xpath_dict['basis_qty']:
            basis_quantity_node = tree.find(xpath)
            if basis_quantity_node is not None:
                basis_qty = float(basis_quantity_node.text) or 1

        # gross_price_unit (optional)
        gross_price_unit = None
        gross_price_unit_node = tree.find(xpath_dict['gross_price_unit'])
        if gross_price_unit_node is not None:
            gross_price_unit = float(gross_price_unit_node.text)

        # rebate (optional)
        # Discount. /!\ as no percent discount can be set on a line, need to infer the percentage
        # from the amount of the actual amount of the discount (the allowance charge)
        rebate = 0
        rebate_node = tree.find(xpath_dict['rebate'])
        net_price_unit_node = tree.find(xpath_dict['net_price_unit'])
        if rebate_node is not None:
            rebate = float(rebate_node.text)
        elif net_price_unit_node is not None and gross_price_unit_node is not None:
            rebate = float(gross_price_unit_node.text) - float(net_price_unit_node.text)

        # net_price_unit (mandatory)
        net_price_unit = None
        if net_price_unit_node is not None:
            net_price_unit = float(net_price_unit_node.text)

        # billed_qty (mandatory)
        billed_qty = 1
        product_uom_id = None
        quantity_node = tree.find(xpath_dict['billed_qty'])
        if quantity_node is not None:
            billed_qty = float(quantity_node.text)
            uom_xml = quantity_node.attrib.get('unitCode')
            if uom_xml:
                uom_infered_xmlid = [
                    odoo_xmlid for odoo_xmlid, uom_unece in UOM_TO_UNECE_CODE.items() if uom_unece == uom_xml
                ]
                if uom_infered_xmlid:
                    product_uom_id = self.env.ref(uom_infered_xmlid[0], raise_if_not_found=False)

        # allow_charge_amount
        fixed_taxes_list = []
        allow_charge_amount = 0  # if positive: it's a discount, if negative: it's a charge
        allow_charge_nodes = tree.findall(xpath_dict['allowance_charge'])
        for allow_charge_el in allow_charge_nodes:
            charge_indicator = allow_charge_el.find(xpath_dict['allowance_charge_indicator'])
            if charge_indicator.text and charge_indicator.text.lower() == 'false':
                discount_factor = 1  # it's a discount
            else:
                discount_factor = -1  # it's a charge
            amount = allow_charge_el.find(xpath_dict['allowance_charge_amount'])
            reason_code = allow_charge_el.find(xpath_dict['allowance_charge_reason_code'])
            reason = allow_charge_el.find(xpath_dict['allowance_charge_reason'])
            if amount is not None:
                if reason_code is not None and reason_code.text == 'AEO' and reason is not None:
                    # Handle Fixed Taxes: when exporting from Odoo, we use the allowance_charge node
                    fixed_taxes_list.append({
                        'tax_name': reason.text,
                        'tax_amount': float(amount.text) / billed_qty,
                    })
                else:
                    allow_charge_amount += float(amount.text) * discount_factor

        # line_net_subtotal (mandatory)
        price_subtotal = None
        line_total_amount_node = tree.find(xpath_dict['line_total_amount'])
        if line_total_amount_node is not None:
            price_subtotal = float(line_total_amount_node.text)

        ####################################################
        # Setting the values on the invoice_line
        ####################################################

        # quantity
        quantity = billed_qty * qty_factor

        # price_unit
        if gross_price_unit is not None:
            price_unit = gross_price_unit / basis_qty
        elif net_price_unit is not None:
            price_unit = (net_price_unit + rebate) / basis_qty
        elif price_subtotal is not None:
            price_unit = (price_subtotal + allow_charge_amount) / (billed_qty or 1)
        else:
            raise UserError(_("No gross price, net price nor line subtotal amount found for line in xml"))

        # discount
        discount = 0
        amount_fixed_taxes = sum(d['tax_amount'] * billed_qty for d in fixed_taxes_list)
        if billed_qty * price_unit != 0 and price_subtotal is not None:
            currency = invoice_line.currency_id or self.env.company.currency_id
            inferred_discount = 100 * (1 - (price_subtotal - amount_fixed_taxes) / currency.round(billed_qty * price_unit))
            discount = inferred_discount if not float_is_zero(inferred_discount, currency.decimal_places) else 0.0

        # Sometimes, the xml received is very bad; e.g.:
        #   * unit price = 0, qty = 0, but price_subtotal = -200
        #   * unit price = 0, qty = 1, but price_subtotal = -200
        #   * unit price = 1, qty = 0, but price_subtotal = -200
        # for instance, when filling a down payment as an invoice line. The equation in the docstring is not
        # respected, and the result will not be correct, so we just follow the simple rule below:
        if net_price_unit is not None and price_subtotal != net_price_unit * (billed_qty / basis_qty) - allow_charge_amount:
            if net_price_unit == 0 and billed_qty == 0:
                quantity = 1
                price_unit = price_subtotal
            elif net_price_unit == 0:
                price_unit = price_subtotal / billed_qty
            elif billed_qty == 0:
                quantity = price_subtotal / price_unit

        return {
            'quantity': quantity,
            'price_unit': price_unit,
            'discount': discount,
            'product_uom_id': product_uom_id,
            'fixed_taxes_list': fixed_taxes_list,
        }

    def _import_retrieve_fixed_tax(self, invoice_line, fixed_tax_vals):
        """ Retrieve the fixed tax at import, iteratively search for a tax:
        1. not price_include matching the name and the amount
        2. not price_include matching the amount
        3. price_include matching the name and the amount
        4. price_include matching the amount
        """
        base_domain = [
            *self.env['account.journal']._check_company_domain(invoice_line.company_id),
            ('amount_type', '=', 'fixed'),
            ('amount', '=', fixed_tax_vals['tax_amount']),
        ]
        for price_include in (False, True):
            for name in (fixed_tax_vals['tax_name'], False):
                domain = base_domain + [('price_include', '=', price_include)]
                if name:
                    domain.append(('name', '=', name))
                tax = self.env['account.tax'].search(domain, limit=1)
                if tax:
                    return tax
        return self.env['account.tax']

    def _import_fill_invoice_line_taxes(self, tax_nodes, invoice_line, inv_line_vals, logs):
        # Taxes: all amounts are tax excluded, so first try to fetch price_include=False taxes,
        # if no results, try to fetch the price_include=True taxes. If results, need to adapt the price_unit.
        inv_line_vals['taxes'] = []
        for tax_node in tax_nodes:
            amount = float(tax_node.text)
            domain = [
                *self.env['account.journal']._check_company_domain(invoice_line.company_id),
                ('amount_type', '=', 'percent'),
                ('type_tax_use', '=', invoice_line.move_id.journal_id.type),
                ('amount', '=', amount),
            ]

            tax = False
            if hasattr(invoice_line, '_predict_specific_tax'):
                # company check is already done in the prediction query
                predicted_tax_id = invoice_line\
                    ._predict_specific_tax('percent', amount, invoice_line.move_id.journal_id.type)
                tax = self.env['account.tax'].browse(predicted_tax_id)
            if not tax:
                tax = self.env['account.tax'].search(domain + [('price_include', '=', False)], limit=1)
            if not tax:
                tax = self.env['account.tax'].search(domain + [('price_include', '=', True)], limit=1)

            if not tax:
                logs.append(_("Could not retrieve the tax: %s %% for line '%s'.", amount, invoice_line.name))
            else:
                inv_line_vals['taxes'].append(tax.id)
                if tax.price_include:
                    inv_line_vals['price_unit'] *= (1 + tax.amount / 100)

        # Handle Fixed Taxes
        for fixed_tax_vals in inv_line_vals['fixed_taxes_list']:
            tax = self._import_retrieve_fixed_tax(invoice_line, fixed_tax_vals)
            if not tax:
                # Nothing found: fix the price_unit s.t. line subtotal is matching the original invoice
                inv_line_vals['price_unit'] += fixed_tax_vals['tax_amount']
            elif tax.price_include:
                inv_line_vals['taxes'].append(tax.id)
                inv_line_vals['price_unit'] += tax.amount
            else:
                inv_line_vals['taxes'].append(tax.id)

        # Set the values on the line_form
        invoice_line.quantity = inv_line_vals['quantity']
        if not inv_line_vals.get('product_uom_id'):
            logs.append(
                _("Could not retrieve the unit of measure for line with label '%s'.", invoice_line.name))
        elif not invoice_line.product_id:
            # no product set on the line, no need to check uom compatibility
            invoice_line.product_uom_id = inv_line_vals['product_uom_id']
        elif inv_line_vals['product_uom_id'].category_id == invoice_line.product_id.product_tmpl_id.uom_id.category_id:
            # needed to check that the uom is compatible with the category of the product
            invoice_line.product_uom_id = inv_line_vals['product_uom_id']

        invoice_line.price_unit = inv_line_vals['price_unit']
        invoice_line.discount = inv_line_vals['discount']
        invoice_line.tax_ids = inv_line_vals['taxes'] or False
        return logs

    def _correct_invoice_tax_amount(self, tree, invoice):
        pass  # To be implemented by the format if needed

    # -------------------------------------------------------------------------
    # Check xml using the free API from Ph. Helger, don't abuse it !
    # -------------------------------------------------------------------------

    def _check_xml_ecosio(self, invoice, xml_content, ecosio_formats):
        # see https://peppol.helger.com/public/locale-en_US/menuitem-validation-ws2
        if not ecosio_formats:
            return
        soap_client = Client('https://peppol.helger.com/wsdvs?wsdl')
        if invoice.move_type == 'out_invoice':
            ecosio_format = ecosio_formats['invoice']
        elif invoice.move_type == 'out_refund':
            ecosio_format = ecosio_formats['credit_note']
        else:
            invoice.message_post(body="ECOSIO: could not validate xml, formats only exist for invoice or credit notes")
            return
        if not ecosio_format:
            return
        response = soap_client.service.validate(xml_content, ecosio_format)

        report = []
        errors_cnt = 0
        for item in response['Result']:
            if item['artifactPath']:
                report.append(
                    Markup("<li><font style='color:Blue;'><strong>%s</strong></font></li>") % item['artifactPath'])
            for detail in item['Item']:
                if detail['errorLevel'] == 'WARN':
                    errors_cnt += 1
                    report.append(
                        Markup("<li><font style='color:Orange;'><strong>%s</strong></font></li>") % detail['errorText'])
                elif detail['errorLevel'] == 'ERROR':
                    errors_cnt += 1
                    report.append(
                        Markup("<li><font style='color:Tomato;'><strong>%s</strong></font></li>") % detail['errorText'])

        if errors_cnt == 0:
            invoice.message_post(body=Markup("<font style='color:Green;'><strong>ECOSIO: All clear for format %s!</strong></font>") % ecosio_format)
        else:
            invoice.message_post(
                body=Markup("<font style='color:Tomato;'><strong>ECOSIO ERRORS/WARNINGS for format %s</strong></font>: <ul>%s</<ul>") % (
                    ecosio_format,
                    Markup().join(report)
                )
            )
        return response
