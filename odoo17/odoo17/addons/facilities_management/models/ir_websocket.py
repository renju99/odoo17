# -*- coding: utf-8 -*-

import json
import logging
from odoo import models, api
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrWebsocket(models.AbstractModel):
    _name = 'ir.websocket'
    _inherit = 'ir.websocket'

    def _build_bus_channel_list(self, channels):
        """Add facilities management specific channels to the bus"""
        channels = super()._build_bus_channel_list(channels)
        
        if request and hasattr(request, 'session') and request.session.uid:
            # Add IoT sensor monitoring channel for authenticated users
            channels.append(f'facilities_iot_sensors_{request.session.uid}')
            
            # Add facility-specific channels if user has access
            facility_ids = self.env['facilities.facility'].search([]).ids
            for facility_id in facility_ids:
                channels.append(f'facility_{facility_id}_sensors')
        
        return channels

    @api.model
    def _get_im_status(self, *args, **kwargs):
        """Override to handle IoT sensor status updates"""
        try:
            return super()._get_im_status(*args, **kwargs)
        except Exception as e:
            _logger.warning(f"Error in _get_im_status: {e}")
            return {}

    @api.model
    def send_sensor_alert(self, sensor_id, alert_data):
        """Send real-time sensor alert to connected clients"""
        try:
            sensor = self.env['facilities.asset.sensor'].browse(sensor_id)
            if sensor.exists():
                # Send to all users monitoring this facility
                channel = f'facility_{sensor.asset_id.facility_id.id}_sensors'
                message = {
                    'type': 'sensor_alert',
                    'sensor_id': sensor_id,
                    'sensor_name': sensor.name,
                    'asset_name': sensor.asset_id.name,
                    'current_value': sensor.current_value,
                    'unit': sensor.unit,
                    'status': sensor.status,
                    'alert_data': alert_data,
                    'timestamp': sensor.last_reading_time,
                }
                self.env['bus.bus']._sendone(channel, 'sensor_alert', message)
                _logger.info(f"Sent sensor alert for sensor {sensor.name}")
        except Exception as e:
            _logger.error(f"Error sending sensor alert: {e}")

    @api.model
    def send_sensor_update(self, sensor_id):
        """Send real-time sensor data update to connected clients"""
        try:
            sensor = self.env['facilities.asset.sensor'].browse(sensor_id)
            if sensor.exists():
                # Send to facility-specific channel
                channel = f'facility_{sensor.asset_id.facility_id.id}_sensors'
                message = {
                    'type': 'sensor_update',
                    'sensor_id': sensor_id,
                    'sensor_name': sensor.name,
                    'current_value': sensor.current_value,
                    'unit': sensor.unit,
                    'status': sensor.status,
                    'timestamp': sensor.last_reading_time,
                }
                self.env['bus.bus']._sendone(channel, 'sensor_update', message)
                
                # Also send to general IoT monitoring channel
                self.env['bus.bus']._sendone('iot_sensors_global', 'sensor_update', message)
        except Exception as e:
            _logger.error(f"Error sending sensor update: {e}")

    @api.model
    def send_maintenance_alert(self, workorder_id, alert_type='reminder'):
        """Send real-time maintenance alerts"""
        try:
            workorder = self.env['facilities.maintenance.workorder'].browse(workorder_id)
            if workorder.exists():
                channel = f'maintenance_team_{workorder.maintenance_team_id.id}'
                message = {
                    'type': 'maintenance_alert',
                    'workorder_id': workorder_id,
                    'workorder_name': workorder.name,
                    'asset_name': workorder.asset_id.name,
                    'alert_type': alert_type,
                    'priority': workorder.priority,
                    'scheduled_date': workorder.scheduled_date,
                }
                self.env['bus.bus']._sendone(channel, 'maintenance_alert', message)
        except Exception as e:
            _logger.error(f"Error sending maintenance alert: {e}")


class BusBus(models.Model):
    _inherit = 'bus.bus'

    def _sendone(self, channel, message_type, message):
        """Override to improve connection reliability"""
        try:
            return super()._sendone(channel, message_type, message)
        except Exception as e:
            _logger.warning(f"Failed to send bus message: {e}")
            # Attempt to reconnect and retry once
            try:
                self.env.cr.commit()
                return super()._sendone(channel, message_type, message)
            except Exception as retry_error:
                _logger.error(f"Failed to send bus message after retry: {retry_error}")
                return False