from odoo import models, fields, api

class AssetCategory(models.Model):
    _name = 'facilities.asset.category'
    _description = 'Asset Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Category Name', required=True, translate=True, tracking=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', 
        recursive=True, store=True)
    description = fields.Text('Description', translate=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    
    # Hierarchical Structure
    parent_id = fields.Many2one(
        'facilities.asset.category', 'Parent Category', 
        index=True, ondelete='cascade', tracking=True)
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(
        'facilities.asset.category', 'parent_id', 'Child Categories')
    
    # Asset Management
    asset_ids = fields.One2many('facilities.asset', 'category_id', string='Assets')
    asset_count = fields.Integer(
        'Assets Count', compute='_compute_asset_count', store=True)
    total_asset_count = fields.Integer(
        'Total Assets (including subcategories)', 
        compute='_compute_total_asset_count')
    
    # Category Properties
    category_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('it', 'IT Hardware'),
        ('building', 'Building Component'),
        ('infrastructure', 'Infrastructure'),
        ('tool', 'Tool'),
        ('other', 'Other')
    ], string='Category Type', default='other', tracking=True)
    
    # Default Asset Properties for this Category
    default_expected_lifespan = fields.Integer(
        'Default Expected Lifespan (Years)', 
        help="Default lifespan for assets in this category")
    default_criticality = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Default Criticality', default='medium')
    
    # Maintenance Defaults
    default_maintenance_interval = fields.Integer(
        'Default Maintenance Interval (Days)', default=90)
    default_inspection_interval = fields.Integer(
        'Default Inspection Interval (Days)', default=365)
    
    # Visual and Organization
    color = fields.Integer('Color', default=0)
    sequence = fields.Integer('Sequence', default=10)
    
    # Financial Tracking
    total_purchase_value = fields.Monetary(
        'Total Purchase Value', compute='_compute_financial_totals',
        currency_field='currency_id')
    total_current_value = fields.Monetary(
        'Total Current Value', compute='_compute_financial_totals',
        currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f'{category.parent_id.complete_name} / {category.name}'
            else:
                category.complete_name = category.name

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for category in self:
            category.asset_count = len(category.asset_ids)

    def _compute_total_asset_count(self):
        for category in self:
            total = category.asset_count
            # Add assets from all child categories
            child_categories = self.search([('parent_path', '=like', f'{category.parent_path}%')])
            for child in child_categories:
                if child != category:
                    total += child.asset_count
            category.total_asset_count = total

    @api.depends('asset_ids.purchase_value', 'asset_ids.current_value')
    def _compute_financial_totals(self):
        for category in self:
            category.total_purchase_value = sum(category.asset_ids.mapped('purchase_value') or [0])
            category.total_current_value = sum(category.asset_ids.mapped('current_value') or [0])

    def action_view_assets(self):
        """Open assets in this category"""
        action = self.env.ref('facilities_management.action_asset').read()[0]
        action['domain'] = [('category_id', '=', self.id)]
        action['context'] = {'default_category_id': self.id}
        return action

    def action_view_all_assets(self):
        """Open all assets in this category and subcategories"""
        category_ids = self.search([('parent_path', '=like', f'{self.parent_path}%')]).ids
        action = self.env.ref('facilities_management.action_asset').read()[0]
        action['domain'] = [('category_id', 'in', category_ids)]
        return action
