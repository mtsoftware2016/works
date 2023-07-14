# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    tracking_url = fields.Text(
        string='Tracking Url'
    )
