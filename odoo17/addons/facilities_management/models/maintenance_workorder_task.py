from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

class MaintenanceWorkorder(models.Model):
    _inherit = 'maintenance.workorder'

    show_tasks_to_complete_btn = fields.Boolean(
        compute="_compute_show_tasks_to_complete_btn",
        string="Show Tasks to Complete Button"
    )

    @api.depends('work_order_type')
    def _compute_show_tasks_to_complete_btn(self):
        for rec in self:
            rec.show_tasks_to_complete_btn = rec.work_order_type == 'preventive'

    def action_open_job_plan_tasks_mobile(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks to Complete'),
            'res_model': 'maintenance.workorder.task',
            'view_mode': 'tree,form',
            'domain': [('workorder_id', '=', self.id), ('is_done', '=', False)],
            'context': {'default_workorder_id': self.id},
            'target': 'current',
        }

class MaintenanceWorkorderTask(models.Model):
    _name = 'maintenance.workorder.task'
    _description = 'Maintenance Work Order Task'
    _order = 'section_id, sequence, id'

    workorder_id = fields.Many2one('maintenance.workorder', string='Work Order', required=True, ondelete='cascade')
    section_id = fields.Many2one('maintenance.workorder.section', string='Section', ondelete='cascade')
    name = fields.Char(string='Task Description', required=True, readonly=True)
    sequence = fields.Integer(string='Sequence', default=10, readonly=True)
    is_done = fields.Boolean(string='Completed', default=False)
    description = fields.Text(string='Instructions', readonly=True)
    notes = fields.Text(string='Technician Notes', help="Notes added by the technician during execution.")
    is_checklist_item = fields.Boolean(string='Checklist Item', default=True, readonly=True)
    before_image = fields.Binary(string="Before Image", attachment=True, help="Image of the asset/area before task execution.")
    before_image_filename = fields.Char(string="Before Image Filename")
    after_image = fields.Binary(string="After Image", attachment=True, help="Image of the asset/area after task execution.")
    after_image_filename = fields.Char(string="After Image Filename")
    duration = fields.Float(string='Estimated Duration (hours)', readonly=True)
    tools_materials = fields.Text(string='Tools/Materials Required', readonly=True)
    responsible_id = fields.Many2one('hr.employee', string='Responsible Personnel (Role)', readonly=True)
    product_id = fields.Many2one('product.product', string='Required Part', readonly=True)
    quantity = fields.Float(string='Quantity', default=1.0, readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    frequency_type = fields.Selection(
        [
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        string='Frequency Type',
        help="How often this task should be performed.",
        readonly=True,
    )

    @api.constrains('is_done')
    def _check_workorder_status_for_task_done(self):
        for rec in self:
            if rec.is_done and rec.workorder_id.state != 'in_progress':
                raise ValidationError(_("Tasks can only be marked as completed when the Work Order is 'In Progress'."))

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        for vals in vals_list:
            workorder = self.env['maintenance.workorder'].browse(vals.get('workorder_id'))
            if workorder and workorder.state != 'draft':
                raise UserError(_("You cannot add tasks to a work order that is not in draft."))
        
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.workorder_id.state != 'draft':
                raise UserError(_("You cannot remove tasks from a work order that is not in draft."))
        return super().unlink()