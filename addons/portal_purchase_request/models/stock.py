# -*- coding: utf-8 -*-
from odoo import fields, models


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    pick_to_backorder_ids = fields.Many2many(
        "stock.picking", help="Picking to backorder"
    )

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        purchase = self.env["purchase.order"].search(
            [("name", "=", self.env.context.get("default_origin"))]
        )
        if purchase.picking_ids.state == "done":
            template_id = self.env.ref(
                "portal_purchase_request.employee_notifcation_picking_mail"
            )
            template_id.sudo().send_mail(
                purchase.id, force_send=True, raise_exception=True
            )
            purchase.sudo().order_request.state = "ready_pick_up"
        return res
