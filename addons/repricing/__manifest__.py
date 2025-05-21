# -*- coding: utf-8 -*-
{
    "name": "Repricing",
    "version": "16.0.0.0",
    "category": "sale",
    "description": """Repricing:  
     """,
    "summary": " ",
    "author": "Maki Turki",
    "license": "AGPL-3",
    "depends": ["base", "sale", "product", "stock", "outillage_dev"],
    "data": [
        "security/ir.model.access.csv",
        # Views
        "views/product.xml",
        "views/bright_data_collector.xml",
        "views/product_ceiling_price.xml",
        "views/ir_cron.xml",
        # Crons
        "data/repricing_cron.xml",
        "data/bright_data_cron.xml",
        # Mail
        "data/repricing_mail.xml",
    ],
}
