from odoo import models, fields


class DateMixin(models.AbstractModel):
    _name = 'hr.hospital.date.mixin'
    _description = 'Date utility mixin'

    def _calculate_years(self, date_field):
        """Compute full years difference between given date and today."""
        if not date_field:
            return 0
        today = fields.Date.today()
        years = today.year - date_field.year - (
            (today.month, today.day) < (date_field.month, date_field.day)
        )
        return max(years, 0)
