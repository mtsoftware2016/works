# -*- coding: utf-8 -*-
from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_url = fields.Text(string="Tracking Url")
