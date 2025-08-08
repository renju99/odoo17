from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, MissingError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class MaintenanceWorkOrder(models.Model):
    _name = 'maintenance.workorder'
    _description = 'Maintenance Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char(string='Work Order', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    asset_id = fields.Many2one('facilities.asset', string='Asset', required=True, tracking=True)
    schedule_id = fields.Many2one('asset.maintenance.schedule', string='Maintenance Schedule', tracking=True)
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
        ('inspection', 'Inspection')
    ], string='Maintenance Type', required=True, default='corrective', tracking=True)
    work_order_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
        ('inspection', 'Inspection')
    ], string='Work Order Type', required=True, default='corrective', tracking=True)

    # Job Plan and Schedule Fields
    job_plan_id = fields.Many2one('maintenance.job.plan', string='Job Plan', tracking=True)
    section_ids = fields.One2many('maintenance.workorder.section', 'workorder_id', string='Sections')

    # SLA and KPI Fields
    sla_id = fields.Many2one('facilities.sla', string='SLA', tracking=True)
    sla_deadline = fields.Datetime(string='SLA Deadline', compute='_compute_sla_deadline', store=True)
    sla_status = fields.Selection([
        ('on_time', 'On Time'),
        ('at_risk', 'At Risk'),
        ('breached', 'Breached'),
        ('completed', 'Completed')
    ], string='SLA Status', compute='_compute_sla_status', store=True)
    sla_breach_time = fields.Datetime(string='SLA Breach Time', readonly=True)
    sla_escalation_level = fields.Integer(string='Escalation Level', default=0)

    # KPI Metrics
    mttr = fields.Float(string='MTTR (Hours)', compute='_compute_mttr', store=True)
    first_time_fix = fields.Boolean(string='First Time Fix', default=True)
    downtime_hours = fields.Float(string='Downtime Hours', compute='_compute_downtime_hours', store=True)
    cost_per_workorder = fields.Monetary(string='Cost per Work Order', currency_field='currency_id',
                                         compute='_compute_cost_per_workorder', store=True)

    # Time Tracking
    start_date = fields.Date(string='Start Date', tracking=True)
    start_time = fields.Datetime(string='Start Time', tracking=True)
    end_time = fields.Datetime(string='End Time', tracking=True)
    actual_start_date = fields.Datetime(string='Actual Start Date', tracking=True)
    actual_end_date = fields.Datetime(string='Actual End Date', tracking=True)
    actual_duration = fields.Float(string='Actual Duration (Hours)', compute='_compute_actual_duration', store=True)
    estimated_duration = fields.Float(string='Estimated Duration (Hours)', tracking=True)

    # Resource Utilization
    technician_ids = fields.Many2many('hr.employee', string='Assigned Technicians', tracking=True)
    team_id = fields.Many2one('maintenance.team', string='Maintenance Team', tracking=True)
    skill_requirements = fields.Many2many('hr.skill', string='Required Skills')
    skill_match_score = fields.Float(string='Skill Match Score', compute='_compute_skill_match_score')

    # Cost Tracking
    labor_cost = fields.Monetary(string='Labor Cost', currency_field='currency_id', tracking=True)
    parts_cost = fields.Monetary(string='Parts Cost', currency_field='currency_id', tracking=True)
    total_cost = fields.Monetary(string='Total Cost', currency_field='currency_id',
                                 compute='_compute_total_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Priority and Criticality
    priority = fields.Selection([
        ('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High'), ('4', 'Critical')
    ], string='Priority', default='2', tracking=True)
    asset_criticality = fields.Selection(related='asset_id.criticality', store=True)

    # Dynamic SLA Assignment
    auto_sla_assignment = fields.Boolean(string='Auto SLA Assignment', default=True)
    sla_assignment_rule = fields.Selection([
        ('asset_criticality', 'Asset Criticality'),
        ('maintenance_type', 'Maintenance Type'),
        ('priority', 'Priority'),
        ('location', 'Location'),
        ('custom', 'Custom Rule')
    ], string='SLA Assignment Rule', default='asset_criticality')

    # Escalation Workflow
    escalation_triggered = fields.Boolean(string='Escalation Triggered', default=False)
    escalation_history = fields.One2many('maintenance.escalation.log', 'workorder_id', string='Escalation History')
    next_escalation_time = fields.Datetime(string='Next Escalation Time', compute='_compute_next_escalation_time')

    # Additional Fields
    description = fields.Text(string='Description', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Approval Workflow
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('supervisor', 'Supervisor Review'),
        ('manager', 'Manager Review'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('refused', 'Refused'),
        ('escalated', 'Escalated'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True)

    # Approval Related Fields
    submitted_by_id = fields.Many2one('res.users', string='Submitted By', readonly=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By', readonly=True)
    approval_request_date = fields.Datetime(string='Approval Request Date', readonly=True)
    escalation_deadline = fields.Datetime(string='Escalation Deadline', readonly=True)
    escalation_to_id = fields.Many2one('res.users', string='Escalated To', readonly=True)
    escalation_count = fields.Integer(string='Escalation Count', default=0, readonly=True)

    # Additional Work Order Fields
    facility_id = fields.Many2one('facilities.facility', string='Facility', related='asset_id.facility_id', store=True)
    room_id = fields.Many2one('facilities.room', string='Room', related='asset_id.room_id', store=True)
    building_id = fields.Many2one('facilities.building', string='Building', related='asset_id.building_id', store=True)
    floor_id = fields.Many2one('facilities.floor', string='Floor', related='asset_id.floor_id', store=True)
    service_type = fields.Selection([
        ('repair', 'Repair'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
        ('installation', 'Installation'),
        ('replacement', 'Replacement'),
        ('calibration', 'Calibration'),
        ('testing', 'Testing'),
        ('cleaning', 'Cleaning')
    ], string='Service Type', tracking=True)
    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team', tracking=True)
    technician_id = fields.Many2one('hr.employee', string='Technician', tracking=True)
    supervisor_id = fields.Many2one('hr.employee', string='Supervisor', tracking=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    picking_count = fields.Integer(string='Parts Transfers', compute='_compute_picking_count')
    all_tasks_completed = fields.Boolean(string='All Tasks Completed', compute='_compute_all_tasks_completed')

    # SLA Response and Resolution Fields
    sla_response_deadline = fields.Datetime(string='SLA Response Deadline', compute='_compute_sla_response_deadline',
                                            store=True)
    sla_resolution_deadline = fields.Datetime(string='SLA Resolution Deadline',
                                              compute='_compute_sla_resolution_deadline', store=True)
    sla_response_status = fields.Selection([
        ('on_time', 'On Time'),
        ('at_risk', 'At Risk'),
        ('breached', 'Breached'),
        ('completed', 'Completed')
    ], string='SLA Response Status', compute='_compute_sla_response_status', store=True)
    sla_resolution_status = fields.Selection([
        ('on_time', 'On Time'),
        ('at_risk', 'At Risk'),
        ('breached', 'Breached'),
        ('completed', 'Completed')
    ], string='SLA Resolution Status', compute='_compute_sla_resolution_status', store=True)

    # Work Done and Related Fields
    work_done = fields.Text(string='Work Done', help='Description of work completed')
    assignment_ids = fields.One2many('maintenance.workorder.assignment', 'workorder_id',
                                     string='Technician Assignments')
    parts_used_ids = fields.One2many('maintenance.workorder.part_line', 'workorder_id', string='Parts Used')
    permit_ids = fields.One2many('maintenance.workorder.permit', 'workorder_id', string='Permits')
    workorder_task_ids = fields.One2many('maintenance.workorder.task', 'workorder_id', string='Work Order Tasks')

    # Status field for view compatibility
    status = fields.Selection(related='state', string='Status', store=True)

    show_job_plan_warning = fields.Boolean(
        string='Show Job Plan Warning',
        compute='_compute_show_job_plan_warning',
        store=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.workorder') or _('New')

            # Auto-assign SLA if enabled
            if vals.get('auto_sla_assignment', True):
                vals['sla_id'] = self._get_appropriate_sla(vals)

        workorders = super().create(vals_list)

        # Set SLA deadline for all created workorders
        for workorder in workorders:
            if workorder.sla_id:
                workorder._compute_sla_deadline()

        return workorders

    @api.depends('sla_id', 'create_date')
    def _compute_sla_deadline(self):
        for workorder in self:
            try:
                if workorder.create_date and workorder.sla_id and workorder.sla_id.response_time_hours:
                    workorder.sla_deadline = workorder.create_date + timedelta(
                        hours=workorder.sla_id.response_time_hours)
                else:
                    workorder.sla_deadline = False
            except MissingError:
                workorder.sla_deadline = False

    @api.depends('sla_deadline', 'state', 'end_time')
    def _compute_sla_status(self):
        for workorder in self:
            try:
                if not workorder.sla_deadline or workorder.state == 'completed':
                    workorder.sla_status = 'completed' if workorder.state == 'completed' else 'on_time'
                    continue

                now = fields.Datetime.now()
                time_remaining = (workorder.sla_deadline - now).total_seconds() / 3600

                if workorder.state == 'completed':
                    workorder.sla_status = 'completed'
                elif time_remaining < 0:
                    workorder.sla_status = 'breached'
                    if not workorder.sla_breach_time:
                        workorder.sla_breach_time = now
                elif workorder.sla_id and time_remaining < workorder.sla_id.warning_threshold_hours:
                    workorder.sla_status = 'at_risk'
                else:
                    workorder.sla_status = 'on_time'
            except MissingError:
                workorder.sla_status = 'on_time'

    @api.depends('actual_start_date', 'actual_end_date')
    def _compute_actual_duration(self):
        for workorder in self:
            if workorder.actual_start_date and workorder.actual_end_date:
                duration = (workorder.actual_end_date - workorder.actual_start_date).total_seconds() / 3600
                workorder.actual_duration = duration
            else:
                workorder.actual_duration = 0.0

    @api.depends('actual_duration')
    def _compute_mttr(self):
        for workorder in self:
            workorder.mttr = workorder.actual_duration

    @api.depends('actual_start_date', 'actual_end_date', 'asset_id')
    def _compute_downtime_hours(self):
        for workorder in self:
            if workorder.actual_start_date and workorder.actual_end_date:
                downtime = (workorder.actual_end_date - workorder.actual_start_date).total_seconds() / 3600
                workorder.downtime_hours = downtime
            else:
                workorder.downtime_hours = 0.0

    @api.depends('labor_cost', 'parts_cost')
    def _compute_total_cost(self):
        for workorder in self:
            workorder.total_cost = workorder.labor_cost + workorder.parts_cost

    @api.depends('total_cost')
    def _compute_cost_per_workorder(self):
        for workorder in self:
            workorder.cost_per_workorder = workorder.total_cost

    @api.depends('technician_ids', 'skill_requirements')
    def _compute_skill_match_score(self):
        for workorder in self:
            if not workorder.technician_ids or not workorder.skill_requirements:
                workorder.skill_match_score = 0.0
                continue

            total_skills = len(workorder.skill_requirements)
            matched_skills = 0

            for technician in workorder.technician_ids:
                technician_skills = technician.skill_ids.mapped('name')
                for required_skill in workorder.skill_requirements:
                    if required_skill.name in technician_skills:
                        matched_skills += 1

            workorder.skill_match_score = (matched_skills / total_skills) * 100 if total_skills > 0 else 0.0

    @api.depends('sla_deadline', 'sla_escalation_level')
    def _compute_next_escalation_time(self):
        for workorder in self:
            try:
                if workorder.sla_deadline and workorder.sla_escalation_level < 3:
                    escalation_delay = workorder.sla_id.escalation_delay_hours if workorder.sla_id else 24
                    workorder.next_escalation_time = workorder.sla_deadline + timedelta(hours=escalation_delay)
                else:
                    workorder.next_escalation_time = False
            except MissingError:
                workorder.next_escalation_time = False

    def _get_appropriate_sla(self, vals):
        """Dynamically assign SLA based on rules"""
        asset_id = vals.get('asset_id')
        maintenance_type = vals.get('maintenance_type')
        priority = vals.get('priority', '2')

        if not asset_id:
            return False

        asset = self.env['facilities.asset'].browse(asset_id)
        assignment_rule = vals.get('sla_assignment_rule', 'asset_criticality')

        domain = [('active', '=', True)]

        if assignment_rule == 'asset_criticality':
            domain.append(('asset_criticality', '=', asset.criticality))
        elif assignment_rule == 'maintenance_type':
            domain.append(('maintenance_type', '=', maintenance_type))
        elif assignment_rule == 'priority':
            domain.append(('priority_level', '=', priority))
        elif assignment_rule == 'location':
            domain.append(('facility_ids', 'in', asset.facility_id.id))

        sla = self.env['facilities.sla'].search(domain, limit=1, order='priority desc')
        return sla.id if sla else False

    def action_start_work(self):
        """Start work order and record start time"""
        for workorder in self:
            workorder.write({
                'state': 'in_progress',
                'start_time': fields.Datetime.now(),
                'actual_start_date': fields.Datetime.now()
            })
            workorder._check_sla_escalation()

    def action_complete_work(self):
        """Complete work order and record end time"""
        for workorder in self:
            workorder.write({
                'state': 'completed',
                'end_time': fields.Datetime.now(),
                'actual_end_date': fields.Datetime.now()
            })
            workorder._compute_kpis()

    def action_assign_technicians(self):
        """Auto-assign technicians based on skills and availability"""
        for workorder in self:
            if workorder.skill_requirements:
                available_technicians = self.env['hr.employee'].search([
                    ('skill_ids', 'in', workorder.skill_requirements.ids),
                    ('maintenance_team_id', '=', workorder.team_id.id)
                ])

                if available_technicians:
                    workorder.technician_ids = available_technicians[:3]  # Assign up to 3 technicians

    def _check_sla_escalation(self):
        for workorder in self:
            if workorder.sla_status == 'breached' and not workorder.escalation_triggered:
                workorder._trigger_escalation()

    def _trigger_escalation(self):
        for workorder in self:
            workorder.escalation_triggered = True
            workorder.sla_escalation_level += 1

            # Create escalation log
            self.env['maintenance.escalation.log'].create({
                'workorder_id': workorder.id,
                'escalation_level': workorder.sla_escalation_level,
                'trigger_time': fields.Datetime.now(),
                'reason': f'SLA breached - {workorder.sla_status}'
            })

            workorder._send_escalation_notification()

    def _send_escalation_notification(self):
        for workorder in self:
            managers = self.env['res.users'].search([('groups_id', 'in',
                                                      self.env.ref('facilities_management.group_facility_manager').id)])

            for manager in managers:
                workorder.message_post(
                    body=f'SLA Escalation: Work Order {workorder.name} has breached SLA deadline.',
                    partner_ids=[manager.partner_id.id]
                )

    def _compute_kpis(self):
        for workorder in self:
            if workorder.state == 'completed':
                workorder.mttr = workorder.actual_duration
                previous_workorders = self.search([
                    ('asset_id', '=', workorder.asset_id.id),
                    ('state', '=', 'completed'),
                    ('id', '!=', workorder.id)
                ], order='end_time desc', limit=1)
                if not previous_workorders:
                    workorder.first_time_fix = True
                else:
                    workorder.first_time_fix = False

    @api.model
    def cron_check_sla_breaches(self):
        workorders = self.search([
            ('state', 'not in', ['completed', 'cancelled']),
            ('sla_deadline', '<', fields.Datetime.now())
        ])
        for workorder in workorders:
            workorder._check_sla_escalation()

    def action_view_kpi_dashboard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'KPI Dashboard',
            'res_model': 'maintenance.kpi.dashboard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_workorder_id': self.id}
        }

    def action_assign_technician(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Technician',
            'res_model': 'assign.technician.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_workorder_id': self.id}
        }

    def action_report_downtime(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Downtime',
            'res_model': 'asset.downtime.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_workorder_id': self.id,
                'default_asset_id': self.asset_id.id
            }
        }

    def action_mark_done(self):
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Work order must be in progress to mark as done."))
        self.write({
            'state': 'completed',
            'end_time': fields.Datetime.now(),
            'actual_end_date': fields.Datetime.now()
        })
        self._compute_kpis()
        self.message_post(body=_("Work order marked as completed"))

    def action_view_picking(self):
        self.ensure_one()
        pickings = self.env['stock.picking'].search([
            ('move_ids.workorder_id', '=', self.id)
        ])
        if not pickings:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Transfers'),
                    'message': _('No stock transfers found for this work order.'),
                    'type': 'warning'
                }
            }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Transfers',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', pickings.ids)],
            'context': {'search_default_workorder_id': self.id}
        }

    def action_submit_for_approval(self):
        self.ensure_one()
        self.write({
            'approval_state': 'submitted',
            'submitted_by_id': self.env.user.id,
            'approval_request_date': fields.Datetime.now()
        })
        self.message_post(body=_("Work order submitted for approval by %s") % self.env.user.name)

    def action_supervisor_approve(self):
        self.ensure_one()
        self.write({
            'approval_state': 'supervisor',
            'approved_by_id': self.env.user.id
        })
        self.message_post(body=_("Work order approved by supervisor %s") % self.env.user.name)

    def action_manager_approve(self):
        self.ensure_one()
        self.write({
            'approval_state': 'manager',
            'approved_by_id': self.env.user.id
        })
        self.message_post(body=_("Work order approved by manager %s") % self.env.user.name)

    def action_fully_approve(self):
        self.ensure_one()
        self.write({
            'approval_state': 'approved',
            'approved_by_id': self.env.user.id
        })
        self.message_post(body=_("Work order fully approved by %s") % self.env.user.name)

    def action_refuse(self):
        self.ensure_one()
        self.write({
            'approval_state': 'refused',
            'approved_by_id': self.env.user.id
        })
        self.message_post(body=_("Work order refused by %s") % self.env.user.name)

    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({
            'approval_state': 'draft'
        })
        self.message_post(body=_("Work order reset to draft by %s") % self.env.user.name)

    def action_escalate(self):
        self.ensure_one()
        self.write({
            'approval_state': 'escalated',
            'escalation_count': self.escalation_count + 1
        })
        self.message_post(body=_("Work order manually escalated by %s") % self.env.user.name)

    def action_start_progress(self):
        self.ensure_one()
        if self.approval_state not in ['approved', 'draft', 'submitted', 'supervisor', 'manager']:
            raise UserError(_("Work order must be in an approvable state before starting progress."))
        
        # Auto-approve if not already approved
        if self.approval_state != 'approved':
            self.write({
                'approval_state': 'approved',
                'approved_by_id': self.env.user.id
            })
        
        self.write({
            'approval_state': 'in_progress',
            'state': 'in_progress',
            'actual_start_date': fields.Datetime.now()
        })
        self.message_post(body=_("Work order started by %s") % self.env.user.name)

    def action_quick_start(self):
        """Quick start work order - bypass approval if needed"""
        self.ensure_one()
        if self.state not in ['draft', 'assigned']:
            raise UserError(_("Work order must be in draft or assigned state to quick start."))
        
        # Auto-approve if in draft approval state
        if self.approval_state == 'draft':
            self.write({
                'approval_state': 'approved',
                'approved_by_id': self.env.user.id
            })
        
        self.write({
            'approval_state': 'in_progress',
            'state': 'in_progress',
            'actual_start_date': fields.Datetime.now()
        })
        self.message_post(body=_("Work order quick started by %s (bypassing approval)") % self.env.user.name)

    def action_resume_work(self):
        """Resume work order from on-hold state"""
        self.ensure_one()
        if self.state != 'on_hold':
            raise UserError(_("Work order must be on hold to resume."))
        
        self.write({
            'state': 'in_progress',
            'approval_state': 'in_progress'
        })
        self.message_post(body=_("Work order resumed by %s") % self.env.user.name)

    def action_complete(self):
        self.ensure_one()
        if self.approval_state != 'in_progress':
            raise UserError(_("Work order must be in progress to mark as completed."))
        self.write({
            'approval_state': 'done',
            'state': 'completed',
            'actual_end_date': fields.Datetime.now()
        })
        self.message_post(body=_("Work order completed by %s") % self.env.user.name)

    def action_stop_work(self):
        """Stop work and record the stop time"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Only work orders in progress can be stopped."))
        
        self.write({
            'state': 'on_hold',
            'actual_end_date': fields.Datetime.now()
        })
        self.message_post(body=_("Work stopped by %s") % self.env.user.name)

    def action_cancel(self):
        self.ensure_one()
        self.write({
            'approval_state': 'cancelled',
            'state': 'cancelled'
        })
        self.message_post(body=_("Work order cancelled by %s") % self.env.user.name)

    def action_toggle_task_completion(self, task_id):
        """Toggle task completion from mobile view"""
        self.ensure_one()
        task = self.env['maintenance.workorder.task'].browse(task_id)
        if task and task.workorder_id == self:
            task.toggle_task_completion()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Task Updated'),
                    'message': _('Task "%s" marked as %s') % (task.name, task.is_done and 'completed' or 'pending'),
                    'type': 'success',
                }
            }
        return False

    @api.depends('section_ids.task_ids.is_done', 'workorder_task_ids.is_done')
    def _compute_all_tasks_completed(self):
        for workorder in self:
            sectioned_tasks = workorder.section_ids.mapped('task_ids')
            flat_tasks = workorder.workorder_task_ids
            all_tasks = sectioned_tasks | flat_tasks
            if not all_tasks:
                workorder.all_tasks_completed = True
            else:
                workorder.all_tasks_completed = all(task.is_done for task in all_tasks if task.is_checklist_item)

    def _compute_picking_count(self):
        for workorder in self:
            pickings = self.env['stock.picking'].search([
                ('move_ids.workorder_id', '=', workorder.id)
            ])
            workorder.picking_count = len(pickings)

    @api.depends('sla_id', 'create_date')
    def _compute_sla_response_deadline(self):
        for workorder in self:
            try:
                if workorder.sla_id and workorder.create_date:
                    workorder.sla_response_deadline = workorder.create_date + timedelta(
                        hours=workorder.sla_id.response_time_hours)
                else:
                    workorder.sla_response_deadline = False
            except MissingError:
                workorder.sla_response_deadline = False

    @api.depends('sla_id', 'create_date')
    def _compute_sla_resolution_deadline(self):
        for workorder in self:
            try:
                if workorder.sla_id and workorder.create_date:
                    workorder.sla_resolution_deadline = workorder.create_date + timedelta(
                        hours=workorder.sla_id.resolution_time_hours)
                else:
                    workorder.sla_resolution_deadline = False
            except MissingError:
                workorder.sla_resolution_deadline = False

    @api.depends('sla_response_deadline', 'state')
    def _compute_sla_response_status(self):
        for workorder in self:
            try:
                if not workorder.sla_response_deadline:
                    workorder.sla_response_status = 'on_time'
                    continue

                now = fields.Datetime.now()
                time_remaining = (workorder.sla_response_deadline - now).total_seconds() / 3600

                if workorder.state == 'completed':
                    workorder.sla_response_status = 'completed'
                elif time_remaining < 0:
                    workorder.sla_response_status = 'breached'
                elif workorder.sla_id and time_remaining < workorder.sla_id.warning_threshold_hours:
                    workorder.sla_response_status = 'at_risk'
                else:
                    workorder.sla_response_status = 'on_time'
            except MissingError:
                workorder.sla_response_status = 'on_time'

    @api.depends('sla_resolution_deadline', 'state')
    def _compute_sla_resolution_status(self):
        for workorder in self:
            try:
                if not workorder.sla_resolution_deadline:
                    workorder.sla_resolution_status = 'on_time'
                    continue

                now = fields.Datetime.now()
                time_remaining = (workorder.sla_resolution_deadline - now).total_seconds() / 3600

                if workorder.state == 'completed':
                    workorder.sla_resolution_status = 'completed'
                elif time_remaining < 0:
                    workorder.sla_resolution_status = 'breached'
                elif workorder.sla_id and time_remaining < workorder.sla_id.warning_threshold_hours:
                    workorder.sla_resolution_status = 'at_risk'
                else:
                    workorder.sla_resolution_status = 'on_time'
            except MissingError:
                workorder.sla_resolution_status = 'on_time'

    @api.depends('work_order_type', 'job_plan_id')
    def _compute_show_job_plan_warning(self):
        for rec in self:
            rec.show_job_plan_warning = (
                rec.work_order_type == 'preventive' and not rec.job_plan_id
            )


class MaintenanceEscalationLog(models.Model):
    _name = 'maintenance.escalation.log'
    _description = 'Maintenance Escalation Log'
    _order = 'trigger_time desc'

    workorder_id = fields.Many2one('maintenance.workorder', string='Work Order', required=True)
    escalation_level = fields.Integer(string='Escalation Level', required=True)
    trigger_time = fields.Datetime(string='Trigger Time', required=True)
    reason = fields.Text(string='Reason', required=True)
    action_taken = fields.Text(string='Action Taken')
    resolved_by_id = fields.Many2one('res.users', string='Resolved By')
    resolution_time = fields.Datetime(string='Resolution Time')