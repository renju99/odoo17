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