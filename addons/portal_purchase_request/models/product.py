# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_employee_autorised = fields.Boolean(string='Autorized for Employee')


class ProductProduct(models.Model):
    _inherit = 'product.product'
    user_ids = fields.Many2many('res.users', string='Employees')

    def autorize_all_employee(self):
        ids = self.env['res.users'].search([('employee_id', '!=', False)]).ids
        self.user_ids = [(6, 0, ids)]
