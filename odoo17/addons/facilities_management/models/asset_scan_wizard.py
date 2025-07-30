# models/asset_scan_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AssetScanWizard(models.TransientModel):
    _name = 'facilities.asset.scan.wizard'
    _description = 'Asset Scanning Wizard'

    asset_id = fields.Many2one('facilities.asset', string='Asset', required=True)
    scan_type = fields.Selection([
        ('barcode', 'Barcode'),
        ('qr_code', 'QR Code'),
        ('rfid', 'RFID'),
        ('nfc', 'NFC'),
        ('manual', 'Manual Entry')
    ], string='Scan Type', default='barcode', required=True)
    
    scanned_code = fields.Char(string='Scanned Code', help="Enter or scan the asset code")
    scan_location = fields.Char(string='Scan Location', help="Location where the scan occurred")
    scan_notes = fields.Text(string='Scan Notes', help="Additional notes about the scan")
    
    # Asset Information (read-only)
    asset_name = fields.Char(string='Asset Name', related='asset_id.name', readonly=True)
    asset_code = fields.Char(string='Asset Code', related='asset_id.asset_code', readonly=True)
    asset_location = fields.Char(string='Asset Location', related='asset_id.location', readonly=True)
    asset_status = fields.Selection(string='Asset Status', related='asset_id.state', readonly=True)
    
    # Quick Actions
    action_type = fields.Selection([
        ('location_update', 'Update Location'),
        ('status_update', 'Update Status'),
        ('maintenance_check', 'Check Maintenance'),
        ('sensor_reading', 'Record Sensor Reading'),
        ('inspection', 'Quick Inspection'),
        ('none', 'No Action')
    ], string='Action Type', default='none')
    
    # Location Update
    new_location = fields.Char(string='New Location')
    new_room_id = fields.Many2one('facilities.room', string='New Room')
    new_building_id = fields.Many2one('facilities.building', string='New Building')
    new_floor_id = fields.Many2one('facilities.floor', string='New Floor')
    
    # Status Update
    new_status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
    ], string='New Status')
    
    # Sensor Reading
    sensor_reading_value = fields.Float(string='Sensor Reading')
    sensor_reading_unit = fields.Char(string='Unit')
    sensor_reading_notes = fields.Text(string='Reading Notes')
    
    # Inspection
    inspection_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional'),
        ('pending', 'Pending')
    ], string='Inspection Result')
    inspection_notes = fields.Text(string='Inspection Notes')
    
    def action_scan_asset(self):
        """Process the asset scan"""
        self.ensure_one()
        
        if not self.scanned_code:
            raise UserError(_("Please enter or scan a code first."))
        
        # Validate scanned code matches asset
        if self.scanned_code != self.asset_id.barcode and self.scanned_code != self.asset_id.asset_code:
            raise UserError(_("Scanned code does not match the selected asset."))
        
        # Update asset scan tracking
        self.asset_id.write({
            'last_scan_location': self.scan_location or 'Unknown',
            'last_scan_time': fields.Datetime.now(),
            'scanned_by_id': self.env.uid
        })
        
        # Execute action based on type
        if self.action_type == 'location_update':
            return self._update_location()
        elif self.action_type == 'status_update':
            return self._update_status()
        elif self.action_type == 'maintenance_check':
            return self._check_maintenance()
        elif self.action_type == 'sensor_reading':
            return self._record_sensor_reading()
        elif self.action_type == 'inspection':
            return self._record_inspection()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Asset Scanned',
                'message': f'Asset {self.asset_id.name} scanned successfully at {self.scan_location or "unknown location"}',
                'type': 'success'
            }
        }
    
    def _update_location(self):
        """Update asset location"""
        update_vals = {}
        
        if self.new_location:
            update_vals['location'] = self.new_location
        
        if self.new_room_id:
            update_vals['room_id'] = self.new_room_id.id
        
        if self.new_building_id:
            update_vals['building_id'] = self.new_building_id.id
        
        if self.new_floor_id:
            update_vals['floor_id'] = self.new_floor_id.id
        
        if update_vals:
            self.asset_id.write(update_vals)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Location Updated',
                    'message': f'Asset {self.asset_id.name} location updated successfully',
                    'type': 'success'
                }
            }
        
        return True
    
    def _update_status(self):
        """Update asset status"""
        if self.new_status:
            self.asset_id.write({'state': self.new_status})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Status Updated',
                    'message': f'Asset {self.asset_id.name} status updated to {self.new_status}',
                    'type': 'success'
                }
            }
        
        return True
    
    def _check_maintenance(self):
        """Check maintenance status and create work order if needed"""
        if self.asset_id.maintenance_due:
            # Create maintenance work order
            workorder_vals = {
                'name': f"Mobile Scan Maintenance - {self.asset_id.name}",
                'asset_id': self.asset_id.id,
                'work_order_type': 'corrective',
                'priority': '2',
                'description': f"Maintenance required for {self.asset_id.name}. Scanned at {self.scan_location}",
                'status': 'draft'
            }
            
            workorder = self.env['maintenance.workorder'].create(workorder_vals)
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Maintenance Work Order',
                'res_model': 'maintenance.workorder',
                'view_mode': 'form',
                'res_id': workorder.id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Maintenance Check',
                    'message': f'Asset {self.asset_id.name} is up to date on maintenance',
                    'type': 'info'
                }
            }
    
    def _record_sensor_reading(self):
        """Record a manual sensor reading"""
        if self.sensor_reading_value is False:
            raise UserError(_("Please enter a sensor reading value."))
        
        # Find or create a sensor for this asset
        sensor = self.env['facilities.asset.sensor'].search([
            ('asset_id', '=', self.asset_id.id),
            ('sensor_type', '=', 'custom')
        ], limit=1)
        
        if not sensor:
            # Create a custom sensor
            sensor = self.env['facilities.asset.sensor'].create({
                'name': f"Mobile Sensor - {self.asset_id.name}",
                'asset_id': self.asset_id.id,
                'sensor_type': 'custom',
                'sensor_id': f"MOBILE_{self.asset_id.id}",
                'unit': self.sensor_reading_unit or 'units',
                'current_value': self.sensor_reading_value
            })
        else:
            # Update existing sensor
            sensor.write({
                'current_value': self.sensor_reading_value,
                'last_reading_time': fields.Datetime.now()
            })
        
        # Create sensor data record
        self.env['facilities.asset.sensor.data'].create({
            'sensor_id': sensor.id,
            'reading_time': fields.Datetime.now(),
            'value': self.sensor_reading_value
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sensor Reading Recorded',
                'message': f'Sensor reading {self.sensor_reading_value} {self.sensor_reading_unit or "units"} recorded for {self.asset_id.name}',
                'type': 'success'
            }
        }
    
    def _record_inspection(self):
        """Record a quick inspection"""
        if not self.inspection_result:
            raise UserError(_("Please select an inspection result."))
        
        # Create inspection record
        inspection_vals = {
            'name': f"Mobile Inspection - {self.asset_id.name}",
            'asset_id': self.asset_id.id,
            'inspection_date': fields.Date.today(),
            'inspector_id': self.env.uid,
            'result': self.inspection_result,
            'notes': self.inspection_notes or f"Quick inspection performed via mobile scan at {self.scan_location}",
            'location': self.scan_location
        }
        
        # Create inspection record (assuming we have an inspection model)
        # self.env['facilities.asset.inspection'].create(inspection_vals)
        
        # For now, create an activity
        self.asset_id.activity_schedule(
            'mail.mail_activity_data_todo',
            note=f"Inspection Result: {self.inspection_result}\nNotes: {self.inspection_notes or 'No notes'}",
            user_id=self.env.uid
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Inspection Recorded',
                'message': f'Inspection result {self.inspection_result} recorded for {self.asset_id.name}',
                'type': 'success'
            }
        }
    
    def action_search_by_code(self):
        """Search for asset by scanned code"""
        if not self.scanned_code:
            raise UserError(_("Please enter a code to search."))
        
        # Search for asset by barcode or asset code
        asset = self.env['facilities.asset'].search([
            '|',
            ('barcode', '=', self.scanned_code),
            ('asset_code', '=', self.scanned_code)
        ], limit=1)
        
        if asset:
            self.asset_id = asset.id
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Asset Found',
                    'message': f'Asset {asset.name} found with code {self.scanned_code}',
                    'type': 'success'
                }
            }
        else:
            raise UserError(_("No asset found with code %s") % self.scanned_code)
    
    def action_generate_qr_code(self):
        """Generate QR code for the asset"""
        self.ensure_one()
        
        if not self.asset_id.qr_code:
            # Generate QR code
            qr_code = f"ASSET_{self.asset_id.asset_code}_{self.asset_id.id}"
            self.asset_id.write({'qr_code': qr_code})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'QR Code Generated',
                'message': f'QR code {self.asset_id.qr_code} generated for {self.asset_id.name}',
                'type': 'success'
            }
        }