# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    is_professional = fields.Char(string="Is Professional")
    company_mano = fields.Char(string="Company Mano")
