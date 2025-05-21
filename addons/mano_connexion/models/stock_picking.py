# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    shiping_mano_active = fields.Boolean(string="Shiping Active ")
