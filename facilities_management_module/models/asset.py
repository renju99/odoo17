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
    
    # ESG Compliance Fields
    esg_compliance = fields.Boolean(string='ESG Compliance Required', default=False, tracking=True)
    environmental_impact = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Environmental Impact', tracking=True)
    energy_efficiency_rating = fields.Selection([
        ('a', 'A - Excellent'),
        ('b', 'B - Good'),
        ('c', 'C - Average'),
        ('d', 'D - Poor'),
        ('e', 'E - Very Poor')
    ], string='Energy Efficiency Rating', tracking=True)
    carbon_footprint = fields.Float(string='Carbon Footprint (kg CO2/year)', tracking=True)
    renewable_energy = fields.Boolean(string='Uses Renewable Energy', default=False, tracking=True)
    
    # Social Impact Fields
    safety_compliance = fields.Boolean(string='Safety Compliant', default=True, tracking=True)
    accessibility_compliant = fields.Boolean(string='Accessibility Compliant', default=False, tracking=True)
    social_impact_score = fields.Float(string='Social Impact Score (1-10)', tracking=True)
    
    # Governance Fields
    regulatory_compliance = fields.Boolean(string='Regulatory Compliant', default=True, tracking=True)
    certification_ids = fields.Many2many('asset.certification', string='Certifications', tracking=True)
    audit_date = fields.Date(string='Last Audit Date', tracking=True)
    next_audit_date = fields.Date(string='Next Audit Date', tracking=True)
    compliance_notes = fields.Text(string='Compliance Notes')
    
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
    
    @api.constrains('social_impact_score')
    def _check_social_impact_score(self):
        for record in self:
            if record.social_impact_score and (record.social_impact_score < 1 or record.social_impact_score > 10):
                raise ValidationError(_('Social Impact Score must be between 1 and 10.'))
    
    @api.constrains('carbon_footprint')
    def _check_carbon_footprint(self):
        for record in self:
            if record.carbon_footprint and record.carbon_footprint < 0:
                raise ValidationError(_('Carbon footprint cannot be negative.'))