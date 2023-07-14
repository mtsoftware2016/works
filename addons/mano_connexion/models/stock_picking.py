# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shiping_mano_active = fields.Boolean(
        string='Shiping Active '
    )
