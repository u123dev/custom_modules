from odoo import models, fields


class DoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'
    _order = 'date desc, start_time asc'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        ondelete='cascade'
    )
    weekday = fields.Selection([
        ('0', 'Mon'),
        ('1', 'Tue'),
        ('2', 'Wed'),
        ('3', 'Thu'),
        ('4', 'Fri'),
        ('5', 'Sat'),
        ('6', 'Sun'),
    ], string='Day of Week')
    date = fields.Date()
    start_time = fields.Float()
    end_time = fields.Float()
    schedule_type = fields.Selection([
        ('working', 'Working day'),
        ('vacation', 'Vacation'),
        ('sick_day', 'Sick day'),
        ('conference', 'Conference'),
    ], default='working')
    notes = fields.Char()

    _sql_constraints = [
        ('check_time_range',
         'CHECK (end_time > start_time)',
         'The end time must be later than the start time in the schedule.'),
    ]
