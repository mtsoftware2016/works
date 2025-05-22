# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_studio_rfrence_marketplace = fields.Char(string="Reference Mano")

    date_order_mano = fields.Datetime(string="Date Order Mano")

    update_order_mano = fields.Datetime(string="Update Order Mano")

    mano_mf = fields.Integer(string="Mano MF")

    is_mmf = fields.Char(string="Is MF")

    status_mano = fields.Selection(
        [
            ("1", "Pending"),
            ("2", "Order Rejected"),
            ("3", "Order in preparation"),
            ("4", "Order shipped"),
            ("5", "Order refunded"),
            ("6", "Order refund in progress"),
        ],
        string="Status Mano",
    )
    is_mano = fields.Boolean(string="IS Mano")

    relay_id = fields.Char(string="Relay ID")
    relay_name = fields.Char(string="Relay Name")

    relay_address = fields.Char(string="Relay Address")

    relay_zipcode = fields.Char(string="Relay zipcode")

    relay_city = fields.Char(string="Relay City")

    relay_country = fields.Char(string="Relay Country")

    is_french = fields.Boolean(string="France")

    is_germany = fields.Boolean(string="Germany")

    is_spain = fields.Boolean(string="Spain")
    is_italy = fields.Boolean(string="Italie")

    is_french_pro = fields.Boolean(string="France Pro")
