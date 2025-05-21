# Copyright 2022 Maki Turki
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProductPriceRouteDelivery(models.Model):
    _name = "product.price.route.delivery"
    _description = "Product Price Route Delivery"

    sales = fields.Integer(string="Ventes")

    create_date_from = fields.Integer(string="Create Date")

    create_date_to = fields.Integer(string="Create Date")

    multiplier = fields.Char(string="Multiplicateur")

    ceiling_id = fields.Many2one(string="Product", comodel_name="product.ceiling.price")
