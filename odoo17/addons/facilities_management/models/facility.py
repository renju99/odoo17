# models/facility.py
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Facility(models.Model):
    _name = 'facilities.facility'
    _description = 'Facility Management'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = 'parent_facility_id'

    # Basic Information
    name = fields.Char(string='Facility Name', required=True, help="The official name of the facility or property.")
    code = fields.Char(string='Facility Code', required=True, copy=False, readonly=True, default='New', help="Unique identifier for the facility, often auto-generated.")
    manager_id = fields.Many2one('hr.employee', string='Facility Manager', tracking=True, help="The employee responsible for managing this facility.")
    active = fields.Boolean(string='Active', default=True, help="Set to false to archive the facility.")

    # Enhanced Location Details with Google Maps Integration
    address = fields.Char(string='Address', help="Street address of the facility.")
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip_code = fields.Char(string='Zip Code')
    country_id = fields.Many2one('res.country', string='Country')
    latitude = fields.Float(string='Latitude', digits=(10, 7), help="Geographical latitude coordinate.")
    longitude = fields.Float(string='Longitude', digits=(10, 7), help="Geographical longitude coordinate.")
    map_link = fields.Char(string='Map Link', help="Link to a map service (e.g., Google Maps) for the facility location.")
    
    # NEW: Enhanced Geo-location Support
    google_maps_embed_url = fields.Html(string='Google Maps Embed', compute='_compute_google_maps_url', store=True)
    location_accuracy = fields.Selection([
        ('exact', 'Exact'),
        ('approximate', 'Approximate'),
        ('estimated', 'Estimated')
    ], string='Location Accuracy', default='exact', help="Accuracy level of the GPS coordinates")
    
    # NEW: Hierarchy Navigation Support
    parent_facility_id = fields.Many2one('facilities.facility', string='Parent Facility', 
                                       help="Parent facility in the hierarchy (e.g., main campus)")
    child_facility_ids = fields.One2many('facilities.facility', 'parent_facility_id', string='Child Facilities')
    facility_level = fields.Integer(string='Hierarchy Level', compute='_compute_facility_level', store=True, recursive=True)
    full_hierarchy_path = fields.Char(string='Full Hierarchy Path', compute='_compute_hierarchy_path', store=True, recursive=True)
    
    # NEW: Bulk Import/Export Support
    import_batch_id = fields.Char(string='Import Batch ID', help="Batch identifier for bulk import operations")
    last_import_date = fields.Datetime(string='Last Import Date', help="Date of last bulk import")
    import_source = fields.Selection([
        ('csv', 'CSV Import'),
        ('xls', 'Excel Import'),
        ('api', 'API Import'),
        ('manual', 'Manual Entry')
    ], string='Import Source', default='manual')

    # Property Details
    property_type = fields.Selection([
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
        ('industrial', 'Industrial'),
        ('retail', 'Retail'),
        ('mixed_use', 'Mixed-Use'),
        ('other', 'Other'),
    ], string='Property Type', default='commercial', help="Categorization of the property.")
    area_sqm = fields.Float(string='Area (sqm)', digits=(10, 2), help="Total area of the facility in square meters.")
    number_of_floors = fields.Integer(string='Number of Floors', help="Total number of floors in the building.")
    year_built = fields.Integer(string='Year Built', help="The year the facility was constructed.")
    last_renovation_date = fields.Date(string='Last Renovation Date', help="Date of the last major renovation.")
    occupancy_status = fields.Selection([
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant'),
        ('under_renovation', 'Under Renovation'),
    ], string='Occupancy Status', default='occupied', help="Current occupancy status of the facility.")
    capacity = fields.Integer(string='Capacity', help="Maximum occupancy or functional capacity of the facility.")

    # Contact & Access Information
    contact_person_id = fields.Many2one('res.partner', string='Primary Contact Person', help="Main contact person associated with this facility (e.g., owner, key tenant).")
    phone = fields.Char(string='Phone Number', help="Primary phone number for the facility.")
    email = fields.Char(string='Email Address', help="Primary email address for the facility.")
    access_instructions = fields.Text(string='Access Instructions', help="Detailed instructions for accessing the facility, e.g., gate codes, key locations.")

    # Utility & Services Information
    electricity_meter_id = fields.Char(string='Electricity Meter ID', help="Identifier for the electricity meter.")
    water_meter_id = fields.Char(string='Water Meter ID', help="Identifier for the water meter.")
    gas_meter_id = fields.Char(string='Gas Meter ID', help="Identifier for the gas meter.")
    internet_provider = fields.Char(string='Internet Provider', help="Main internet service provider.")
    security_system_type = fields.Char(string='Security System Type', help="Description of the security system installed.")

    # Compliance & Documentation
    permit_numbers = fields.Char(string='Permit Numbers', help="Relevant building permits or licenses.")
    inspection_due_date = fields.Date(string='Next Inspection Due Date', help="Date when the next regulatory inspection is due.")
    notes = fields.Text(string='Internal Notes', help="Any additional internal notes or remarks about the facility.")
    documents_ids = fields.Many2many('ir.attachment', string='Facility Documents',
                                    domain="[('res_model','=','facilities.facility')]", help="Attached documents related to the facility (e.g., blueprints, floor plans, certificates).")

    # One2many relationship to Buildings
    building_ids = fields.One2many('facilities.building', 'facility_id', string='Buildings', help="List of buildings associated with this facility.")
    building_count = fields.Integer(compute='_compute_building_count', string='Number of Buildings', store=True)

    @api.depends('building_ids')
    def _compute_building_count(self):
        for rec in self:
            rec.building_count = len(rec.building_ids)

    @api.depends('latitude', 'longitude')
    def _compute_google_maps_url(self):
        for facility in self:
            if facility.latitude and facility.longitude:
                embed_url = f"https://www.google.com/maps/embed/v1/view?key=YOUR_API_KEY&center={facility.latitude},{facility.longitude}&zoom=15"
                facility.google_maps_embed_url = f'''
                <iframe src="{embed_url}" 
                        width="100%" height="400" frameborder="0" 
                        style="border:0;" allowfullscreen="" 
                        loading="lazy" referrerpolicy="no-referrer-when-downgrade">
                </iframe>
                '''
            else:
                facility.google_maps_embed_url = False

    @api.depends('parent_facility_id', 'parent_facility_id.facility_level')
    def _compute_facility_level(self):
        for facility in self:
            if facility.parent_facility_id:
                facility.facility_level = facility.parent_facility_id.facility_level + 1
            else:
                facility.facility_level = 0

    @api.depends('name', 'parent_facility_id', 'parent_facility_id.full_hierarchy_path')
    def _compute_hierarchy_path(self):
        for facility in self:
            if facility.parent_facility_id and facility.parent_facility_id.full_hierarchy_path:
                facility.full_hierarchy_path = f"{facility.parent_facility_id.full_hierarchy_path} > {facility.name}"
            else:
                facility.full_hierarchy_path = facility.name

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('facilities.facility') or 'New'
        
        return super(Facility, self).create(vals_list)

    def action_view_hierarchy(self):
        """Action to view the facility hierarchy in a tree view"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facility Hierarchy',
            'res_model': 'facilities.facility',
            'view_mode': 'tree,form',
            'domain': [('id', 'child_of', self.id)],
            'context': {'default_parent_facility_id': self.id},
        }

    def action_export_facilities_csv(self):
        """Export facilities data to CSV format"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/facilities/export/csv?facility_ids={",".join(str(x) for x in self.ids)}',
            'target': 'self',
        }

    def action_import_facilities_csv(self):
        """Import facilities data from CSV format"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Facilities',
            'res_model': 'facilities.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_facility_ids': self.ids},
        }