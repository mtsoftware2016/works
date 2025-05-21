# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    product_domain = fields.Char(
        string="Domain", help="Alternative to a list of products"
    )
