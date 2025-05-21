# -*- coding: utf-8 -*-

from datetime import date, timedelta

from odoo import _, api, fields, models


class ManoSetting(models.Model):
    _name = "mano.setting"

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    mano_connexion = fields.Many2one("mano.mano", string="Connexion")
    ref_ids = fields.Many2many("mano.order.reference", string="Références")

    def sale_order_resolver(self):
        EndDate = self.date + timedelta(days=15)
        mano_object = self.env["mano.mano"]
        orders = mano_object.get_last_orders(
            self.mano_connexion, EndDate.strftime("%y-%m-%d")
        )
        refs = []
        for ref in self.ref_ids:
            refs.append(ref.name)
        for order in orders:
            if order.find("order_ref").text in refs:
                if not self.env["sale.order"].search(
                    [
                        (
                            "x_studio_rfrence_marketplace",
                            "=",
                            order.find("order_ref").text,
                        )
                    ]
                ):
                    sale_order = mano_object.create_sale_order(order, "France")
                    if sale_order:
                        mano_object.accept_order(
                            order.find("order_ref").text, self.mano_connexion
                        )
                    else:
                        mano_object.refuse_order(
                            order.find("order_ref").text, self.mano_connexion
                        )


class OrderReference(models.Model):
    _name = "mano.order.reference"
    name = fields.Char(string="Name")
