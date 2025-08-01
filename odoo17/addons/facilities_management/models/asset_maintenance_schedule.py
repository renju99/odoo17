# models/asset_maintenance_schedule.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class AssetMaintenanceSchedule(models.Model):
    _name = 'asset.maintenance.schedule'
    _description = 'Asset Maintenance Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Schedule Name', required=True, tracking=True)
    asset_id = fields.Many2one('facilities.asset', string='Asset', required=True, tracking=True, ondelete='restrict')
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
        ('inspection', 'Inspection'),
    ], string='Maintenance Type', required=True, default='preventive', tracking=True)

    interval_number = fields.Integer(string='Repeat Every', default=1, required=True, tracking=True)
    interval_type = fields.Selection([
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('quarterly', 'Quarter(s)'),
        ('yearly', 'Year(s)'),
    ], string='Recurrence', default='monthly', required=True, tracking=True)

    last_maintenance_date = fields.Date(string='Last Maintenance Date', tracking=True)
    next_maintenance_date = fields.Date(string='Next Scheduled Date', compute='_compute_next_maintenance_date', store=True, tracking=True, readonly=False)
    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=True, tracking=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='planned', tracking=True)

    job_plan_id = fields.Many2one('maintenance.job.plan', string='Job Plan',
                                  help="Select a job plan to associate with this maintenance schedule. "
                                       "Tasks from this plan will be copied to generated work orders.")

    workorder_ids = fields.One2many('maintenance.workorder', 'schedule_id', string='Generated Work Orders')
    workorder_count = fields.Integer(compute='_compute_workorder_count', string='Work Orders')

    _sql_constraints = [
        ('asset_type_unique_per_asset', 'unique(asset_id, maintenance_type, active)', 'A schedule of this type already exists for this active asset!'),
    ]

    @api.depends('last_maintenance_date', 'interval_number', 'interval_type')
    def _compute_next_maintenance_date(self):
        for rec in self:
            if rec.last_maintenance_date and rec.interval_number > 0:
                current_date = rec.last_maintenance_date
                if rec.interval_type == 'daily':
                    rec.next_maintenance_date = current_date + relativedelta(days=rec.interval_number)
                elif rec.interval_type == 'weekly':
                    rec.next_maintenance_date = current_date + relativedelta(weeks=rec.interval_number)
                elif rec.interval_type == 'monthly':
                    rec.next_maintenance_date = current_date + relativedelta(months=rec.interval_number)
                elif rec.interval_type == 'quarterly':
                    rec.next_maintenance_date = current_date + relativedelta(months=rec.interval_number * 3)
                elif rec.interval_type == 'yearly':
                    rec.next_maintenance_date = current_date + relativedelta(years=rec.interval_number)
                else:
                    rec.next_maintenance_date = False
            else:
                rec.next_maintenance_date = False

    @api.depends('workorder_ids')
    def _compute_workorder_count(self):
        for rec in self:
            rec.workorder_count = len(rec.workorder_ids)

    def action_generate_work_order(self):
        """Generates a work order for the maintenance schedule."""
        for schedule in self:
            if not schedule.active:
                raise UserError(_("Cannot generate a work order for an inactive schedule."))
            if not schedule.next_maintenance_date:
                raise UserError(_("Next maintenance date is not set for the schedule: %s.") % schedule.name)

            # Create the work order
            work_order_vals = {
                'name': _('New'),
                'asset_id': schedule.asset_id.id,
                'schedule_id': schedule.id,
                'work_order_type': schedule.maintenance_type,
                'start_date': schedule.next_maintenance_date,
                'job_plan_id': schedule.job_plan_id.id if schedule.job_plan_id else False,
            }
            work_order = self.env['maintenance.workorder'].create(work_order_vals)

            # Update the last maintenance date and compute the next maintenance date
            schedule.last_maintenance_date = schedule.next_maintenance_date
            schedule._compute_next_maintenance_date()

            # Log the creation
            schedule.message_post(body=_("Work order %s has been generated.") % work_order.name)

    def toggle_active(self):
        """Toggle the active state of the maintenance schedule"""
        for schedule in self:
            schedule.active = not schedule.active
            if schedule.active:
                schedule.message_post(body=_("Maintenance schedule activated"))
            else:
                schedule.message_post(body=_("Maintenance schedule deactivated"))

    @api.model
    def _generate_preventive_workorders(self):
        """Cron job method to generate preventive maintenance work orders"""
        today = fields.Date.today()
        schedules = self.search([
            ('active', '=', True),
            ('maintenance_type', '=', 'preventive'),
            ('next_maintenance_date', '<=', today),
            ('status', 'in', ['planned', 'done'])
        ])
        
        generated_count = 0
        for schedule in schedules:
            try:
                # Check if a work order already exists for this schedule and date
                existing_workorder = self.env['maintenance.workorder'].search([
                    ('schedule_id', '=', schedule.id),
                    ('start_date', '=', schedule.next_maintenance_date),
                    ('state', 'not in', ['cancelled'])
                ], limit=1)
                
                if not existing_workorder:
                    schedule.action_generate_work_order()
                    generated_count += 1
                    
            except Exception as e:
                _logger.error(f"Error generating work order for schedule {schedule.name}: {str(e)}")
                continue
        
        _logger.info(f"Generated {generated_count} preventive maintenance work orders")
        return generated_count

    @api.model
    def send_maintenance_reminder(self):
        """Send maintenance reminders for upcoming scheduled maintenance"""
        today = fields.Date.today()
        reminder_date = today + timedelta(days=7)  # Send reminders 7 days in advance
        
        schedules = self.search([
            ('active', '=', True),
            ('next_maintenance_date', '=', reminder_date),
            ('status', 'in', ['planned'])
        ])
        
        sent_count = 0
        for schedule in schedules:
            try:
                # Send email notification to responsible person
                if schedule.asset_id.responsible_id:
                    template = self.env.ref('facilities_management.email_template_maintenance_reminder', raise_if_not_found=False)
                    if template:
                        template.with_context(
                            schedule_name=schedule.name,
                            asset_name=schedule.asset_id.name,
                            next_maintenance_date=schedule.next_maintenance_date
                        ).send_mail(schedule.id, force_send=True)
                        sent_count += 1
                        
            except Exception as e:
                _logger.error(f"Error sending maintenance reminder for schedule {schedule.name}: {str(e)}")
                continue
        
        _logger.info(f"Sent {sent_count} maintenance reminders")
        return sent_count