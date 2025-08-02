from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import io
from datetime import date, datetime, timedelta
import logging

try:
    import qrcode
except ImportError:
    qrcode = None

_logger = logging.getLogger(__name__)

class FacilityAsset(models.Model):
    _name = 'facilities.asset'
    _description = 'Facility Asset'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, asset_code'

    name = fields.Char('Asset Name', required=True, tracking=True)
    asset_tag = fields.Char(string="Asset Tag", tracking=True)
    serial_number = fields.Char(string="Serial Number", tracking=True)
    location = fields.Char(string="Location", compute='_compute_location')
    facility_id = fields.Many2one('facilities.facility', string='Project', required=True, tracking=True)
    asset_code = fields.Char('Asset Code', size=20, tracking=True, copy=False)

    # Timeline History Events for UI
    history_events = fields.Json(string="Asset History Events", compute='_compute_history_events', store=False)
    history_events_display = fields.Text(string="Asset History Events", compute='_compute_history_events_display', store=False)
    history_events_html = fields.Html(string="Asset History Timeline", compute='_compute_history_events_html', store=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
    ], string='State', default='draft', tracking=True, required=True)

    def action_activate(self):
        for asset in self:
            asset.state = 'active'

    def action_set_maintenance(self):
        for asset in self:
            asset.state = 'maintenance'

    def action_set_active(self):
        for asset in self:
            asset.state = 'active'

    def action_dispose(self):
        for asset in self:
            asset.state = 'disposed'

    # Relationships
    maintenance_ids = fields.One2many('asset.maintenance.schedule', 'asset_id', string='Maintenance Schedules')
    depreciation_ids = fields.One2many('facilities.asset.depreciation', 'asset_id', string='Depreciation Records')
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Documents',
        domain="[('res_model','=','facilities.asset')]"
    )
    category_id = fields.Many2one('facilities.asset.category', string='Category', tracking=True)

    # Dates
    purchase_date = fields.Date('Purchase Date', tracking=True)
    installation_date = fields.Date(string='Installation Date', tracking=True)
    warranty_expiration_date = fields.Date('Warranty Expiration Date', tracking=True)

    # Physical Properties
    condition = fields.Selection(
        [
            ('new', 'New'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        default='good',
        string='Condition',
        tracking=True
    )

    # Location Hierarchy Fields
    room_id = fields.Many2one(
        'facilities.room', string='Room',
        tracking=True
    )
    building_id = fields.Many2one(
        'facilities.building', string='Building',
        compute='_compute_building_floor',
        store=True,
        readonly=False
    )
    floor_id = fields.Many2one(
        'facilities.floor', string='Floor',
        compute='_compute_building_floor',
        store=True,
        readonly=False
    )

    @api.depends('room_id')
    def _compute_building_floor(self):
        for asset in self:
            asset.building_id = asset.room_id.building_id if asset.room_id and asset.room_id.building_id else False
            asset.floor_id = asset.room_id.floor_id if asset.room_id and asset.room_id.floor_id else False

    # People & Organization
    responsible_id = fields.Many2one('res.users', string='Responsible Person', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer', tracking=True)
    service_provider_id = fields.Many2one('res.partner', string='Service Provider', tracking=True)

    # Financial
    purchase_value = fields.Monetary(string='Purchase Value', currency_field='currency_id', tracking=True)
    current_value = fields.Monetary(string='Current Value', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # Technical Details
    model_number = fields.Char(string='Model Number', tracking=True)
    expected_lifespan = fields.Integer(string='Expected Lifespan (Years)', tracking=True)

    # Enhanced Asset Management Fields
    criticality = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Business Criticality', default='medium', tracking=True,
       help="How critical this asset is to business operations")
    
    energy_rating = fields.Selection([
        ('a', 'A - Excellent'),
        ('b', 'B - Good'),
        ('c', 'C - Average'),
        ('d', 'D - Below Average'),
        ('e', 'E - Poor')
    ], string='Energy Efficiency Rating', tracking=True)
    
    environmental_impact = fields.Selection([
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact')
    ], string='Environmental Impact', default='low', tracking=True)
    
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('pending_review', 'Pending Review'),
        ('not_applicable', 'Not Applicable')
    ], string='Compliance Status', default='compliant', tracking=True)
    
    last_inspection_date = fields.Date(string='Last Inspection Date', tracking=True)
    next_inspection_date = fields.Date(string='Next Inspection Date', tracking=True)
    
    # IoT and Smart Asset Fields
    iot_device_id = fields.Char(string='IoT Device ID', help="Connected IoT device identifier")
    sensor_data_url = fields.Char(string='Sensor Data URL', help="URL for real-time sensor data")
    remote_monitoring = fields.Boolean(string='Remote Monitoring Enabled', default=False)
    
    # NEW: Enhanced IoT Integration
    iot_sensors = fields.One2many('facilities.asset.sensor', 'asset_id', string='IoT Sensors')
    sensor_count = fields.Integer(compute='_compute_sensor_count', string='Active Sensors')
    last_sensor_reading = fields.Datetime(string='Last Sensor Reading', help="Timestamp of the most recent sensor data")
    sensor_data_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('minute', 'Every Minute'),
        ('hour', 'Hourly'),
        ('day', 'Daily')
    ], string='Sensor Data Frequency', default='hour')
    
    # NEW: Real-time Condition Monitoring
    temperature = fields.Float(string='Current Temperature (°C)', help="Real-time temperature reading")
    humidity = fields.Float(string='Current Humidity (%)', help="Real-time humidity reading")
    vibration = fields.Float(string='Vibration Level', help="Real-time vibration measurement")
    pressure = fields.Float(string='Pressure Reading', help="Real-time pressure measurement")
    power_consumption = fields.Float(string='Power Consumption (kW)', help="Real-time power consumption")
    runtime_hours = fields.Float(string='Runtime Hours', help="Total runtime hours")
    
    # NEW: Condition-based Triggers
    condition_thresholds = fields.One2many('facilities.asset.threshold', 'asset_id', string='Condition Thresholds')
    alert_enabled = fields.Boolean(string='Enable Alerts', default=True, help="Enable real-time alerts for this asset")
    critical_condition = fields.Boolean(string='Critical Condition', compute='_compute_critical_condition', store=True)
    
    # NEW: Enhanced Barcode & RFID Integration
    barcode = fields.Char('Barcode', copy=False, index=True, tracking=True)
    rfid_tag = fields.Char(string='RFID Tag ID', help="RFID tag identifier for asset tracking")
    qr_code = fields.Char(string='QR Code', help="QR code for mobile scanning")
    nfc_tag = fields.Char(string='NFC Tag ID', help="NFC tag identifier")
    
    # NEW: Mobile Asset Tracking
    last_scan_location = fields.Char(string='Last Scan Location', help="Location where asset was last scanned")
    last_scan_time = fields.Datetime(string='Last Scan Time', help="Timestamp of last mobile scan")
    scanned_by_id = fields.Many2one('res.users', string='Scanned By', help="User who last scanned the asset")
    
    # NEW: Asset Lifecycle Automation
    auto_dispose_on_zero_value = fields.Boolean(string='Auto-dispose on Zero Value', default=False,
                                              help="Automatically dispose asset when depreciation reaches zero")
    disposal_workflow_state = fields.Selection([
        ('none', 'No Disposal'),
        ('pending', 'Disposal Pending'),
        ('approved', 'Disposal Approved'),
        ('in_progress', 'Disposal In Progress'),
        ('completed', 'Disposal Completed')
    ], string='Disposal Workflow State', default='none', tracking=True)
    
    # NEW: Predictive Maintenance Integration
    predictive_maintenance_enabled = fields.Boolean(string='Predictive Maintenance Enabled', default=False)
    ml_model_id = fields.Char(string='ML Model ID', help="Machine learning model identifier for this asset")
    prediction_confidence = fields.Float(string='Prediction Confidence (%)', help="Confidence level of failure prediction")
    next_failure_prediction = fields.Datetime(string='Predicted Next Failure', help="ML-predicted next failure date")
    
    # NEW: Asset Health Scoring
    health_score = fields.Float(string='Asset Health Score', compute='_compute_health_score', store=True)
    health_trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
        ('critical', 'Critical')
    ], string='Health Trend', compute='_compute_health_trend', store=True)
    
    # Asset Location Enhancement
    gps_coordinates = fields.Char(string='GPS Coordinates', help="Latitude,Longitude format")
    floor_plan_location = fields.Char(string='Floor Plan Location', help="X,Y coordinates on floor plan")
    
    # Financial Enhancement
    insurance_value = fields.Monetary(string='Insurance Value', currency_field='currency_id', tracking=True)
    replacement_cost = fields.Monetary(string='Replacement Cost', currency_field='currency_id', tracking=True)
    annual_operating_cost = fields.Monetary(string='Annual Operating Cost', currency_field='currency_id')
    
    # Usage and Performance
    operating_hours_total = fields.Float(string='Total Operating Hours', default=0.0)
    operating_hours_yearly = fields.Float(string='Operating Hours This Year', default=0.0)
    utilization_target = fields.Float(string='Target Utilization (%)', default=80.0)
    actual_utilization = fields.Float(string='Actual Utilization (%)', compute='_compute_utilization')
    
    # Asset Lifecycle Enhancement
    installation_status = fields.Selection([
        ('not_installed', 'Not Installed'),
        ('in_progress', 'Installation In Progress'),
        ('installed', 'Installed'),
        ('commissioned', 'Commissioned'),
        ('decommissioned', 'Decommissioned')
    ], string='Installation Status', default='not_installed', tracking=True)
    
    commissioning_date = fields.Date(string='Commissioning Date', tracking=True)
    decommissioning_date = fields.Date(string='Decommissioning Date', tracking=True)

    # Media & Documentation
    image_1920 = fields.Image("Image")
    notes = fields.Text('Notes')
    active = fields.Boolean('Active', default=True)

    # Barcode System
    barcode = fields.Char('Barcode', copy=False, index=True, tracking=True)
    barcode_image = fields.Image(
        "QR Code Image",
        compute='_compute_barcode_image',
        store=True,
        attachment=True,
        max_width=256,
        max_height=256
    )

    warranty_status = fields.Selection(
        [
            ('valid', 'Valid'),
            ('expired', 'Expired'),
            ('none', 'No Warranty')
        ],
        string='Warranty Status',
        compute='_compute_warranty_status',
        store=True,
        tracking=True
    )

    maintenance_due = fields.Boolean(
        string='Maintenance Due',
        compute='_compute_maintenance_due',
        store=True
    )

    is_enterprise = fields.Boolean(
        string="Enterprise Mode",
        compute='_compute_is_enterprise',
        help="Technical field to check if enterprise features are available"
    )

    @api.depends('warranty_expiration_date')
    def _compute_warranty_status(self):
        today = fields.Date.today()
        for asset in self:
            if not asset.warranty_expiration_date:
                asset.warranty_status = 'none'
            elif asset.warranty_expiration_date >= today:
                asset.warranty_status = 'valid'
            else:
                asset.warranty_status = 'expired'

    @api.depends('maintenance_ids.next_maintenance_date')
    def _compute_maintenance_due(self):
        today = fields.Date.today()
        for asset in self:
            due_maintenances = asset.maintenance_ids.filtered(
                lambda m: m.active and m.next_maintenance_date and m.next_maintenance_date <= today
            )
            asset.maintenance_due = bool(due_maintenances)

    def _compute_is_enterprise(self):
        enterprise_installed = self.env['ir.module.module'].search_count([
            ('name', '=', 'web_enterprise'),
            ('state', '=', 'installed')
        ])
        for asset in self:
            asset.is_enterprise = enterprise_installed

    @api.depends('barcode')
    def _compute_barcode_image(self):
        for asset in self:
            if asset.barcode and qrcode:
                try:
                    qr = qrcode.QRCode(version=1, box_size=4, border=1)
                    qr.add_data(asset.barcode)
                    qr.make(fit=True)
                    img = qr.make_image()

                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue())
                    asset.barcode_image = img_str
                except Exception:
                    asset.barcode_image = False
            else:
                asset.barcode_image = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('asset_code'):
                vals['asset_code'] = self.env['ir.sequence'].next_by_code('facilities.asset') or 'AS0000'
            if not vals.get('barcode'):
                vals['barcode'] = self.env['ir.sequence'].next_by_code('facilities.asset.barcode') or 'AS0000'
        return super().create(vals_list)

    def name_get(self):
        return [(record.id, f"{record.name} [{record.asset_code}]") for record in self]

    def action_open_dashboard(self):
        self.ensure_one()
        if self.is_enterprise:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Asset Dashboard (Enterprise)',
                'res_model': 'facilities.asset',
                'view_mode': 'dashboard',
                'views': [(False, 'dashboard')],
                'target': 'current',
                'context': dict(self.env.context),
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Asset Dashboard (Community)',
                'res_model': 'facilities.asset',
                'view_mode': 'kanban,graph,pivot',
                'views': [(False, 'kanban'), (False, 'graph'), (False, 'pivot')],
                'target': 'current',
                'context': dict(self.env.context),
            }

    @api.depends('maintenance_ids', 'depreciation_ids')
    def _compute_history_events(self):
        for asset in self:
            events = []
            # Maintenance events (EXCLUDE preventive work orders)
            for maint in asset.maintenance_ids:
                # If maintenance schedule links to a workorder, and that workorder is NOT preventive, include it
                if hasattr(maint, 'workorder_ids') and maint.workorder_ids:
                    for workorder in maint.workorder_ids:
                        if getattr(workorder, 'work_order_type', None) != 'preventive' and maint.last_maintenance_date:
                            events.append({
                                'date': str(maint.last_maintenance_date),
                                'type': 'maintenance',
                                'name': maint.name,
                                'notes': maint.notes,
                                'details': f"Type: {maint.maintenance_type} ({workorder.work_order_type})"
                            })
                else:
                    # If no workorder connection, just append (legacy)
                    if getattr(maint, 'maintenance_type', None) != 'preventive' and maint.last_maintenance_date:
                        events.append({
                            'date': str(maint.last_maintenance_date),
                            'type': 'maintenance',
                            'name': maint.name,
                            'notes': maint.notes,
                            'details': f"Type: {maint.maintenance_type}"
                        })
            # Depreciation events
            for dep in asset.depreciation_ids:
                events.append({
                    'date': str(dep.depreciation_date),
                    'type': 'depreciation',
                    'name': 'Depreciation',
                    'notes': f"Amount: {dep.depreciation_amount}",
                    'details': f"Value After: {dep.value_after}"
                })
            # Movement events (Stock Picking)
            pickings = self.env['stock.picking'].search([('workorder_id.asset_id', '=', asset.id)])
            for picking in pickings:
                if picking.scheduled_date:
                    events.append({
                        'date': str(picking.scheduled_date),
                        'type': 'movement',
                        'name': picking.name,
                        'notes': f"Transferred: {picking.origin}",
                        'details': f"State: {picking.state}"
                    })
            asset.history_events = sorted(events, key=lambda e: e['date'], reverse=True)

    @api.depends('history_events')
    def _compute_history_events_html(self):
        for asset in self:
            html = "<div class='o_asset_timeline'>"
            for event in asset.history_events or []:
                color = {
                    "maintenance": "#28a745",
                    "depreciation": "#ffc107",
                    "movement": "#17a2b8"
                }.get(event.get("type"), "#007bff")
                html += f"""
                    <div class="o_timeline_event" style="margin-bottom:1em; padding-left:1.5em; position:relative;">
                        <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:{color}; position:absolute; left:0; top:0.5em;"></span>
                        <strong>{event.get('date', '')}</strong>
                        <span class="badge" style="background:{color}; color:white; margin-left:0.5em;">{event.get('type', '').capitalize()}</span>
                        <div><b>{event.get('name', '')}</b></div>
                        <div>{event.get('notes', '')}</div>
                        <div style="color:#6c757d; font-size:0.85em;">{event.get('details', '')}</div>
                    </div>
                """
            if not (asset.history_events or []):
                html += "<span>No history yet.</span>"
            html += "</div>"
            asset.history_events_html = html

    @api.depends('room_id', 'floor_id', 'building_id')
    def _compute_location(self):
        for asset in self:
            vals = []
            if asset.room_id:
                vals.append(asset.room_id.name)
            if asset.floor_id:
                vals.append(f"Floor {asset.floor_id.name}")
            if asset.building_id:
                vals.append(f"Building {asset.building_id.name}")
            asset.location = ", ".join(vals) if vals else ""

    @api.depends('operating_hours_yearly', 'utilization_target')
    def _compute_utilization(self):
        for asset in self:
            if asset.utilization_target > 0:
                # Assuming 8760 hours per year (365 * 24)
                max_hours = 8760
                target_hours = (asset.utilization_target / 100) * max_hours
                if target_hours > 0:
                    asset.actual_utilization = min(100, (asset.operating_hours_yearly / target_hours) * 100)
                else:
                    asset.actual_utilization = 0.0
            else:
                asset.actual_utilization = 0.0

    # NEW: IoT and Condition Monitoring Computed Methods
    @api.depends('iot_sensors')
    def _compute_sensor_count(self):
        for asset in self:
            asset.sensor_count = len(asset.iot_sensors.filtered(lambda s: s.active))

    @api.depends('temperature', 'humidity', 'vibration', 'pressure', 'condition_thresholds')
    def _compute_critical_condition(self):
        for asset in self:
            critical = False
            for threshold in asset.condition_thresholds:
                if threshold.is_exceeded:
                    critical = True
                    break
            asset.critical_condition = critical

    @api.depends('condition', 'compliance_status', 'warranty_status', 'actual_utilization', 'maintenance_due', 'critical_condition')
    def _compute_health_score(self):
        for asset in self:
            score = 100.0
            
            # Condition impact
            condition_scores = {
                'new': 100,
                'good': 85,
                'fair': 60,
                'poor': 30
            }
            score *= condition_scores.get(asset.condition, 50) / 100
            
            # Compliance impact
            if asset.compliance_status == 'non_compliant':
                score *= 0.7
            
            # Warranty impact
            if asset.warranty_status == 'expired':
                score *= 0.9
            
            # Utilization impact
            if asset.actual_utilization > 95:
                score *= 0.8  # Over-utilization penalty
            
            # Maintenance impact
            if asset.maintenance_due:
                score *= 0.6
            
            # Critical condition impact
            if asset.critical_condition:
                score *= 0.5
            
            asset.health_score = max(0, min(100, score))

    @api.depends('health_score', 'maintenance_cost_ytd')
    def _compute_health_trend(self):
        for asset in self:
            if asset.health_score >= 80:
                asset.health_trend = 'improving'
            elif asset.health_score >= 60:
                asset.health_trend = 'stable'
            elif asset.health_score >= 40:
                asset.health_trend = 'declining'
            else:
                asset.health_trend = 'critical'

    # NEW: Asset Lifecycle Automation Methods
    def action_scan_asset(self):
        """Mobile action to scan asset barcode/RFID"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scan Asset',
            'res_model': 'facilities.asset.scan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_asset_id': self.id},
        }

    def action_view_sensor_data(self):
        """View real-time sensor data for the asset"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sensor Data',
            'res_model': 'facilities.asset.sensor',
            'view_mode': 'tree,form',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }

    def action_trigger_maintenance(self):
        """Automatically trigger maintenance based on condition"""
        self.ensure_one()
        if self.critical_condition:
            # Create emergency maintenance work order
            workorder_vals = {
                'name': f"Emergency Maintenance - {self.name}",
                'asset_id': self.id,
                'work_order_type': 'corrective',
                'priority': '3',  # High priority
                'description': f"Automatically triggered due to critical condition on {self.name}",
                'status': 'draft'
            }
            self.env['maintenance.workorder'].create(workorder_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Maintenance Triggered',
                    'message': f'Emergency maintenance work order created for {self.name}',
                    'type': 'warning'
                }
            }
        return True

    def action_dispose_asset(self):
        """Initiate asset disposal workflow"""
        self.ensure_one()
        if self.current_value <= 0 and self.auto_dispose_on_zero_value:
            self.disposal_workflow_state = 'pending'
            # Create disposal approval request
            return {
                'type': 'ir.actions.act_window',
                'name': 'Asset Disposal',
                'res_model': 'facilities.asset.disposal.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_asset_id': self.id},
            }
        return True

    # ESG (Environmental, Social, Governance) Fields
    esg_compliance = fields.Boolean(string='ESG Compliant', default=True, tracking=True,
                                   help="Indicates if this asset meets ESG compliance standards")
    carbon_footprint = fields.Float(string='Carbon Footprint (kg CO2)', tracking=True,
                                   help="Estimated carbon footprint of this asset")
    energy_efficiency_rating = fields.Selection([
        ('a', 'A - Excellent'),
        ('b', 'B - Good'),
        ('c', 'C - Average'),
        ('d', 'D - Below Average'),
        ('e', 'E - Poor')
    ], string='Energy Efficiency Rating', tracking=True)
    renewable_energy_usage = fields.Float(string='Renewable Energy Usage (%)', tracking=True,
                                        help="Percentage of energy from renewable sources")
    waste_management_score = fields.Float(string='Waste Management Score', tracking=True,
                                        help="Score indicating waste management effectiveness")
    water_consumption = fields.Float(string='Water Consumption (L/day)', tracking=True,
                                   help="Daily water consumption of this asset")
    biodiversity_impact = fields.Selection([
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact')
    ], string='Biodiversity Impact', default='low', tracking=True)
    
    # Social Metrics
    community_impact_score = fields.Float(string='Community Impact Score', tracking=True,
                                        help="Score indicating positive community impact")
    employee_satisfaction = fields.Float(string='Employee Satisfaction Score', tracking=True,
                                       help="Employee satisfaction rating for this asset")
    diversity_index = fields.Float(string='Diversity Index', tracking=True,
                                 help="Diversity and inclusion metric")
    health_safety_score = fields.Float(string='Health & Safety Score', tracking=True,
                                     help="Health and safety performance score")
    training_hours = fields.Float(string='Training Hours', tracking=True,
                                help="Annual training hours provided")
    local_procurement = fields.Float(string='Local Procurement (%)', tracking=True,
                                   help="Percentage of procurement from local suppliers")
    
    # Governance Metrics
    compliance_rate = fields.Float(string='Compliance Rate (%)', tracking=True,
                                 help="Overall compliance rate for this asset")
    risk_management_score = fields.Float(string='Risk Management Score', tracking=True,
                                       help="Risk management effectiveness score")
    transparency_index = fields.Float(string='Transparency Index', tracking=True,
                                    help="Transparency and reporting score")
    board_diversity = fields.Float(string='Board Diversity Score', tracking=True,
                                 help="Board diversity and inclusion score")
    ethics_score = fields.Float(string='Ethics Score', tracking=True,
                              help="Ethical business practices score")
    stakeholder_engagement = fields.Float(string='Stakeholder Engagement Score', tracking=True,
                                        help="Stakeholder engagement effectiveness")
    
    # Enhanced Asset Status and Risk Assessment
    risk_score = fields.Float(string='Risk Score', compute='_compute_risk_score', store=True)
    maintenance_cost_ytd = fields.Monetary(string='Maintenance Cost YTD', 
                                          compute='_compute_maintenance_cost', 
                                          currency_field='currency_id')
    total_cost_of_ownership = fields.Monetary(string='Total Cost of Ownership',
                                             compute='_compute_total_cost_ownership',
                                             currency_field='currency_id')
    
    asset_health_score = fields.Float(string='Asset Health Score', 
                                     compute='_compute_health_score', store=True,
                                     help='Asset health score as a decimal (0.0-1.0 representing 0%-100%)')
    
    @api.depends('criticality', 'condition', 'compliance_status', 'warranty_status', 'maintenance_due')
    def _compute_risk_score(self):
        """Calculate risk score based on multiple factors"""
        for asset in self:
            score = 0
            
            # Criticality weight (0-40 points)
            criticality_scores = {'low': 10, 'medium': 20, 'high': 30, 'critical': 40}
            score += criticality_scores.get(asset.criticality, 20)
            
            # Condition weight (0-30 points)
            condition_scores = {'new': 5, 'good': 10, 'fair': 20, 'poor': 30}
            score += condition_scores.get(asset.condition, 15)
            
            # Compliance weight (0-20 points)
            compliance_scores = {'compliant': 0, 'pending_review': 10, 'non_compliant': 20, 'not_applicable': 0}
            score += compliance_scores.get(asset.compliance_status, 0)
            
            # Warranty status weight (0-10 points)
            warranty_scores = {'valid': 0, 'none': 5, 'expired': 10}
            score += warranty_scores.get(asset.warranty_status, 5)
            
            asset.risk_score = min(100, score)

    def _compute_maintenance_cost(self):
        """Calculate maintenance cost for current year"""
        current_year = fields.Date.today().year
        for asset in self:
            # Get maintenance costs from work orders or maintenance records
            maintenance_cost = 0.0
            if hasattr(self.env, 'maintenance.workorder'):
                workorders = self.env['maintenance.workorder'].search([
                    ('asset_id', '=', asset.id),
                    ('start_date', '>=', f'{current_year}-01-01'),
                    ('start_date', '<=', f'{current_year}-12-31')
                ])
                maintenance_cost = sum(workorders.mapped('cost')) if workorders else 0.0
            asset.maintenance_cost_ytd = maintenance_cost

    @api.depends('purchase_value', 'maintenance_cost_ytd', 'annual_operating_cost')
    def _compute_total_cost_ownership(self):
        """Calculate total cost of ownership"""
        for asset in self:
            years_owned = 1
            if asset.purchase_date:
                years_owned = max(1, (fields.Date.today() - asset.purchase_date).days / 365.25)
            
            total_maintenance = asset.maintenance_cost_ytd * years_owned
            total_operating = asset.annual_operating_cost * years_owned
            
            asset.total_cost_of_ownership = (asset.purchase_value or 0) + total_maintenance + total_operating

    @api.model
    def _update_health_scores(self):
        """Cron job method to update asset health scores"""
        assets = self.search([('active', '=', True)])
        
        updated_count = 0
        for asset in assets:
            try:
                # Trigger recomputation of health score
                asset._compute_health_score()
                asset._compute_health_trend()
                updated_count += 1
                
            except Exception as e:
                _logger.error(f"Error updating health score for asset {asset.name}: {str(e)}")
                continue
        
        _logger.info(f"Updated health scores for {updated_count} assets")
        return updated_count

    @api.model
    def _run_predictive_analysis(self):
        """Cron job method to run predictive maintenance analysis"""
        assets = self.search([
            ('active', '=', True),
            ('predictive_maintenance_enabled', '=', True)
        ])
        
        analyzed_count = 0
        for asset in assets:
            try:
                # Simulate predictive analysis (in real implementation, this would call ML models)
                import random
                
                # Generate a random prediction confidence
                confidence = random.uniform(60, 95)
                asset.prediction_confidence = confidence
                
                # Simulate next failure prediction (within next 30 days)
                from datetime import timedelta
                days_to_failure = random.randint(1, 30)
                next_failure = fields.Datetime.now() + timedelta(days=days_to_failure)
                asset.next_failure_prediction = next_failure
                
                # If confidence is high and failure is predicted soon, create preventive work order
                if confidence > 80 and days_to_failure <= 7:
                    workorder_vals = {
                        'name': f"Predictive Maintenance - {asset.name}",
                        'asset_id': asset.id,
                        'work_order_type': 'predictive',
                        'priority': '3',  # High priority
                        'description': f"Predictive maintenance triggered for {asset.name}. "
                                     f"Failure predicted in {days_to_failure} days with {confidence:.1f}% confidence.",
                        'status': 'draft'
                    }
                    self.env['maintenance.workorder'].create(workorder_vals)
                
                analyzed_count += 1
                
            except Exception as e:
                _logger.error(f"Error running predictive analysis for asset {asset.name}: {str(e)}")
                continue
        
        _logger.info(f"Predictive analysis completed for {analyzed_count} assets")
        return analyzed_count

    @api.model
    def _check_disposal_candidates(self):
        """Cron job method to check for assets that should be disposed"""
        today = fields.Date.today()
        
        # Find assets that meet disposal criteria
        disposal_candidates = self.search([
            ('active', '=', True),
            ('state', '!=', 'disposed'),
            '|',
            ('current_value', '<=', 0),
            ('health_score', '<', 20),
            ('warranty_status', '=', 'expired'),
            ('condition', '=', 'poor')
        ])
        
        disposed_count = 0
        for asset in disposal_candidates:
            try:
                # Check if asset meets multiple disposal criteria
                disposal_score = 0
                
                if asset.current_value <= 0:
                    disposal_score += 30
                if asset.health_score < 20:
                    disposal_score += 25
                if asset.warranty_status == 'expired':
                    disposal_score += 20
                if asset.condition == 'poor':
                    disposal_score += 25
                
                # If disposal score is high enough, mark for disposal
                if disposal_score >= 50:
                    asset.disposal_workflow_state = 'pending'
                    asset.message_post(
                        body=_("Asset marked for disposal due to poor condition, "
                              "expired warranty, or zero value. Disposal score: %s") % disposal_score
                    )
                    disposed_count += 1
                
            except Exception as e:
                _logger.error(f"Error checking disposal for asset {asset.name}: {str(e)}")
                continue
        
        _logger.info(f"Disposal check completed. {disposed_count} assets marked for disposal")
        return disposed_count