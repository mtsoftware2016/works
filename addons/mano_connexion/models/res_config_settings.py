# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    api_key_mano = fields.Char(string="API KEY")

    seller_contract_id = fields.Char(string="Seller Contract ID Espagne")

    contract_id_fr = fields.Char(string="Seller Contract ID France")

    def set_values(self):
        IR_CONFIG_PARAMETER = self.env["ir.config_parameter"]
        super(ResConfigSettings, self).set_values()

        IR_CONFIG_PARAMETER.sudo().set_param("api_key_mano", self.api_key_mano)

        IR_CONFIG_PARAMETER.sudo().set_param(
            "seller_contract_id", self.seller_contract_id
        )

        IR_CONFIG_PARAMETER.sudo().set_param("contract_id_fr", self.contract_id_fr)

    @api.model
    def get_values(self):
        IR_CONFIG_PARAMETER = self.env["ir.config_parameter"]

        res = super(ResConfigSettings, self).get_values()

        api_key_mano = IR_CONFIG_PARAMETER.sudo().get_param("api_key_mano")
        seller_contract_id = IR_CONFIG_PARAMETER.sudo().get_param("seller_contract_id")
        contract_id_fr = IR_CONFIG_PARAMETER.sudo().get_param("contract_id_fr")
        res.update(
            {
                "api_key_mano": api_key_mano,
                "seller_contract_id": seller_contract_id,
                "contract_id_fr": contract_id_fr,
            }
        )
        return res
