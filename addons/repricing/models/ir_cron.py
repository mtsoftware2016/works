# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = 'ir.cron'

    product_domain = fields.Char(
        string='Domain',
        help='Alternative to a list of products'
    )
