# -*- coding: utf-8 -*-
# pylint: disable=pointless-statement


{
    "name": "Mano Connexion",
    "version": "16.0.0.0",
    "summary": "",
    "author": "Maki Turki",
    "description": "Module make connexion with platform ManoMano",
    "depends": ["base", "sale", "delivery", "stock", "repricing"],
    "sequence": 1,
    "data": [
        "views/mano_view.xml",
        "data/mano_connexion.xml",
        "data/mano_cron.xml",
        "data/create_shipping_cron.xml",
        "data/mano_email.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
        "views/delivery_carrier_view.xml",
        "views/stock_picking_view.xml",
        "views/product_form.xml",
        "views/mano_setting_view.xml",
        "views/res_config_view.xml",
    ],
    "license": "LGPL-3",
}
