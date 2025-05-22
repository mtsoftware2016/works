# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    virtual_available_without_incoming_qty_v1 = fields.Float(
        string="Stock disponible Outillage Online",
        compute="get_virtual_available_without_incoming_qty_v1",
    )

    @api.depends("stock_quantity_by_location_ids")
    def get_virtual_available_without_incoming_qty_v1(self):
        for rec in self:
            qty = 0
            for item in rec.stock_quantity_by_location_ids:
                if item.location_id.id != 19:
                    qty += item.virtual_available_without_incoming_qty
            rec.virtual_available_without_incoming_qty_v1 = qty
