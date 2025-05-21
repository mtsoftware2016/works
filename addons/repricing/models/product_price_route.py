# Copyright 2022 Maki Turki
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProductPriceRoute(models.Model):
    _name = "product.price.route"
    _description = "Product Price Route"

    ceiling_id = fields.Many2one(string="Product", comodel_name="product.ceiling.price")

    order_number = fields.Integer(string="Nombre de commandes OO+MF ")
    number_of_availability_days = fields.Integer(
        string="Nombre de jours de disponibilité"
    )

    number_of_availability_days_2 = fields.Integer(
        string="Nombre de jours de disponibilité"
    )

    multiplier = fields.Char(string="Multiplicateur")
