import logging
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pytz


_logger = logging.getLogger(__name__)


class HrHospitalDoctorScheduleWizard(models.TransientModel):
    _name = 'hr.hospital.doctor.schedule.wizard'
    _description = 'Doctor Schedule Generation Wizard'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
    )
    start_week_date = fields.Date(
        required=True,
        default=fields.Date.today,
        help='The first day of the week (Monday) from which scheduling begins.'
    )
    num_weeks = fields.Integer(
        string='Number of Weeks',
        required=True,
        default=1,
    )
    schedule_type = fields.Selection(selection=[
        ('standard', 'Standard (Every Week)'),
        ('even', 'Even Week Only'),
        ('odd', 'Odd Week Only'),
    ], default='standard', required=True)

    mon = fields.Boolean(string='Monday')
    tue = fields.Boolean(string='Tuesday')
    wed = fields.Boolean(string='Wednesday')
    thu = fields.Boolean(string='Thursday')
    fri = fields.Boolean(string='Friday')
    sat = fields.Boolean(string='Saturday')
    sun = fields.Boolean(string='Sunday')

    time_start = fields.Float(required=True)
    time_end = fields.Float(required=True)
    break_from = fields.Float()
    break_to = fields.Float()

    @api.model
    def default_get(self, fields_list):
        """Pre-fill doctor_id if opened from a doctor's record."""
        res = super(HrHospitalDoctorScheduleWizard, self).default_get(
            fields_list)
        active_id = self._context.get('active_id')
        if self._context.get(
                'active_model') == 'hr.hospital.doctor' and active_id:
            res['doctor_id'] = active_id
        return res

    @api.constrains('time_start', 'time_end', 'break_from', 'break_to')
    def _check_time_constraints(self):
        """Validate time logic:
        Start < End, Break From < Break To, Break Time is within Work Time."""
        for rec in self:
            if rec.time_start >= rec.time_end:
                raise ValidationError(
                    _("Start Time must be strictly earlier than End Time."))

            if rec.break_from or rec.break_to:
                if rec.break_from >= rec.break_to:
                    raise ValidationError(
                        _("Break From must be earlier than Break To."))
                if (rec.break_from < rec.time_start or
                        rec.break_to > rec.time_end):
                    raise ValidationError(
                        _("Break Time must during working hours."))

    @api.constrains('num_weeks')
    def _check_num_weeks(self):
        """Ensure number of weeks is positive."""
        for rec in self:
            if rec.num_weeks <= 0:
                raise ValidationError(
                    _("Number of Weeks must be greater than zero."))

    @api.onchange('start_week_date')
    def _onchange_start_week_date(self):
        """Change the date to the beginning of the week (Monday)."""
        if self.start_week_date:
            date = self.start_week_date
            day_of_week = date.weekday()
            self.start_week_date = date - timedelta(days=day_of_week)

    def _float_to_utc_datetime(self, target_date, float_time):
        """
        Converts a Date object and a float time (hours)
        based on the user's timezone.
        """
        tz_name = self.env.context.get('tz') or 'UTC'
        local_tz = pytz.timezone(tz_name)

        hours = int(float_time)
        minutes = int(round((float_time - hours) * 60))

        # Combine date and time into a naive local datetime object
        local_dt = datetime.combine(target_date, datetime.min.time())
        local_dt += timedelta(hours=hours, minutes=minutes)
        # Localize (make it timezone-aware)
        local_dt_aware = local_tz.localize(local_dt)

        # Convert to UTC and return as datetime
        return local_dt_aware.astimezone(pytz.utc).replace(tzinfo=None)

    def action_generate_schedule(self):
        """Generates schedule entries for the selected days and weeks."""
        self.ensure_one()

        # Determine which days are selected
        days_to_schedule = {
            0: self.mon, 1: self.tue, 2: self.wed, 3: self.thu,
            4: self.fri, 5: self.sat, 6: self.sun
        }

        # Check if any day is selected
        if not any(days_to_schedule.values()):
            raise UserError(_("Please select at least one day to schedule."))

        Schedule = self.env['hr.hospital.doctor.schedule']
        schedule_records = []
        current_date = self.start_week_date

        # pylint: disable=unused-variable
        for week_index in range(self.num_weeks):
            # Calculate ISO week number (used for even/odd checking)
            iso_week_num = current_date.isocalendar()[1]
            is_even_week = (iso_week_num % 2 == 0)

            # Check schedule type validity for the current week
            if (self.schedule_type == 'even' and not is_even_week) or \
                    (self.schedule_type == 'odd' and is_even_week):
                # Skip this week if it doesn't match the even/odd filter
                current_date += timedelta(weeks=1)
                continue

            for day_index, is_selected in days_to_schedule.items():
                if not is_selected:
                    continue

                # Calculate the specific date for this day
                day_date = current_date + timedelta(days=day_index)

                start_dt_utc = self._float_to_utc_datetime(
                    day_date, self.time_start)
                end_dt_utc = self._float_to_utc_datetime(
                    day_date, self.time_end)

                # Prepare data for the new schedule record
                schedule_data = {
                    'doctor_id': self.doctor_id.id,
                    'start_datetime': start_dt_utc,
                    'end_datetime': end_dt_utc,
                    'schedule_type': 'working',  # Default schedule type
                }

                # TO DO:    Add break times if provided
                #   !!! But now there are no fields 'break_from' & 'break_to'
                #       in schedule model !!!
                # if self.break_from and self.break_to:
                #     schedule_data.update({
                #         'break_from': self.break_from,
                #         'break_to': self.break_to,
                #     })

                schedule_records.append(schedule_data)
                logging.warning("******* ", )
                logging.warning(schedule_data)

            # Move to the next week's starting date
            current_date += timedelta(weeks=1)

        if not schedule_records:
            raise UserError(
                _("No schedule entries generated. "
                  "Check if the dates conflict with the Even/Odd Week Type."))

        # Create all records in batch
        Schedule.create(schedule_records)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Schedule'),
            'res_model': 'hr.hospital.doctor.schedule',
            'view_mode': 'tree,form',
            'domain': [('doctor_id', '=', self.doctor_id.id)],
            'target': 'current',
        }
