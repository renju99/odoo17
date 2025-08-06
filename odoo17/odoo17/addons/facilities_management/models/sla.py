# models/sla.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class FacilitiesSLA(models.Model):
    _name = 'facilities.sla'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Level Agreement'
    _order = 'priority desc, name'

    name = fields.Char(string='SLA Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    priority = fields.Integer(string='Priority', default=10, help="Higher number = higher priority")
    
    # SLA Timeframes
    response_time_hours = fields.Float(string='Response Time (Hours)', required=True, default=4.0)
    resolution_time_hours = fields.Float(string='Resolution Time (Hours)', required=True, default=24.0)
    warning_threshold_hours = fields.Float(string='Warning Threshold (Hours)', default=2.0, 
                                         help="Hours before deadline to trigger warning")
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
    business_days = fields.Selection([
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')
    ], string='Business Days', default='monday,tuesday,wednesday,thursday,friday')
    
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
            'warning_threshold_hours': 2.0,
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
            'warning_threshold_hours': 0.5,
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
            'warning_threshold_hours': 1.0,
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
            'warning_threshold_hours': 2.0,
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
            'warning_threshold_hours': 4.0,
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
            if not dashboard.sla_id:
                continue
            
            workorders = self.env['maintenance.workorder'].search([
                ('sla_id', '=', dashboard.sla_id.id),
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ])
            
            dashboard.total_workorders = len(workorders)
            dashboard.compliant_workorders = len(workorders.filtered(lambda w: w.sla_status == 'completed'))
            dashboard.breached_workorders = len(workorders.filtered(lambda w: w.sla_status == 'breached'))
            
            if dashboard.total_workorders > 0:
                dashboard.compliance_rate = (dashboard.compliant_workorders / dashboard.total_workorders) * 100
                dashboard.avg_mttr = sum(workorders.mapped('mttr')) / dashboard.total_workorders
                
                first_time_fixes = len(workorders.filtered(lambda w: w.first_time_fix))
                dashboard.avg_first_time_fix_rate = (first_time_fixes / dashboard.total_workorders) * 100
            else:
                dashboard.compliance_rate = 0.0
                dashboard.avg_mttr = 0.0
                dashboard.avg_first_time_fix_rate = 0.0
            
            # Calculate daily compliance trend
            dashboard.daily_compliance = self._calculate_daily_compliance(workorders)
            dashboard.weekly_trend = self._calculate_weekly_trend(workorders)

    def _calculate_daily_compliance(self, workorders):
        """Calculate daily compliance rates"""
        daily_data = {}
        for workorder in workorders:
            date = workorder.create_date.date()
            if date not in daily_data:
                daily_data[date] = {'total': 0, 'compliant': 0}
            
            daily_data[date]['total'] += 1
            if workorder.sla_status == 'completed':
                daily_data[date]['compliant'] += 1
        
        return [
            {
                'date': date.strftime('%Y-%m-%d'),
                'compliance_rate': (data['compliant'] / data['total']) * 100 if data['total'] > 0 else 0
            }
            for date, data in sorted(daily_data.items())
        ]

    def _calculate_weekly_trend(self, workorders):
        """Calculate weekly trend analysis"""
        weekly_data = {}
        for workorder in workorders:
            week_start = workorder.create_date.date() - timedelta(days=workorder.create_date.weekday())
            if week_start not in weekly_data:
                weekly_data[week_start] = {
                    'total': 0, 'compliant': 0, 'breached': 0, 'avg_mttr': 0
                }
            
            weekly_data[week_start]['total'] += 1
            if workorder.sla_status == 'completed':
                weekly_data[week_start]['compliant'] += 1
            elif workorder.sla_status == 'breached':
                weekly_data[week_start]['breached'] += 1
            
            weekly_data[week_start]['avg_mttr'] += workorder.mttr or 0
        
        return [
            {
                'week': week_start.strftime('%Y-%m-%d'),
                'total': data['total'],
                'compliance_rate': (data['compliant'] / data['total']) * 100 if data['total'] > 0 else 0,
                'breach_rate': (data['breached'] / data['total']) * 100 if data['total'] > 0 else 0,
                'avg_mttr': data['avg_mttr'] / data['total'] if data['total'] > 0 else 0
            }
            for week_start, data in sorted(weekly_data.items())
        ]

    def action_export_report(self):
        """Export SLA performance report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'facilities_management.sla_performance_report',
            'report_type': 'qweb-pdf',
            'data': {
                'sla_id': self.sla_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to
            }
        }

class MaintenanceKPIDashboard(models.Model):
    _name = 'maintenance.kpi.dashboard'
    _description = 'Maintenance KPI Dashboard'

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
