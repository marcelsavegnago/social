# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    state = fields.Selection(selection_add=[('read', 'Lido')])

    message_id = fields.Char(
        string="SMS ID",
    )
