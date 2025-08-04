from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import re
import qrcode
import base64
from io import BytesIO
import json


class FacilitiesSpaceBooking(models.Model):
    _name = 'facilities.space.booking'
    _description = 'Space/Room Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char('Booking Reference', required=True, readonly=True, default=lambda self: _('New'))
    room_id = fields.Many2one('facilities.room', string='Room', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Booked By', default=lambda self: self.env.user, tracking=True)
    start_datetime = fields.Datetime('Start Time', required=True, tracking=True)
    end_datetime = fields.Datetime('End Time', required=True, tracking=True)
    purpose = fields.Char('Purpose', tracking=True)
    attendees = fields.Integer('Number of Attendees')
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')

    # Enhanced fields
    booking_type = fields.Selection([
        ('meeting', 'Meeting'),
        ('event', 'Event'),
        ('training', 'Training'),
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ], string='Booking Type', default='meeting', tracking=True, required=True)

    contact_email = fields.Char('Contact Email', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)

    # Recurrence fields
    is_recurring = fields.Boolean('Recurring Booking', tracking=True)
    recurrence_rule = fields.Char('Recurrence Rule',
                                  help="iCal-style recurrence rule (e.g., FREQ=WEEKLY;BYDAY=MO,WE,FR)")
    parent_booking_id = fields.Many2one('facilities.space.booking', string='Parent Booking')
    child_booking_ids = fields.One2many('facilities.space.booking', 'parent_booking_id', string='Child Bookings')

    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    # External guests
    is_external_guest = fields.Boolean('Has External Guests', tracking=True)
    external_guest_names = fields.Text('External Guest Names', help="List external guest names, one per line")

    # NEW ENHANCED FEATURES
    
    # QR Code Generation
    qr_code = fields.Binary('QR Code', compute='_compute_qr_code', store=True)
    qr_code_filename = fields.Char('QR Code Filename', default='booking_qr.png')
    
    # Booking Templates
    template_id = fields.Many2one('facilities.booking.template', string='Booking Template')
    is_template = fields.Boolean('Save as Template')
    template_name = fields.Char('Template Name')
    
    # Capacity Management
    required_capacity = fields.Integer('Required Capacity', default=1)
    room_capacity = fields.Integer('Room Capacity', related='room_id.capacity', store=True)
    capacity_utilization = fields.Float('Capacity Utilization %', compute='_compute_capacity_utilization', store=True)
    
    # Cost Calculation
    hourly_rate = fields.Float('Hourly Rate', related='room_id.hourly_rate', store=True)
    total_cost = fields.Float('Total Cost', compute='_compute_total_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # Room Equipment
    required_equipment_ids = fields.Many2many('facilities.room.equipment', string='Required Equipment')
    equipment_availability = fields.Text('Equipment Availability', compute='_compute_equipment_availability')
    
    # Check-in/Check-out
    check_in_time = fields.Datetime('Check-in Time')
    check_out_time = fields.Datetime('Check-out Time')
    auto_check_in = fields.Boolean('Auto Check-in', default=False)
    auto_check_out = fields.Boolean('Auto Check-out', default=False)
    
    # Approval Workflow
    approval_required = fields.Boolean('Approval Required', compute='_compute_approval_required', store=True)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Datetime('Approval Date')
    rejection_reason = fields.Text('Rejection Reason')
    
    # Integration Fields
    calendar_event_id = fields.Char('Calendar Event ID')
    external_booking_ref = fields.Char('External Booking Reference')
    portal_access_token = fields.Char('Portal Access Token', default=lambda self: self._generate_access_token())
    
    # Notification Settings
    notification_settings = fields.Text('Notification Settings', default='{"email": true, "sms": false, "app": true}')
    reminder_sent = fields.Boolean('Reminder Sent', default=False)
    
    # Priority and Rating
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='normal', string='Priority', tracking=True)
    
    rating = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐')
    ], string='Rating')
    feedback = fields.Text('Feedback')

    # Computed fields
    duration_hours = fields.Float('Duration (Hours)', compute='_compute_duration_hours', store=True)
    is_holiday_conflict = fields.Boolean('Holiday Conflict', compute='_compute_holiday_conflict')
    recurring_display = fields.Char('Recurrence', compute='_compute_recurring_display')
    booking_status_display = fields.Char('Status Display', compute='_compute_status_display')
    is_overdue = fields.Boolean('Is Overdue', compute='_compute_is_overdue', store=True)
    
    def _generate_access_token(self):
        import secrets
        return secrets.token_urlsafe(32)

    @api.depends('name', 'room_id', 'start_datetime')
    def _compute_qr_code(self):
        for booking in self:
            if booking.name and booking.room_id:
                qr_data = {
                    'booking_id': booking.id,
                    'booking_ref': booking.name,
                    'room': booking.room_id.name,
                    'start_time': booking.start_datetime.isoformat() if booking.start_datetime else '',
                    'access_token': booking.portal_access_token
                }
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(json.dumps(qr_data))
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                booking.qr_code = base64.b64encode(buffer.getvalue())
            else:
                booking.qr_code = False

    @api.depends('required_capacity', 'room_capacity')
    def _compute_capacity_utilization(self):
        for booking in self:
            if booking.room_capacity and booking.required_capacity:
                booking.capacity_utilization = (booking.required_capacity / booking.room_capacity) * 100
            else:
                booking.capacity_utilization = 0.0

    @api.depends('duration_hours', 'hourly_rate')
    def _compute_total_cost(self):
        for booking in self:
            booking.total_cost = booking.duration_hours * booking.hourly_rate

    @api.depends('required_equipment_ids')
    def _compute_equipment_availability(self):
        for booking in self:
            if booking.required_equipment_ids and booking.start_datetime and booking.end_datetime:
                availability_info = []
                for equipment in booking.required_equipment_ids:
                    # Check if equipment is available during booking time
                    conflicting_bookings = self.search([
                        ('id', '!=', booking.id),
                        ('required_equipment_ids', 'in', equipment.id),
                        ('state', 'in', ['confirmed', 'in_progress']),
                        ('start_datetime', '<', booking.end_datetime),
                        ('end_datetime', '>', booking.start_datetime),
                    ])
                    
                    if conflicting_bookings:
                        availability_info.append(f"{equipment.name}: Not Available (conflicting bookings)")
                    else:
                        availability_info.append(f"{equipment.name}: Available")
                
                booking.equipment_availability = '\n'.join(availability_info)
            else:
                booking.equipment_availability = ''

    @api.depends('booking_type', 'total_cost', 'duration_hours')
    def _compute_approval_required(self):
        for booking in self:
            # Approval required for events, high-cost bookings, or long duration
            booking.approval_required = (
                booking.booking_type == 'event' or 
                booking.total_cost > 1000 or 
                booking.duration_hours > 8
            )

    @api.depends('state', 'check_in_time', 'check_out_time')
    def _compute_status_display(self):
        for booking in self:
            if booking.state == 'confirmed' and booking.check_in_time:
                booking.booking_status_display = 'Checked In'
            elif booking.state == 'completed' and booking.check_out_time:
                booking.booking_status_display = 'Checked Out'
            else:
                booking.booking_status_display = dict(booking._fields['state'].selection).get(booking.state, booking.state)

    @api.depends('end_datetime', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for booking in self:
            booking.is_overdue = (
                booking.state in ['confirmed', 'in_progress'] and 
                booking.end_datetime and 
                booking.end_datetime < now
            )

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration_hours(self):
        for booking in self:
            if booking.start_datetime and booking.end_datetime:
                delta = booking.end_datetime - booking.start_datetime
                booking.duration_hours = delta.total_seconds() / 3600.0
            else:
                booking.duration_hours = 0.0

    @api.depends('start_datetime', 'end_datetime')
    def _compute_holiday_conflict(self):
        for booking in self:
            booking.is_holiday_conflict = False

    @api.depends('is_recurring', 'recurrence_rule')
    def _compute_recurring_display(self):
        for booking in self:
            if booking.is_recurring and booking.recurrence_rule:
                rule = booking.recurrence_rule
                if 'FREQ=DAILY' in rule:
                    booking.recurring_display = 'Daily'
                elif 'FREQ=WEEKLY' in rule:
                    booking.recurring_display = 'Weekly'
                elif 'FREQ=MONTHLY' in rule:
                    booking.recurring_display = 'Monthly'
                else:
                    booking.recurring_display = 'Custom'
            else:
                booking.recurring_display = ''

    @api.constrains('start_datetime', 'end_datetime')
    def _check_datetime_validity(self):
        for booking in self:
            if booking.start_datetime and booking.end_datetime:
                if booking.end_datetime <= booking.start_datetime:
                    raise ValidationError(_("End time must be after start time."))

                if booking.is_holiday_conflict:
                    raise ValidationError(_("Booking conflicts with company holidays."))

    @api.constrains('room_id', 'start_datetime', 'end_datetime')
    def _check_booking_conflicts(self):
        for booking in self:
            if not booking.room_id or not booking.start_datetime or not booking.end_datetime:
                continue
            domain = [
                ('room_id', '=', booking.room_id.id),
                ('state', 'in', ['pending', 'confirmed']),
                ('id', '!=', booking.id),
                ('start_datetime', '<', booking.end_datetime),
                ('end_datetime', '>', booking.start_datetime),
            ]
            if self.search_count(domain):
                raise ValidationError(_("This room is already booked for the selected time."))

    @api.constrains('booking_type', 'department_id')
    def _check_event_department(self):
        for booking in self:
            if booking.booking_type == 'event' and not booking.department_id:
                raise ValidationError(_("Department must be specified for Event bookings."))

    @api.constrains('is_recurring', 'recurrence_rule')
    def _check_recurrence_rule(self):
        for booking in self:
            if booking.is_recurring and booking.recurrence_rule:
                if not self._validate_recurrence_rule(booking.recurrence_rule):
                    raise ValidationError(
                        _("Invalid recurrence rule format. Please use iCal format (e.g., FREQ=WEEKLY;BYDAY=MO,WE,FR)."))

    def _validate_recurrence_rule(self, rule):
        if not rule:
            return False

        if 'FREQ=' not in rule.upper():
            return False

        valid_freq = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
        freq_match = re.search(r'FREQ=([A-Z]+)', rule.upper())
        if freq_match and freq_match.group(1) not in valid_freq:
            return False

        return True

    @api.constrains('contact_email')
    def _check_contact_email(self):
        for booking in self:
            if booking.contact_email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, booking.contact_email):
                    raise ValidationError(_("Please enter a valid email address."))

    @api.constrains('required_capacity', 'room_capacity')
    def _check_capacity(self):
        for booking in self:
            if booking.required_capacity and booking.room_capacity:
                if booking.required_capacity > booking.room_capacity:
                    raise ValidationError(_("Required capacity (%d) exceeds room capacity (%d).") % 
                                        (booking.required_capacity, booking.room_capacity))

    @api.constrains('required_equipment_ids')
    def _check_equipment_availability(self):
        for booking in self:
            if booking.required_equipment_ids and booking.start_datetime and booking.end_datetime:
                for equipment in booking.required_equipment_ids:
                    conflicting_bookings = self.search([
                        ('id', '!=', booking.id),
                        ('required_equipment_ids', 'in', equipment.id),
                        ('state', 'in', ['confirmed', 'in_progress']),
                        ('start_datetime', '<', booking.end_datetime),
                        ('end_datetime', '>', booking.start_datetime),
                    ])
                    
                    if conflicting_bookings:
                        raise ValidationError(_("Equipment '%s' is not available during the selected time.") % equipment.name)

    def create_room_manager_activity(self):
        for booking in self:  # Use 'self' as a recordset in case of multi-create
            manager_employee = booking.room_id.manager_id
            if booking.booking_type == 'event' and booking.state == 'pending' and manager_employee:
                manager_user = manager_employee.user_id
                if manager_user:  # Ensure the employee has a linked Odoo user
                    booking.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=manager_user.id,  # <--- CORRECTED: Use the res.users ID
                        summary='Event booking approval required',
                        note=f'Please review and approve booking {booking.name} for room {booking.room_id.name}.',
                    )
                else:
                    # Optional: Log a warning if manager has no user, or raise error if critical
                    self.env.cr.execute(
                        f"INSERT INTO ir_logging (create_date, create_uid, name, level, message, type, dbname, func, line) VALUES (NOW(), {self.env.uid}, 'facilities.space.booking', 'WARNING', 'Room manager {manager_employee.name} for room {booking.room_id.name} does not have an associated Odoo user. Cannot create approval activity.', 'server', '{self.env.cr.dbname}', 'create_room_manager_activity', '{__name__}.py:L{self._get_linenumber()}');")
                    _logger.warning(
                        "Room manager %s for room %s does not have an associated Odoo user. Cannot create approval activity.",
                        manager_employee.name, booking.room_id.name)

    def schedule_reminder_emails(self):
        for booking in self:
            if booking.state == 'confirmed' and booking.start_datetime:
                reminder_date = booking.start_datetime - timedelta(hours=24)
                if reminder_date > datetime.now():
                    booking.activity_schedule(
                        'mail.mail_activity_data_email',
                        date_deadline=reminder_date.date(),
                        user_id=booking.user_id.id,
                        summary='Booking Reminder',
                        note=f'Reminder: You have a booking tomorrow - {booking.name}',
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('facilities.space.booking') or _('New')

            if vals.get('booking_type') == 'event':
                vals['state'] = 'pending'
            else:
                vals['state'] = 'confirmed'

        records = super().create(vals_list)

        for rec in records:
            # Check if an hr_employee and linked res_users is available for activity creation
            manager_employee = rec.room_id.manager_id
            if rec.booking_type == 'event' and rec.state == 'pending' and manager_employee and manager_employee.user_id:
                rec.create_room_manager_activity()  # This method will now handle fetching user_id correctly

            if rec.state == 'confirmed':
                rec.schedule_reminder_emails()
                template = self.env.ref('facilities_management.mail_template_space_booking_confirmed',
                                        raise_if_not_found=False)
                if template:
                    template.send_mail(rec.id, force_send=True)

        return records

    def write(self, vals):
        old_state = {rec.id: rec.state for rec in self}
        result = super().write(vals)

        for rec in self:
            if vals.get('state') == 'confirmed' and old_state.get(rec.id) != 'confirmed':
                template = self.env.ref('facilities_management.mail_template_space_booking_confirmed',
                                        raise_if_not_found=False)
                if template:
                    template.send_mail(rec.id, force_send=True)
                rec.schedule_reminder_emails()

        return result

    def action_confirm(self):
        for booking in self:
            if booking.booking_type == 'event' and booking.state == 'pending':
                manager_employee = booking.room_id.manager_id

                if not manager_employee:
                    raise ValidationError(_("No room manager assigned to this room. Event booking cannot be approved."))

                manager_user = manager_employee.user_id

                if not manager_user:
                    raise ValidationError(_("The assigned room manager (%s) does not have an associated Odoo user.") % (
                        manager_employee.name))

                if self.env.user.id != manager_user.id:
                    raise ValidationError(_("Only the room manager (%s) can approve this event booking.") % (
                        manager_employee.name))

                # Mark activity as done for the correct user
                activities = self.env['mail.activity'].search([
                    ('res_model', '=', 'facilities.space.booking'),
                    ('res_id', '=', booking.id),
                    ('user_id', '=', manager_user.id),  # <--- CORRECTED: Use the res.users ID here
                    ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
                    ('summary', '=', 'Event booking approval required'),
                ])
                activities.action_feedback(feedback='Approved')
                booking.write({'state': 'confirmed'})
            elif booking.state == 'draft':
                booking.write({'state': 'confirmed'})
            elif booking.state == 'pending' and booking.booking_type != 'event':
                booking.write({'state': 'confirmed'})
            else:
                raise ValidationError(_("Booking cannot be confirmed from its current state."))

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_create_recurring_bookings(self):
        for booking in self:
            if not booking.is_recurring or not booking.recurrence_rule:
                continue

            if 'FREQ=WEEKLY' in booking.recurrence_rule.upper():
                current_date = booking.start_datetime
                duration = booking.end_datetime - booking.start_datetime

                for i in range(1, 11):
                    next_start = current_date + timedelta(weeks=i)
                    next_end = next_start + duration

                    existing = self.search([
                        ('room_id', '=', booking.room_id.id),
                        ('start_datetime', '=', next_start),
                        ('end_datetime', '=', next_end),
                    ])

                    if not existing:
                        new_booking_state = 'pending' if booking.booking_type == 'event' else 'confirmed'
                        self.create({
                            'room_id': booking.room_id.id,
                            'user_id': booking.user_id.id,
                            'start_datetime': next_start,
                            'end_datetime': next_end,
                            'purpose': booking.purpose,
                            'attendees': booking.attendees,
                            'notes': booking.notes,
                            'booking_type': booking.booking_type,
                            'contact_email': booking.contact_email,
                            'department_id': booking.department_id.id if booking.department_id else False,
                            'is_external_guest': booking.is_external_guest,
                            'external_guest_names': booking.external_guest_names,
                            'is_recurring': False,
                            'state': new_booking_state,
                        })

    def action_check_in(self):
        """Manual or automatic check-in"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("Only confirmed bookings can be checked in."))
        
        self.write({
            'check_in_time': fields.Datetime.now(),
            'state': 'in_progress'
        })
        
        self.message_post(body=_("Booking checked in at %s") % fields.Datetime.now())

    def action_check_out(self):
        """Manual or automatic check-out"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Only in-progress bookings can be checked out."))
        
        self.write({
            'check_out_time': fields.Datetime.now(),
            'state': 'completed'
        })
        
        self.message_post(body=_("Booking checked out at %s") % fields.Datetime.now())

    def action_approve(self):
        """Approve booking"""
        self.ensure_one()
        if not self.approval_required:
            raise UserError(_("This booking does not require approval."))
        
        self.write({
            'state': 'confirmed',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        self.message_post(body=_("Booking approved by %s") % self.env.user.name)

    def action_reject(self):
        """Reject booking with reason"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Booking',
            'res_model': 'facilities.booking.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_booking_id': self.id}
        }

    def action_create_template(self):
        """Create booking template from current booking"""
        self.ensure_one()
        if not self.template_name:
            raise UserError(_("Please provide a template name."))
        
        template_data = {
            'name': self.template_name,
            'booking_type': self.booking_type,
            'purpose': self.purpose,
            'attendees': self.attendees,
            'notes': self.notes,
            'department_id': self.department_id.id,
            'required_equipment_ids': [(6, 0, self.required_equipment_ids.ids)],
            'is_external_guest': self.is_external_guest,
            'priority': self.priority,
            'notification_settings': self.notification_settings,
        }
        
        template = self.env['facilities.booking.template'].create(template_data)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking Template',
            'res_model': 'facilities.booking.template',
            'res_id': template.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_reminder(self):
        """Send booking reminder"""
        self.ensure_one()
        template = self.env.ref('facilities_management.mail_template_space_booking_reminder', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.reminder_sent = True

    def action_view_rating(self):
        """View booking rating details"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking Rating',
            'res_model': 'facilities.space.booking',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'flags': {'mode': 'readonly'},
        }

    def action_view_portal(self):
        """Get portal view URL"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        portal_url = f"{base_url}/my/booking/{self.id}?access_token={self.portal_access_token}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': portal_url,
            'target': 'new',
        }

    @api.model
    def auto_check_in_out(self):
        """Cron job for automatic check-in/out"""
        now = fields.Datetime.now()
        
        # Auto check-in
        bookings_to_check_in = self.search([
            ('state', '=', 'confirmed'),
            ('auto_check_in', '=', True),
            ('start_datetime', '<=', now),
            ('check_in_time', '=', False),
        ])
        
        for booking in bookings_to_check_in:
            booking.action_check_in()
        
        # Auto check-out
        bookings_to_check_out = self.search([
            ('state', '=', 'in_progress'),
            ('auto_check_out', '=', True),
            ('end_datetime', '<=', now),
            ('check_out_time', '=', False),
        ])
        
        for booking in bookings_to_check_out:
            booking.action_check_out()

    @api.model
    def send_reminder_notifications(self):
        """Cron job to send reminder notifications"""
        reminder_time = fields.Datetime.now() + timedelta(hours=24)
        
        bookings = self.search([
            ('state', '=', 'confirmed'),
            ('start_datetime', '<=', reminder_time),
            ('start_datetime', '>', fields.Datetime.now()),
            ('reminder_sent', '=', False),
        ])
        
        for booking in bookings:
            booking.action_send_reminder()

    @api.model
    def send_overdue_notifications(self):
        """Send notifications for overdue bookings"""
        # Find overdue bookings and notify
        overdue_bookings = self.search([
            ('is_overdue', '=', True),
            ('state', 'in', ['confirmed', 'in_progress'])
        ])
        
        for booking in overdue_bookings:
            booking.message_post(
                body=f'Booking {booking.name} is overdue. Please check out or extend the booking.',
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

    def action_view_my_bookings(self):
        """View my bookings"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Bookings',
            'res_model': 'facilities.space.booking',
            'view_mode': 'kanban,tree,form,calendar',
            'domain': [('user_id', '=', self.env.user.id)],
            'context': {
                'search_default_my_bookings': 1,
                'default_user_id': self.env.user.id,
            },
            'target': 'current',
        }

    def action_view_today_bookings(self):
        """View today's bookings"""
        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)
        
        return {
            'type': 'ir.actions.act_window',
            'name': "Today's Bookings",
            'res_model': 'facilities.space.booking',
            'view_mode': 'kanban,tree,form,calendar',
            'domain': [
                ('start_datetime', '>=', today),
                ('start_datetime', '<', tomorrow)
            ],
            'context': {
                'search_default_today': 1,
                'default_start_datetime': fields.Datetime.now(),
            },
            'target': 'current',
        }

    def action_view_utilization_report(self):
        """View utilization report"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Utilization Report',
            'res_model': 'facilities.space.booking',
            'view_mode': 'pivot,graph',
            'domain': [('state', 'in', ['confirmed', 'completed'])],
            'context': {
                'group_by': ['room_id'],
                'search_default_confirmed': 1,
            },
            'target': 'current',
        }

    def action_view_cost_analysis(self):
        """View cost analysis"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cost Analysis',
            'res_model': 'facilities.space.booking',
            'view_mode': 'pivot,graph',
            'domain': [('state', 'in', ['confirmed', 'completed']), ('total_cost', '>', 0)],
            'context': {
                'group_by': ['department_id'],
                'search_default_confirmed': 1,
            },
            'target': 'current',
        }

    def action_view_trends(self):
        """View booking trends"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking Trends',
            'res_model': 'facilities.space.booking',
            'view_mode': 'graph,pivot',
            'domain': [('state', 'in', ['confirmed', 'completed'])],
            'context': {
                'group_by': ['start_datetime:month'],
                'search_default_confirmed': 1,
            },
            'target': 'current',
        }

    def action_view_department_analysis(self):
        """View department analysis"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Department Analysis',
            'res_model': 'facilities.space.booking',
            'view_mode': 'graph,pivot',
            'domain': [('state', 'in', ['confirmed', 'completed']), ('department_id', '!=', False)],
            'context': {
                'group_by': ['department_id'],
                'search_default_confirmed': 1,
            },
            'target': 'current',
        }

    def action_view_booking_patterns(self):
        """View booking patterns"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking Patterns',
            'res_model': 'facilities.space.booking',
            'view_mode': 'graph,pivot',
            'domain': [('state', 'in', ['confirmed', 'completed'])],
            'context': {
                'group_by': ['booking_type', 'start_datetime:week'],
                'search_default_confirmed': 1,
            },
            'target': 'current',
        }

    @api.model
    def get_dashboard_data(self):
        """Get dashboard data for the facilities management dashboard"""
        try:
            # Get current date and time
            now = fields.Datetime.now()
            today = fields.Date.today()
            
            # Calculate date ranges
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Get booking statistics
            total_bookings = self.search_count([])
            today_bookings = self.search_count([
                ('start_datetime', '>=', today),
                ('start_datetime', '<', today + timedelta(days=1))
            ])
            week_bookings = self.search_count([
                ('start_datetime', '>=', week_ago)
            ])
            month_bookings = self.search_count([
                ('start_datetime', '>=', month_ago)
            ])
            
            # Get status breakdown
            confirmed_bookings = self.search_count([('state', '=', 'confirmed')])
            pending_bookings = self.search_count([('state', '=', 'pending')])
            completed_bookings = self.search_count([('state', '=', 'completed')])
            cancelled_bookings = self.search_count([('state', '=', 'cancelled')])
            
            # Get booking type breakdown
            booking_types = self.read_group(
                [('state', 'in', ['confirmed', 'completed'])],
                ['booking_type'],
                ['booking_type']
            )
            
            # Get room utilization
            rooms = self.env['facilities.room'].search([])
            room_utilization = []
            for room in rooms:
                room_bookings = self.search_count([
                    ('room_id', '=', room.id),
                    ('state', 'in', ['confirmed', 'completed']),
                    ('start_datetime', '>=', week_ago)
                ])
                room_utilization.append({
                    'room_name': room.name,
                    'bookings_count': room_bookings,
                    'capacity': room.capacity or 0
                })
            
            # Get recent bookings
            recent_bookings = self.search([
                ('start_datetime', '>=', today)
            ], limit=5, order='start_datetime asc')
            
            recent_bookings_data = []
            for booking in recent_bookings:
                recent_bookings_data.append({
                    'id': booking.id,
                    'name': booking.name,
                    'room_name': booking.room_id.name,
                    'start_datetime': booking.start_datetime.strftime('%Y-%m-%d %H:%M'),
                    'end_datetime': booking.end_datetime.strftime('%Y-%m-%d %H:%M'),
                    'state': booking.state,
                    'booking_type': booking.booking_type,
                    'user_name': booking.user_id.name
                })
            
            return {
                'total_bookings': total_bookings,
                'today_bookings': today_bookings,
                'week_bookings': week_bookings,
                'month_bookings': month_bookings,
                'status_breakdown': {
                    'confirmed': confirmed_bookings,
                    'pending': pending_bookings,
                    'completed': completed_bookings,
                    'cancelled': cancelled_bookings
                },
                'booking_types': booking_types,
                'room_utilization': room_utilization,
                'recent_bookings': recent_bookings_data,
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_bookings': 0,
                'today_bookings': 0,
                'week_bookings': 0,
                'month_bookings': 0,
                'status_breakdown': {
                    'confirmed': 0,
                    'pending': 0,
                    'completed': 0,
                    'cancelled': 0
                },
                'booking_types': [],
                'room_utilization': [],
                'recent_bookings': [],
                'current_time': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }