# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_request = fields.Many2one("order.request", string="Request")

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if self.sudo().order_request.user_id.is_user:
            template_id = self.env.ref(
                "portal_purchase_request.employee_notifcation_delivery_mail"
            )
            template_id.sudo().send_mail(self.id, force_send=True, raise_exception=True)
        return res
