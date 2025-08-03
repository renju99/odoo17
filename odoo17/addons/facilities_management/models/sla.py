# models/sla.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class FacilitiesSLA(models.Model):
    _name = 'facilities.sla'
    _description = 'Service Level Agreement'
    _order = 'priority desc, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='SLA Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    priority = fields.Integer(string='Priority', default=10, help="Higher number = higher priority")
    
    # SLA Timeframes
    response_time_hours = fields.Float(string='Response Time (Hours)', required=True, default=4.0)
    resolution_time_hours = fields.Float(string='Resolution Time (Hours)', required=True, default=24.0)
    warning_threshold_hours = fields.Float(string='Warning Threshold (Hours)', default=2.0, 
                                         help="Hours before deadline to trigger warning")
    critical_threshold_hours = fields.Float(string='Critical Threshold (Hours)', default=1.0,
                                          help="Hours before deadline to trigger critical alert")
    escalation_delay_hours = fields.Float(string='Escalation Delay (Hours)', default=2.0,
                                        help="Hours after breach to trigger escalation")
    
    # Assignment Rules
    asset_criticality = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')
    ], string='Asset Criticality', help="Apply to assets with this criticality level")
    
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'), ('corrective', 'Corrective'),
        ('predictive', 'Predictive'), ('inspection', 'Inspection')
    ], string='Maintenance Type', help="Apply to this maintenance type")
    
    priority_level = fields.Selection([
        ('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High'), ('4', 'Critical')
    ], string='Priority Level', help="Apply to work orders with this priority")
    
    facility_ids = fields.Many2many('facilities.facility', string='Facilities', 
                                   help="Apply to assets in these facilities")
    
    # Escalation Configuration
    escalation_enabled = fields.Boolean(string='Enable Escalation', default=True)
    max_escalation_level = fields.Integer(string='Max Escalation Level', default=3)
    escalation_recipients = fields.Many2many('res.users', string='Escalation Recipients')
    
    # Notification Settings
    email_notifications = fields.Boolean(string='Email Notifications', default=True)
    sms_notifications = fields.Boolean(string='SMS Notifications', default=False)
    notification_template_id = fields.Many2one('mail.template', string='Notification Template')
    
    # KPI Targets
    target_mttr_hours = fields.Float(string='Target MTTR (Hours)', default=8.0)
    target_first_time_fix_rate = fields.Float(string='Target First Time Fix Rate (%)', default=85.0)
    target_sla_compliance_rate = fields.Float(string='Target SLA Compliance Rate (%)', default=95.0)
    
    # Advanced Settings
    business_hours_only = fields.Boolean(string='Business Hours Only', default=False)
    business_hours_start = fields.Float(string='Business Hours Start', default=8.0)
    business_hours_end = fields.Float(string='Business Hours End', default=17.0)
    business_days = fields.Char(string='Business Days', default='monday,tuesday,wednesday,thursday,friday',
                               help="Comma-separated list of business days (e.g., monday,tuesday,wednesday,thursday,friday)")
    
    # Performance Tracking
    total_workorders = fields.Integer(string='Total Work Orders', compute='_compute_performance_metrics')
    compliant_workorders = fields.Integer(string='Compliant Work Orders', compute='_compute_performance_metrics')
    breached_workorders = fields.Integer(string='Breached Work Orders', compute='_compute_performance_metrics')
    compliance_rate = fields.Float(string='Compliance Rate (%)', compute='_compute_performance_metrics')
    avg_mttr = fields.Float(string='Average MTTR (Hours)', compute='_compute_performance_metrics')
    
    @api.depends('name')
    def _compute_performance_metrics(self):
        for sla in self:
            workorders = self.env['maintenance.workorder'].search([
                ('sla_id', '=', sla.id),
                ('state', '=', 'completed')
            ])
            
            sla.total_workorders = len(workorders)
            sla.compliant_workorders = len(workorders.filtered(lambda w: w.sla_status == 'completed'))
            sla.breached_workorders = len(workorders.filtered(lambda w: w.sla_status == 'breached'))
            
            if sla.total_workorders > 0:
                sla.compliance_rate = (sla.compliant_workorders / sla.total_workorders) * 100
                sla.avg_mttr = sum(workorders.mapped('mttr')) / sla.total_workorders
            else:
                sla.compliance_rate = 0.0
                sla.avg_mttr = 0.0

    @api.constrains('response_time_hours', 'resolution_time_hours')
    def _check_timeframes(self):
        for sla in self:
            if sla.response_time_hours >= sla.resolution_time_hours:
                raise ValidationError(_('Response time must be less than resolution time.'))
            if sla.response_time_hours <= 0 or sla.resolution_time_hours <= 0:
                raise ValidationError(_('Response and resolution times must be positive values.'))
            if sla.warning_threshold_hours >= sla.critical_threshold_hours:
                raise ValidationError(_('Warning threshold must be less than critical threshold.'))
            if sla.warning_threshold_hours <= 0 or sla.critical_threshold_hours <= 0:
                raise ValidationError(_('Warning and critical thresholds must be positive values.'))

    def action_view_workorders(self):
        """View work orders assigned to this SLA"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Work Orders - {self.name}',
            'res_model': 'maintenance.workorder',
            'view_mode': 'tree,form',
            'domain': [('sla_id', '=', self.id)],
            'context': {'default_sla_id': self.id}
        }

    def action_view_performance_dashboard(self):
        """Open performance dashboard for this SLA"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'SLA Performance - {self.name}',
            'res_model': 'facilities.sla.dashboard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sla_id': self.id}
        }

    def action_activate_sla(self):
        """Activate the SLA"""
        self.ensure_one()
        self.write({'active': True})
        
        # Log the activation in chatter
        self.message_post(
            body=_('SLA "%s" has been activated by %s.') % (self.name, self.env.user.name),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SLA Activated'),
                'message': f'SLA "{self.name}" has been activated successfully.',
                'type': 'success',
            }
        }

    def action_deactivate_sla(self):
        """Deactivate the SLA"""
        self.ensure_one()
        self.write({'active': False})
        
        # Log the deactivation in chatter
        self.message_post(
            body=_('SLA "%s" has been deactivated by %s.') % (self.name, self.env.user.name),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SLA Deactivated'),
                'message': f'SLA "{self.name}" has been deactivated.',
                'type': 'warning',
            }
        }

    def action_duplicate_sla(self):
        """Duplicate the SLA"""
        self.ensure_one()
        default_values = {
            'name': f'{self.name} (Copy)',
            'active': False,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicate SLA'),
            'res_model': 'facilities.sla',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': default_values['name'],
                'default_active': default_values['active'],
                'default_description': self.description,
                'default_response_time_hours': self.response_time_hours,
                'default_resolution_time_hours': self.resolution_time_hours,
                'default_warning_threshold_hours': self.warning_threshold_hours,
                'default_critical_threshold_hours': self.critical_threshold_hours,
                'default_escalation_delay_hours': self.escalation_delay_hours,
                'default_asset_criticality': self.asset_criticality,
                'default_maintenance_type': self.maintenance_type,
                'default_priority_level': self.priority_level,
                'default_facility_ids': [(6, 0, self.facility_ids.ids)],
                'default_escalation_enabled': self.escalation_enabled,
                'default_max_escalation_level': self.max_escalation_level,
                'default_escalation_recipients': [(6, 0, self.escalation_recipients.ids)],
                'default_email_notifications': self.email_notifications,
                'default_sms_notifications': self.sms_notifications,
                'default_notification_template_id': self.notification_template_id.id,
                'default_target_mttr_hours': self.target_mttr_hours,
                'default_target_first_time_fix_rate': self.target_first_time_fix_rate,
                'default_target_sla_compliance_rate': self.target_sla_compliance_rate,
                'default_business_hours_only': self.business_hours_only,
                'default_business_hours_start': self.business_hours_start,
                'default_business_hours_end': self.business_hours_end,
                'default_business_days': self.business_days,
            }
        }

    def action_test_sla_assignment(self):
        """Test SLA assignment with current work orders"""
        self.ensure_one()
        workorders = self.env['maintenance.workorder'].search([
            ('sla_id', '=', False),
            ('state', 'in', ['draft', 'assigned'])
        ], limit=10)
        
        assigned_count = 0
        for workorder in workorders:
            try:
                workorder._apply_sla()
                if workorder.sla_id == self:
                    assigned_count += 1
            except Exception as e:
                _logger.warning(f"Error testing SLA assignment for work order {workorder.name}: {str(e)}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SLA Assignment Test'),
                'message': f'Tested SLA assignment on {len(workorders)} work orders. {assigned_count} were assigned to this SLA.',
                'type': 'success' if assigned_count > 0 else 'warning',
            }
        }

    def action_bulk_activate(self):
        """Activate selected SLAs"""
        activated_count = 0
        activated_names = []
        for sla in self:
            if not sla.active:
                sla.write({'active': True})
                # Log the activation in chatter
                sla.message_post(
                    body=_('SLA "%s" has been activated by %s via bulk operation.') % (sla.name, self.env.user.name),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
                activated_count += 1
                activated_names.append(sla.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SLAs Activated'),
                'message': f'{activated_count} SLA(s) have been activated successfully.',
                'type': 'success',
            }
        }

    def action_bulk_deactivate(self):
        """Deactivate selected SLAs"""
        deactivated_count = 0
        deactivated_names = []
        for sla in self:
            if sla.active:
                sla.write({'active': False})
                # Log the deactivation in chatter
                sla.message_post(
                    body=_('SLA "%s" has been deactivated by %s via bulk operation.') % (sla.name, self.env.user.name),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
                deactivated_count += 1
                deactivated_names.append(sla.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SLAs Deactivated'),
                'message': f'{deactivated_count} SLA(s) have been deactivated successfully.',
                'type': 'warning',
            }
        }

    def _calculate_business_hours(self, start_time, end_time):
        """Calculate business hours between two timestamps"""
        if not self.business_hours_only:
            return (end_time - start_time).total_seconds() / 3600
        
        # Implement business hours calculation logic
        # This is a simplified version - in production, you'd want more sophisticated logic
        total_hours = 0
        current_time = start_time
        
        while current_time < end_time:
            # Check if current time is within business hours
            hour = current_time.hour + current_time.minute / 60
            day_of_week = current_time.strftime('%A').lower()
            
            if (self.business_hours_start <= hour <= self.business_hours_end and
                day_of_week in self.business_days.split(',')):
                total_hours += 1
            
            current_time += timedelta(hours=1)
        
        return total_hours

    @api.model
    def create_default_sla_records(self):
        """Create default SLA records if none exist"""
        existing_slas = self.search([])
        if existing_slas:
            return existing_slas
        
        default_slas = []
        
        # Default SLA
        default_slas.append({
            'name': 'Default SLA',
            'description': 'Default Service Level Agreement for general maintenance',
            'response_time_hours': 4.0,
            'resolution_time_hours': 24.0,
            'warning_threshold_hours': 1.0,
            'critical_threshold_hours': 2.0,
            'escalation_delay_hours': 2.0,
            'active': True,
            'priority': 10,
        })
        
        # Critical Asset SLA
        default_slas.append({
            'name': 'Critical Asset SLA',
            'description': 'SLA for critical assets requiring immediate attention',
            'response_time_hours': 1.0,
            'resolution_time_hours': 8.0,
            'warning_threshold_hours': 0.25,
            'critical_threshold_hours': 0.5,
            'escalation_delay_hours': 1.0,
            'active': True,
            'priority': 40,
            'asset_criticality': 'critical',
        })
        
        # High Priority SLA
        default_slas.append({
            'name': 'High Priority SLA',
            'description': 'SLA for high priority assets',
            'response_time_hours': 2.0,
            'resolution_time_hours': 12.0,
            'warning_threshold_hours': 0.5,
            'critical_threshold_hours': 1.0,
            'escalation_delay_hours': 2.0,
            'active': True,
            'priority': 30,
            'asset_criticality': 'high',
        })
        
        # Medium Priority SLA
        default_slas.append({
            'name': 'Medium Priority SLA',
            'description': 'SLA for medium priority assets',
            'response_time_hours': 4.0,
            'resolution_time_hours': 24.0,
            'warning_threshold_hours': 1.0,
            'critical_threshold_hours': 2.0,
            'escalation_delay_hours': 4.0,
            'active': True,
            'priority': 20,
            'asset_criticality': 'medium',
        })
        
        # Low Priority SLA
        default_slas.append({
            'name': 'Low Priority SLA',
            'description': 'SLA for low priority assets',
            'response_time_hours': 8.0,
            'resolution_time_hours': 48.0,
            'warning_threshold_hours': 2.0,
            'critical_threshold_hours': 4.0,
            'escalation_delay_hours': 8.0,
            'active': True,
            'priority': 10,
            'asset_criticality': 'low',
        })
        
        created_slas = []
        for sla_data in default_slas:
            created_sla = self.create(sla_data)
            created_slas.append(created_sla)
        
        return created_slas

class SLADashboard(models.Model):
    _name = 'facilities.sla.dashboard'
    _description = 'SLA Performance Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sla_id = fields.Many2one('facilities.sla', string='SLA', required=True)
    date_from = fields.Date(string='From Date', default=fields.Date.today)
    date_to = fields.Date(string='To Date', default=fields.Date.today)
    
    # Performance Metrics
    total_workorders = fields.Integer(string='Total Work Orders', compute='_compute_metrics')
    compliant_workorders = fields.Integer(string='Compliant Work Orders', compute='_compute_metrics')
    breached_workorders = fields.Integer(string='Breached Work Orders', compute='_compute_metrics')
    compliance_rate = fields.Float(string='Compliance Rate (%)', compute='_compute_metrics')
    avg_mttr = fields.Float(string='Average MTTR (Hours)', compute='_compute_metrics')
    avg_first_time_fix_rate = fields.Float(string='First Time Fix Rate (%)', compute='_compute_metrics')
    
    # Trend Analysis
    daily_compliance = fields.Json(string='Daily Compliance', compute='_compute_metrics')
    weekly_trend = fields.Json(string='Weekly Trend', compute='_compute_metrics')
    
    @api.depends('sla_id', 'date_from', 'date_to')
    def _compute_metrics(self):
        for dashboard in self:
            # Initialize default values
            dashboard.total_workorders = 0
            dashboard.compliant_workorders = 0
            dashboard.breached_workorders = 0
            dashboard.compliance_rate = 0.0
            dashboard.avg_mttr = 0.0
            dashboard.avg_first_time_fix_rate = 0.0
            dashboard.daily_compliance = []
            dashboard.weekly_trend = []
            
            if not dashboard.sla_id:
                continue
            
            # Search for work orders with the specified SLA and date range
            domain = [
                ('sla_id', '=', dashboard.sla_id.id),
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ]
            
            workorders = self.env['maintenance.workorder'].search(domain)
            
            if not workorders:
                continue
            
            dashboard.total_workorders = len(workorders)
            
            # Count compliant work orders (completed SLA status)
            compliant_workorders = workorders.filtered(lambda w: w.sla_status == 'completed')
            dashboard.compliant_workorders = len(compliant_workorders)
            
            # Count breached work orders
            breached_workorders = workorders.filtered(lambda w: w.sla_status == 'breached')
            dashboard.breached_workorders = len(breached_workorders)
            
            # Calculate compliance rate
            if dashboard.total_workorders > 0:
                dashboard.compliance_rate = (dashboard.compliant_workorders / dashboard.total_workorders) * 100
                
                # Calculate average MTTR (Mean Time To Repair)
                mttr_values = workorders.mapped('mttr')
                valid_mttr_values = [mttr for mttr in mttr_values if mttr and mttr > 0]
                if valid_mttr_values:
                    dashboard.avg_mttr = sum(valid_mttr_values) / len(valid_mttr_values)
                
                # Calculate first time fix rate
                first_time_fixes = workorders.filtered(lambda w: w.first_time_fix and w.state == 'completed')
                dashboard.avg_first_time_fix_rate = (len(first_time_fixes) / dashboard.total_workorders) * 100
            
            # Calculate daily compliance trend
            dashboard.daily_compliance = self._calculate_daily_compliance(workorders)
            dashboard.weekly_trend = self._calculate_weekly_trend(workorders)

    def _calculate_daily_compliance(self, workorders):
        """Calculate daily compliance rates"""
        if not workorders:
            return []
            
        daily_data = {}
        for workorder in workorders:
            if not workorder.create_date:
                continue
                
            date = workorder.create_date.date()
            if date not in daily_data:
                daily_data[date] = {'total': 0, 'compliant': 0}
            
            daily_data[date]['total'] += 1
            if workorder.sla_status == 'completed':
                daily_data[date]['compliant'] += 1
        
        return [
            {
                'date': date.strftime('%Y-%m-%d'),
                'compliance_rate': (data['compliant'] / data['total']) * 100 if data['total'] > 0 else 0,
                'total_workorders': data['total'],
                'compliant_workorders': data['compliant']
            }
            for date, data in sorted(daily_data.items())
        ]

    def _calculate_weekly_trend(self, workorders):
        """Calculate weekly trend analysis"""
        if not workorders:
            return []
            
        weekly_data = {}
        for workorder in workorders:
            if not workorder.create_date:
                continue
                
            week_start = workorder.create_date.date() - timedelta(days=workorder.create_date.weekday())
            if week_start not in weekly_data:
                weekly_data[week_start] = {
                    'total': 0, 'compliant': 0, 'breached': 0, 'avg_mttr': 0, 'mttr_count': 0
                }
            
            weekly_data[week_start]['total'] += 1
            if workorder.sla_status == 'completed':
                weekly_data[week_start]['compliant'] += 1
            elif workorder.sla_status == 'breached':
                weekly_data[week_start]['breached'] += 1
            
            # Add MTTR if available
            if workorder.mttr and workorder.mttr > 0:
                weekly_data[week_start]['avg_mttr'] += workorder.mttr
                weekly_data[week_start]['mttr_count'] += 1
        
        return [
            {
                'week': week_start.strftime('%Y-%m-%d'),
                'total': data['total'],
                'compliance_rate': (data['compliant'] / data['total']) * 100 if data['total'] > 0 else 0,
                'breach_rate': (data['breached'] / data['total']) * 100 if data['total'] > 0 else 0,
                'avg_mttr': data['avg_mttr'] / data['mttr_count'] if data['mttr_count'] > 0 else 0,
                'compliant_workorders': data['compliant'],
                'breached_workorders': data['breached']
            }
            for week_start, data in sorted(weekly_data.items())
        ]

    def action_export_report(self):
        """Export SLA performance report"""
        # Create or get the SLA dashboard record
        dashboard = self.env['facilities.sla.dashboard'].create({
            'sla_id': self.sla_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to
        })
        
        # Return the report action
        return {
            'type': 'ir.actions.report',
            'report_name': 'facilities_management.sla_performance_report',
            'report_type': 'qweb-pdf',
            'data': {
                'doc_ids': [dashboard.id],
                'doc_model': 'facilities.sla.dashboard',
            }
        }

    def action_debug_data(self):
        """Debug method to check data availability"""
        self.ensure_one()
        
        # Check if SLA exists
        if not self.sla_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Debug Info',
                    'message': 'No SLA selected',
                    'type': 'warning',
                }
            }
        
        # Search for work orders
        workorders = self.env['maintenance.workorder'].search([
            ('sla_id', '=', self.sla_id.id),
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ])
        
        # Get SLA status distribution
        status_distribution = {}
        for workorder in workorders:
            status = workorder.sla_status or 'no_status'
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Check if there are any SLAs in the system
        all_slas = self.env['facilities.sla'].search([])
        all_workorders = self.env['maintenance.workorder'].search([])
        workorders_with_sla = self.env['maintenance.workorder'].search([('sla_id', '!=', False)])
        
        message = f"""
        Debug Information:
        - SLA: {self.sla_id.name}
        - Date Range: {self.date_from} to {self.date_to}
        - Total Work Orders Found: {len(workorders)}
        - Status Distribution: {status_distribution}
        - Total Work Orders in Dashboard: {self.total_workorders}
        - Compliant Work Orders: {self.compliant_workorders}
        - Breached Work Orders: {self.breached_workorders}
        - Compliance Rate: {self.compliance_rate}%
        
        System Overview:
        - Total SLAs in system: {len(all_slas)}
        - Total Work Orders in system: {len(all_workorders)}
        - Work Orders with SLA assigned: {len(workorders_with_sla)}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Debug Information',
                'message': message,
                'type': 'info',
            }
        }

    def action_create_default_slas(self):
        """Create default SLA records if none exist"""
        existing_slas = self.env['facilities.sla'].search([])
        
        if existing_slas:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Default SLAs',
                    'message': f'SLAs already exist ({len(existing_slas)} found). No need to create defaults.',
                    'type': 'info',
                }
            }
        
        # Create default SLAs
        default_slas = self.env['facilities.sla'].create_default_sla_records()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Default SLAs Created',
                'message': f'Created {len(default_slas)} default SLA records. You can now select an SLA for the dashboard.',
                'type': 'success',
            }
        }

    def action_create_test_data(self):
        """Create test data for debugging"""
        self.ensure_one()
        
        if not self.sla_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Please select an SLA first',
                    'type': 'error',
                }
            }
        
        # Find or create a test asset
        test_asset = self.env['facilities.asset'].search([], limit=1)
        if not test_asset:
            # Create a test asset if none exists
            test_facility = self.env['facilities.facility'].search([], limit=1)
            if not test_facility:
                # Create a test facility if none exists
                test_facility = self.env['facilities.facility'].create({
                    'name': 'Test Facility',
                    'code': 'TEST001',
                })
            
            test_asset = self.env['facilities.asset'].create({
                'name': 'Test Asset',
                'code': 'TEST_ASSET_001',
                'facility_id': test_facility.id,
                'criticality': 'medium',
                'asset_type': 'equipment',
            })
        
        # Create some test work orders
        test_workorders = []
        for i in range(5):
            workorder = self.env['maintenance.workorder'].create({
                'name': f'Test Work Order {i+1}',
                'description': f'Test work order for debugging SLA dashboard {i+1}',
                'asset_id': test_asset.id,
                'sla_id': self.sla_id.id,
                'maintenance_type': 'corrective',
                'priority': '2',
                'state': 'completed',
                'sla_status': 'completed' if i < 3 else 'breached',  # 3 compliant, 2 breached
                'first_time_fix': True if i < 4 else False,  # 4 first time fixes
                'mttr': 2.5 + i,  # Different MTTR values
                'actual_duration': 2.5 + i,  # Set actual duration for MTTR calculation
                'create_date': self.date_from,
                'actual_start_date': self.date_from,
                'actual_end_date': self.date_from,
            })
            test_workorders.append(workorder)
        
        # Refresh the dashboard
        self._compute_metrics()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test Data Created',
                'message': f'Created {len(test_workorders)} test work orders with asset {test_asset.name}. Dashboard should now show data.',
                'type': 'success',
            }
        }

class MaintenanceKPIDashboard(models.Model):
    _name = 'maintenance.kpi.dashboard'
    _description = 'Maintenance KPI Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    workorder_id = fields.Many2one('maintenance.workorder', string='Work Order')
    team_id = fields.Many2one('maintenance.team', string='Maintenance Team')
    date_from = fields.Date(string='From Date', default=fields.Date.today)
    date_to = fields.Date(string='To Date', default=fields.Date.today)
    
    # KPI Metrics
    total_workorders = fields.Integer(string='Total Work Orders', compute='_compute_kpis')
    completed_workorders = fields.Integer(string='Completed Work Orders', compute='_compute_kpis')
    avg_mttr = fields.Float(string='Average MTTR (Hours)', compute='_compute_kpis')
    first_time_fix_rate = fields.Float(string='First Time Fix Rate (%)', compute='_compute_kpis')
    sla_compliance_rate = fields.Float(string='SLA Compliance Rate (%)', compute='_compute_kpis')
    total_downtime = fields.Float(string='Total Downtime (Hours)', compute='_compute_kpis')
    total_cost = fields.Monetary(string='Total Cost', currency_field='currency_id', compute='_compute_kpis')
    avg_cost_per_workorder = fields.Monetary(string='Avg Cost per Work Order', currency_field='currency_id', compute='_compute_kpis')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    @api.depends('workorder_id', 'team_id', 'date_from', 'date_to')
    def _compute_kpis(self):
        for dashboard in self:
            domain = [
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ]
            
            if dashboard.workorder_id:
                workorders = dashboard.workorder_id
            elif dashboard.team_id:
                domain.append(('team_id', '=', dashboard.team_id.id))
                workorders = self.env['maintenance.workorder'].search(domain)
            else:
                workorders = self.env['maintenance.workorder'].search(domain)
            
            dashboard.total_workorders = len(workorders)
            dashboard.completed_workorders = len(workorders.filtered(lambda w: w.state == 'completed'))
            
            if dashboard.completed_workorders > 0:
                dashboard.avg_mttr = sum(workorders.filtered(lambda w: w.state == 'completed').mapped('mttr')) / dashboard.completed_workorders
                first_time_fixes = len(workorders.filtered(lambda w: w.first_time_fix and w.state == 'completed'))
                dashboard.first_time_fix_rate = (first_time_fixes / dashboard.completed_workorders) * 100
                
                sla_compliant = len(workorders.filtered(lambda w: w.sla_status == 'completed'))
                dashboard.sla_compliance_rate = (sla_compliant / dashboard.completed_workorders) * 100
            else:
                dashboard.avg_mttr = 0.0
                dashboard.first_time_fix_rate = 0.0
                dashboard.sla_compliance_rate = 0.0
            
            dashboard.total_downtime = sum(workorders.mapped('downtime_hours'))
            dashboard.total_cost = sum(workorders.mapped('total_cost'))
            dashboard.avg_cost_per_workorder = dashboard.total_cost / dashboard.total_workorders if dashboard.total_workorders > 0 else 0.0