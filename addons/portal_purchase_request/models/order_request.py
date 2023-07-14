# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OrderRequest(models.Model):
    _name = 'order.request'
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string='User')
    vendor_id = fields.Many2one('res.partner', string='Supplier')
    attachment_ids = fields.Many2many('ir.attachment')
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('purchase_in_progress', 'Purchase in progress'),
         ('ready_pick_up', 'Ready to pick-up'), ('done', 'Done'), ('rejected', 'Rejected')], string='Status',
        default='draft')
    line_ids = fields.One2many('order.request.line', 'order_id', string='Order Line')

    def change_request_order_to_done(self):
        self.sudo().state = 'done'
        self.sudo().user_id.authorization_create = True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
            'request.order.counter')
        res = super(OrderRequest, self).create(vals)
        return res


class OrderRequestLine(models.Model):
    _name = 'order.request.line'

    order_id = fields.Many2one('order.request', string='Order')
    quantity = fields.Integer(string='Quantity')
    unit_price = fields.Float(string='Price')
    tax_ids = fields.Many2many('account.tax', string='Tax')
    product_id = fields.Many2one('product.product', string='Product')
