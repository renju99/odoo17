from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    esg_framework_id = fields.Many2one(
        'esg.framework',
        string='ESG Framework',
        help="ESG framework this purchase order is related to"
    )