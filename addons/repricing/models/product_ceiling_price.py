# Copyright 2022 Maki Turki
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProductCeilingPrice(models.Model):
    _name = "product.ceiling.price"
    _description = "Product Ceiling Price"

    name = fields.Char(string="Name")

    price_list_route_buy = fields.One2many(
        string="Route Acheter",
        comodel_name="product.price.route",
        inverse_name="ceiling_id",
    )

    price_list_route_direct_delivery = fields.One2many(
        string="Route Livraison Directe",
        comodel_name="product.price.route.delivery",
        inverse_name="ceiling_id",
    )
