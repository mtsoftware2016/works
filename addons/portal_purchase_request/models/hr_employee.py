# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    tax_id = fields.Many2one(
        'account.tax',
        string="Tax"
    )
