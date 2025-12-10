import logging
from datetime import datetime

import pytz
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'
    _order = 'date desc, start_time asc'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        ondelete='cascade'
    )
    weekday = fields.Selection(selection=[
        ('0', 'Mon'),
        ('1', 'Tue'),
        ('2', 'Wed'),
        ('3', 'Thu'),
        ('4', 'Fri'),
        ('5', 'Sat'),
        ('6', 'Sun'),
    ],
        string='Day of Week',
        compute='_compute_weekday'
    )

    date = fields.Date(
        compute='_compute_time_parts',
        store=True,
        compute_sudo=False,
        readonly=True
    )
    start_time = fields.Float(
        compute='_compute_time_parts',
        store=True,
        compute_sudo=False,
        readonly=True
    )
    end_time = fields.Float(
        compute='_compute_time_parts',
        store=True,
        compute_sudo=False,
        readonly=True
    )

    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)

    schedule_type = fields.Selection(selection=[
        ('working', 'Working day'),
        ('vacation', 'Vacation'),
        ('sick_day', 'Sick day'),
        ('conference', 'Conference'),
    ], default='working')
    notes = fields.Char()

    _sql_constraints = [
        ('check_time_range',
         'CHECK (end_datetime > start_datetime)',
         'The end time must be later than the start time in the schedule.'),
    ]

    def _combine_datetime_parts(self, source_dt, target_dt):
        """Combines the DATE from source_dt and the TIME from target_dt
        to create a new datetime object or False if data is missing."""
        if source_dt and target_dt:
            return datetime.combine(source_dt.date(), target_dt.time())
        return False

    @api.onchange('start_datetime')
    def _onchange_start_datetime_copy_date(self):
        """When Start Time is changed: copies the DATE part to End Time,
        preserving the existing TIME part of End Time."""
        _logger.warning(f"*** {self.start_datetime}  *** {self.end_datetime}")

        if not self.start_datetime:
            return

        if self.end_datetime:
            self.end_datetime = self._combine_datetime_parts(
                self.start_datetime, self.end_datetime
            )
        else:
            self.end_datetime = self.start_datetime

    @api.onchange('end_datetime')
    def _onchange_end_datetime_copy_date(self):
        """When End Time is changed: copies the DATE part to Start Time,
        preserving the existing TIME part of Start Time."""
        _logger.warning(f"*** {self.start_datetime}  *** {self.end_datetime}")

        if not self.end_datetime:
            return
        if self.start_datetime:
            self.start_datetime = self._combine_datetime_parts(
                self.end_datetime, self.start_datetime
            )
        else:
            self.start_datetime = self.end_datetime

    @api.depends('date')
    def _compute_weekday(self):
        """Calculates the weekday (0 to 6) based on the 'date' field."""
        for rec in self:
            if rec.date:
                rec.weekday = str(rec.date.weekday())
            else:
                rec.weekday = False

    @api.depends('start_datetime', 'end_datetime')
    def _compute_time_parts(self):
        """Converts UTC values of start_datetime and end_datetime into local
           date, start_time (float), end_time (float) on the user's TZ."""
        tz_name = self.env.context.get('tz') or 'UTC'
        local_tz = pytz.timezone(tz_name)

        for rec in self:
            if rec.start_datetime:
                local_dt_start = pytz.utc.localize(
                    rec.start_datetime
                ).astimezone(local_tz)
                rec.date = local_dt_start.date()
                rec.start_time = (
                    local_dt_start.hour + local_dt_start.minute / 60.0
                )
            else:
                rec.date = False
                rec.start_time = 0.0

            if rec.end_datetime:
                local_dt_end = pytz.utc.localize(
                    rec.end_datetime
                ).astimezone(local_tz)
                rec.end_time = local_dt_end.hour + local_dt_end.minute / 60.0
            else:
                rec.end_time = 0.0
