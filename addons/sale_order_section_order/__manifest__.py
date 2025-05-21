# -*- coding: utf-8 -*-
# pylint: disable=pointless-statement

{
    "name": "Sale Order Section order",
    "version": "15.0.1.0.0",
    "description": """
        Sale Order Section order
    """,
    "author": "Maki Turki",
    "category": "Sales",
    # any module necessary for this one to work correctly
    "depends": [
        "sale_management",
    ],
    # always loaded
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/sale_order.xml",
        "wizard/sale_order_section_wizard.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "images": [],
    "license": "OPL-1",
    "live_test_url": "",
    "installable": True,
}
