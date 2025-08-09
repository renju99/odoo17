# models/asset_sensor.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AssetSensor(models.Model):
    _name = 'facilities.asset.sensor'
    _description = 'IoT Sensor for Asset Monitoring'
    _order = 'name'

    name = fields.Char(string='Sensor Name', required=True)
    asset_id = fields.Many2one('facilities.asset', string='Asset', required=True, ondelete='cascade')
    sensor_type = fields.Selection([
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('vibration', 'Vibration'),
        ('pressure', 'Pressure'),
        ('power', 'Power Consumption'),
        ('runtime', 'Runtime Hours'),
        ('flow', 'Flow Rate'),
        ('level', 'Level'),
        ('custom', 'Custom')
    ], string='Sensor Type', required=True)
    
    sensor_id = fields.Char(string='Sensor ID', required=True, help="Unique identifier for the IoT sensor")
    active = fields.Boolean(string='Active', default=True)
    
    # Measurement Configuration
    unit = fields.Char(string='Unit', help="Unit of measurement (e.g., °C, %, Hz)")
    min_value = fields.Float(string='Minimum Value', help="Minimum acceptable value")
    max_value = fields.Float(string='Maximum Value', help="Maximum acceptable value")
    warning_threshold = fields.Float(string='Warning Threshold', help="Value that triggers a warning alert")
    critical_threshold = fields.Float(string='Critical Threshold', help="Value that triggers a critical alert")
    
    # Real-time Data
    current_value = fields.Float(string='Current Value', help="Latest sensor reading")
    last_reading_time = fields.Datetime(string='Last Reading Time', help="Timestamp of the last sensor reading")
    reading_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('minute', 'Every Minute'),
        ('hour', 'Hourly'),
        ('day', 'Daily')
    ], string='Reading Frequency', default='hour')
    
    # Status and Alerts
    status = fields.Selection([
        ('normal', 'Normal'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('offline', 'Offline'),
        ('error', 'Error')
    ], string='Status', default='normal', compute='_compute_status', store=True)
    
    alert_enabled = fields.Boolean(string='Enable Alerts', default=True)
    last_alert_time = fields.Datetime(string='Last Alert Time')
    alert_count = fields.Integer(string='Alert Count', default=0)
    
    # Historical Data
    historical_data = fields.Json(string='Historical Data', help="Stored historical readings")
    data_retention_days = fields.Integer(string='Data Retention (Days)', default=30)
    
    # Communication
    communication_protocol = fields.Selection([
        ('mqtt', 'MQTT'),
        ('http', 'HTTP/REST'),
        ('modbus', 'Modbus'),
        ('opc_ua', 'OPC UA'),
        ('custom', 'Custom')
    ], string='Communication Protocol', default='mqtt')
    
    endpoint_url = fields.Char(string='Endpoint URL', help="URL or endpoint for sensor data")
    api_key = fields.Char(string='API Key', help="API key for sensor communication")
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends('current_value', 'warning_threshold', 'critical_threshold', 'min_value', 'max_value')
    def _compute_status(self):
        for sensor in self:
            if not sensor.active:
                sensor.status = 'offline'
                continue
                
            if sensor.current_value is False:
                sensor.status = 'error'
                continue
                
            if sensor.critical_threshold and sensor.current_value >= sensor.critical_threshold:
                sensor.status = 'critical'
            elif sensor.warning_threshold and sensor.current_value >= sensor.warning_threshold:
                sensor.status = 'warning'
            elif sensor.min_value and sensor.current_value < sensor.min_value:
                sensor.status = 'critical'
            elif sensor.max_value and sensor.current_value > sensor.max_value:
                sensor.status = 'critical'
            else:
                sensor.status = 'normal'
    
    def action_update_reading(self, value, timestamp=None):
        """Update sensor reading from external source"""
        self.ensure_one()
        if timestamp is None:
            timestamp = fields.Datetime.now()
            
        self.write({
            'current_value': value,
            'last_reading_time': timestamp
        })
        
        # Check for alerts
        if self.alert_enabled and self.status in ['warning', 'critical']:
            self._create_alert()
    
    def _create_alert(self):
        """Create alert notification for sensor"""
        self.ensure_one()
        
        alert_message = f"Sensor {self.name} on {self.asset_id.name} is in {self.status} status. Current value: {self.current_value} {self.unit}"
        
        # Create activity for asset
        self.asset_id.activity_schedule(
            'mail.mail_activity_data_todo',
            note=alert_message,
            user_id=self.asset_id.responsible_id.id or self.env.uid
        )
        
        # Update alert tracking
        self.write({
            'last_alert_time': fields.Datetime.now(),
            'alert_count': self.alert_count + 1
        })
        
        # Send notification to responsible person
        if self.asset_id.responsible_id:
            self.env['mail.channel'].message_post(
                body=alert_message,
                partner_ids=[self.asset_id.responsible_id.partner_id.id]
            )
    
    def action_view_historical_data(self):
        """View historical sensor data"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Sensor Data - {self.name}',
            'res_model': 'facilities.asset.sensor.data',
            'view_mode': 'graph,tree',
            'domain': [('sensor_id', '=', self.id)],
            'context': {'default_sensor_id': self.id},
        }
    
    def action_test_sensor(self):
        """Test sensor communication"""
        self.ensure_one()
        try:
            # Simulate sensor reading (in real implementation, this would call the actual sensor)
            test_value = 25.0  # Example temperature value
            self.action_update_reading(test_value)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sensor Test',
                    'message': f'Sensor {self.name} test successful. Reading: {test_value} {self.unit}',
                    'type': 'success'
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sensor Test Failed',
                    'message': f'Error testing sensor {self.name}: {str(e)}',
                    'type': 'danger'
                }
            }
    
    @api.model
    def cron_update_sensor_readings(self):
        """Cron job to update sensor readings from external sources"""
        active_sensors = self.search([('active', '=', True)])
        for sensor in active_sensors:
            try:
                # In real implementation, this would fetch data from the actual sensor
                # For now, we'll simulate with a random value
                import random
                if sensor.sensor_type == 'temperature':
                    value = random.uniform(15, 35)
                elif sensor.sensor_type == 'humidity':
                    value = random.uniform(30, 80)
                elif sensor.sensor_type == 'vibration':
                    value = random.uniform(0, 10)
                else:
                    value = random.uniform(0, 100)
                
                sensor.action_update_reading(value)
                
            except Exception as e:
                _logger.error(f"Error updating sensor {sensor.name}: {str(e)}")
                sensor.status = 'error'

    @api.model
    def _check_sensor_health(self):
        """Cron method to check sensor health and trigger alerts"""
        try:
            # Find sensors that need health checks
            sensors = self.search([('active', '=', True)])
            
            for sensor in sensors:
                # Check if sensor is offline (no reading in last hour)
                if sensor.last_reading_time:
                    time_diff = fields.Datetime.now() - sensor.last_reading_time
                    if time_diff.total_seconds() > 3600:  # 1 hour
                        sensor.status = 'offline'
                        if sensor.alert_enabled:
                            sensor._create_alert()
                
                # Check for critical conditions
                if sensor.status == 'critical' and sensor.alert_enabled:
                    sensor._create_alert()
            
            _logger.info(f"Sensor health check completed. {len(sensors)} sensors checked.")
            
        except Exception as e:
            _logger.error(f"Error in sensor health check cron: {str(e)}")


class AssetSensorData(models.Model):
    _name = 'facilities.asset.sensor.data'
    _description = 'Historical Sensor Data'
    _order = 'reading_time desc'

    sensor_id = fields.Many2one('facilities.asset.sensor', string='Sensor', required=True, ondelete='cascade')
    asset_id = fields.Many2one('facilities.asset', string='Asset', related='sensor_id.asset_id', store=True)
    
    reading_time = fields.Datetime(string='Reading Time', required=True)
    value = fields.Float(string='Value', required=True)
    unit = fields.Char(string='Unit', related='sensor_id.unit', store=True)
    
    status = fields.Selection([
        ('normal', 'Normal'),
        ('warning', 'Warning'),
        ('critical', 'Critical')
    ], string='Status', compute='_compute_status', store=True)
    
    @api.depends('value', 'sensor_id.warning_threshold', 'sensor_id.critical_threshold')
    def _compute_status(self):
        for record in self:
            if record.sensor_id.critical_threshold and record.value >= record.sensor_id.critical_threshold:
                record.status = 'critical'
            elif record.sensor_id.warning_threshold and record.value >= record.sensor_id.warning_threshold:
                record.status = 'warning'
            else:
                record.status = 'normal'