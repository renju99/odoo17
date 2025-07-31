from odoo import models, fields, api, _
from datetime import datetime
import io, base64
from collections import Counter
import calendar

class MonthlyBuildingReportWizard(models.TransientModel):
    _name = 'monthly.building.report.wizard'
    _description = 'Monthly Building Maintenance Report Wizard'

    building_id = fields.Many2one('facilities.building', string='Building', required=True)
    year = fields.Integer('Year', required=True, default=lambda self: datetime.now().year)
    month = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1, 13)],
        string='Month', required=True, default=lambda self: str(datetime.now().month))

    def action_generate_pdf_report(self):
        year, month = int(self.year), int(self.month)
        start_dt = datetime(year, month, 1)
        end_dt = datetime(year + (month == 12), (month % 12) + 1, 1)
        workorders = self.env['maintenance.workorder'].search([
            ('building_id', '=', self.building_id.id),
            ('create_date', '>=', start_dt),
            ('create_date', '<', end_dt),
        ])

        # Mappings for friendly names
        STATUS_LABELS = {
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'draft': 'Draft',
            'cancelled': 'Cancelled',
            'assigned': 'Assigned',
            'on_hold': 'On Hold',
        }
        PRIORITY_LABELS = {
            '0': 'Very Low',
            '1': 'Low',
            '2': 'Normal',
            '3': 'High',
            '4': 'Critical',
        }
        TYPE_LABELS = {
            'corrective': 'Corrective',
            'preventive': 'Preventive',
            'inspection': 'Inspection',
        }
        SLA_LABELS = {
            'on_time': 'On Time',
            'at_risk': 'At Risk',
            'breached': 'Breached',
            'completed': 'Completed',
        }

        # Map technical to friendly names for counts
        status_counts = Counter(w.state for w in workorders)
        status_counts_friendly = Counter()
        for k, v in status_counts.items():
            status_counts_friendly[STATUS_LABELS.get(k, k)] = v

        type_counts = Counter(w.work_order_type for w in workorders)
        type_counts_friendly = Counter()
        for k, v in type_counts.items():
            type_counts_friendly[TYPE_LABELS.get(k, k)] = v

        priority_counts = Counter(w.priority for w in workorders)
        priority_counts_friendly = Counter()
        for k, v in priority_counts.items():
            priority_counts_friendly[PRIORITY_LABELS.get(k, k)] = v

        asset_counts = Counter(w.asset_id.name for w in workorders if w.asset_id)
        room_counts = Counter(w.room_id.name for w in workorders if w.room_id)
        parts_counts = Counter()
        for wo in workorders:
            for part in getattr(wo, 'parts_used_ids', []):
                parts_counts[getattr(part, 'product_id', None) and part.product_id.name or ''] += getattr(part, 'quantity', 0)
        completion_times = [
            (wo.actual_end_date - wo.actual_start_date).total_seconds()/3600
            for wo in workorders
            if wo.state == 'completed' and wo.actual_start_date and wo.actual_end_date
        ]
        avg_completion_time = round(sum(completion_times) / len(completion_times), 2) if completion_times else 0
        sla_status_counts = Counter(getattr(w, 'sla_resolution_status', None) for w in workorders)
        sla_status_counts_friendly = Counter()
        for k, v in sla_status_counts.items():
            sla_status_counts_friendly[SLA_LABELS.get(k, k)] = v

        desc_words = []
        for wo in workorders:
            if getattr(wo, 'description', None):
                desc_words += [w.lower() for w in wo.description.split() if len(w) > 4]
        issue_counts = Counter(desc_words)
        day_counts = Counter()
        for wo in workorders:
            if getattr(wo, 'create_date', None):
                day = wo.create_date.day
                day_counts[day] += 1
        top_assets = asset_counts.most_common(5)
        top_rooms = room_counts.most_common(5)
        top_parts = parts_counts.most_common(5)
        top_issues = issue_counts.most_common(5)

        # Pass all data to QWeb
        data = {
            'building': self.building_id.name,
            'year': self.year,
            'month': calendar.month_name[int(self.month)],
            'total': len(workorders),
            'status_counts': status_counts_friendly,
            'type_counts': type_counts_friendly,
            'priority_counts': priority_counts_friendly,
            'top_assets': top_assets,
            'top_rooms': top_rooms,
            'top_parts': top_parts,
            'top_issues': top_issues,
            'avg_completion_time': avg_completion_time,
            'sla_status_counts': sla_status_counts_friendly,
            'day_counts': dict(day_counts),
            'generated_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        return self.env.ref('facilities_management.monthly_building_report_pdf_action').report_action(self, data={'doc': data})