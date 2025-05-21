# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

OUTILLAGE_ONLINE = [
    "Outillage Online",
    "Outillage online",
    "Outillage Online MF",
    "Outillage online MF",
]


class Product(models.Model):
    _inherit = "product.product"

    buybox_seller_name = fields.Char(string="Buybox seller name")

    buybox_seller_price = fields.Monetary(string="Buybox seller price")

    first_seller_name = fields.Text(string="First seller name")
    first_seller_price = fields.Monetary(string="First seller price")

    preconisation_odoo = fields.Monetary(string="Préconisation Odoo")

    price_plafond = fields.Monetary(string="Prix plafond")

    price_plancher = fields.Monetary(
        string="Prix plancher", compute="_compute_price_plancher"
    )

    scrapping_status = fields.Selection(
        [
            ("url", "URL introuvable"),
            ("price_mano_odoo", "Prix Mano et Prix Odoo différents"),
            ("no_marchand", "Aucun marchand"),
            ("all_conforme", "Tout est conforme"),
            ("seller_not_found", "Vendeur Outillage Online introuvable"),
        ],
        string="Statut Scrapping",
    )

    figer = fields.Boolean(string="Figer le repricing")

    restauring = fields.Boolean(string="Récupération Buybox")

    status_repricing = fields.Selection(
        [
            ("buybox_empty", "Buybox vide"),
            ("buybox_lost", "Buybox perdue"),
            ("buybox_recuperee", "Buybox récupérée"),
            ("buybox_consolide", "Buybox consolidée"),
            ("buybox_without_concurrent", "Buybox sans concurrent"),
            ("buybox_with_concurrent", "Buybox avec concurrent prix en monté"),
            (
                "buybox_with_concurrent_plafond",
                "Buybox avec concurrent prix en plafond",
            ),
            ("no_buybox_price_down", "Pas de Buybox prix en baisse"),
            ("no_buybox_price_plancher", "Pas de Buybox prix plancher"),
            ("error_scraping", "Erreur lors du scrapping"),
            ("no_buybox_mf", "Pas de Buybox MF prix en baisse"),
            ("no_buybox_mf_price_lost", "Pas de Buybox MF prix à perte"),
        ],
        string="Statut Repricing",
    )

    # OLD VALUES

    buybox_seller_name_old = fields.Char(string="Ancien Buybox seller name")

    buybox_seller_price_old = fields.Monetary(string="Ancien Buybox seller price")

    first_seller_name_old = fields.Text(string="Ancien First seller name")
    first_seller_price_old = fields.Monetary(string="Ancien First seller price")

    preconisation_odoo_old = fields.Monetary(string="Ancien Préconisation Odoo")

    scrapping_status_old = fields.Selection(
        [
            ("url", "URL introuvable "),
            ("price_mano_odoo", "Prix Mano et Prix Odoo différents"),
            ("no_marchand", "Aucun marchand"),
            ("all_conforme", "Tout est conforme"),
            ("seller_not_found", "Vendeur Outillage Online introuvable"),
        ],
        string="Ancien Statut Scrapping",
    )

    figer_old = fields.Boolean(string="Ancien Figer le repricing")

    restauring_old = fields.Boolean(string="Ancien Récupération Buybox")

    status_repricing_old = fields.Selection(
        [
            ("buybox_empty", "Buybox vide"),
            ("buybox_lost", "Buybox perdue"),
            ("buybox_recuperee", "Buybox récupérée"),
            ("buybox_consolide", "Buybox consolidée"),
            ("buybox_without_concurrent", "Buybox sans concurrent"),
            ("buybox_with_concurrent", "Buybox avec concurrent prix en monté"),
            (
                "buybox_with_concurrent_plafond",
                "Buybox avec concurrent prix en plafond",
            ),
            ("no_buybox_price_down", "Pas de Buybox prix en baisse"),
            ("no_buybox_price_plancher", "Pas de Buybox prix plancher"),
            ("error_scraping", "Erreur lors du scrapping"),
            ("no_buybox_mf", "Pas de Buybox MF prix en baisse"),
            ("no_buybox_mf_price_lost", "Pas de Buybox MF prix à perte"),
        ],
        string="Ancien Statut Repricing",
    )

    product_not_found = fields.Char(string="Input")

    seller_outtilage_online = fields.Float(string="Seller Outillage Online")

    buybox_shipping = fields.Monetary(string="Buybox Shipping")
    buybox_stock = fields.Integer(string="Buybox stock")

    buybox_mf = fields.Text(string="Buybox MF")

    order_number_oo_mf = fields.Integer(
        string="Nombre de commandes OO+MF", compute="_compute_order_number_oo_mf"
    )
    is_price_plafond_off = fields.Boolean(string="Désactiver prix plafond")

    is_synchronized = fields.Boolean(string="Is Synchronized", default=False)

    is_cron_price_plancher_synchronized = fields.Boolean(
        string="Is Cron Synchronized", default=False
    )

    is_batch_1 = fields.Boolean(string="Batch 1", default=False)

    is_batch_2 = fields.Boolean(string="Batch 2", default=False)

    is_batch_3 = fields.Boolean(string="Batch 3", default=False)

    date_scrapping = fields.Date(string="Date Scrapping")

    # ----------------------------------------------------------------------------------------------------
    # 1- ORM Methods (create, write, unlink)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 2- Constraints methods (_check_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 3- Compute methods (namely _compute_***)
    # ----------------------------------------------------------------------------------------------------

    @api.depends("order_count", "order_count_second")
    def _compute_order_number_oo_mf(self):
        for record in self:
            record.order_number_oo_mf = record.order_count + record.order_count_second

    def _compute_price_plancher(self):
        for rec in self:
            part_1 = (
                rec.x_studio_prix_dachat
                + rec.price_logistique
                + rec.price_transport
                + rec.fee_approche
            )
            part_2 = part_1 - (rec.x_studio_prix_dachat * rec.bfa_incon)
            part_3 = part_2 * 1.177
            part_4 = part_3 * 1.2
            part_5 = part_4 - rec.port_client
            rec.price_plancher = part_5

    # ----------------------------------------------------------------------------------------------------
    # 4- Onchange methods (namely onchange_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 5- Actions methods (namely action_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 6- CRONs methods
    # ----------------------------------------------------------------------------------------------------

    @api.model
    def _reset_pricing_for_products(self):
        products = self.env["product.product"].search(
            [("product_not_found", "!=", False)]
        )
        for product in products:
            product.buybox_seller_name_old = product.buybox_seller_name
            product.buybox_seller_name = ""
            product.buybox_seller_price_old = product.buybox_seller_price
            product.buybox_seller_price = 0
            product.first_seller_name_old = product.first_seller_name
            product.first_seller_name = ""
            product.first_seller_price_old = product.first_seller_price
            product.first_seller_price = 0
            product.preconisation_odoo_old = product.preconisation_odoo
            product.preconisation_odoo = 0
            product.scrapping_status_old = product.scrapping_status
            product.scrapping_status = False
            product.status_repricing_old = product.status_repricing
            product.status_repricing = False
            product.figer_old = product.figer
            product.figer = False
            product.restauring_old = product.restauring
            product.restauring = False
            product.product_not_found = False

    @api.model
    def _update_products_price_plafond(self):
        products = self.env["product.product"].search(
            [("type", "=", "product"), ("active", "=", True)]
        )
        for product in products:
            product._calculate_price_plafond()

    @api.model
    def _update_pricing_products(self):
        PRODUCT = self.env["product.product"]
        domain = [
            ("product_not_found", "!=", False),
            ("is_synchronized", "=", False),
        ]
        products = PRODUCT.search(domain, limit=2000)
        all_products = PRODUCT.search([("product_not_found", "!=", False)])
        products_synchronized = PRODUCT.search_count(
            [("product_not_found", "!=", False), ("is_synchronized", "=", True)]
        )
        # RESET Synchronization Products
        if len(all_products) == products_synchronized:
            all_products.write({"is_synchronized": False})
        for product in products:
            price_diff = round(product.seller_outtilage_online - product.lst_price, 2)

            if price_diff != 0 and product.lst_price >= 40:
                product.status_repricing = "error_scraping"
                product.scrapping_status = "price_mano_odoo"
                product.preconisation_odoo = 0

            if price_diff != 0 and price_diff != 3.99 and product.lst_price <= 39.99:
                product.status_repricing = "error_scraping"
                product.scrapping_status = "price_mano_odoo"
                product.preconisation_odoo = 0

            if product.seller_outtilage_online == 0:
                product.status_repricing = "error_scraping"
                product.scrapping_status = "seller_not_found"
                product.preconisation_odoo = 0
            # Vers le prix parfait 1/3, buybox perdue
            if (
                not product.status_repricing
                and product.buybox_seller_name_old in OUTILLAGE_ONLINE
                and product.buybox_seller_name not in OUTILLAGE_ONLINE
                and product.first_seller_name_old == product.buybox_seller_name
                and product.first_seller_price_old == product.buybox_seller_price
            ):
                product.status_repricing = "buybox_lost"
                product.scrapping_status = "all_conforme"
                product.preconisation_odoo = product.buybox_seller_price_old
                product.restauring = True
                product.product_tmpl_id.lst_price = (
                    product.preconisation_odoo
                    if product.preconisation_odoo > 0
                    else product.lst_price
                )

            # prix parfait 2/3, buybox récupérée
            if (
                not product.status_repricing
                and product.restauring_old
                and product.buybox_seller_name in OUTILLAGE_ONLINE
                and product.buybox_seller_name_old == product.first_seller_name
                and product.buybox_seller_price_old == product.first_seller_price
            ):
                product.status_repricing = "buybox_recuperee"
                product.scrapping_status = "all_conforme"
                product.preconisation_odoo = product.list_price
                product.figer = True
            # Vers le prix parfait 3/3, buybox consolidée
            if (
                not product.status_repricing
                and product.figer_old
                and product.buybox_seller_name == product.buybox_seller_name_old
                and product.buybox_seller_price_old == product.buybox_seller_price
                and product.first_seller_name_old == product.first_seller_name
                and product.first_seller_price_old == product.first_seller_price
            ):
                product.status_repricing = "buybox_consolide"
                product.scrapping_status = "all_conforme"
                product.preconisation_odoo = product.list_price
                product.figer = True
            # Buybox Outillage Online sans concurrent
            if (
                not product.status_repricing
                and product.buybox_seller_name in OUTILLAGE_ONLINE
                and not product.first_seller_name
            ):
                product.status_repricing = "buybox_without_concurrent"
                product.scrapping_status = "all_conforme"
                product.preconisation_odoo = product.price_plafond
                product.product_tmpl_id.lst_price = (
                    product.preconisation_odoo
                    if product.preconisation_odoo > 0
                    else product.lst_price
                )

            # Buybox Outillage Online avec concurrent
            if (
                not product.status_repricing
                and product.buybox_seller_name in OUTILLAGE_ONLINE
                and product.first_seller_name
            ):
                result_price = (
                    product.price_plafond
                    if product.lst_price * 1.005 >= product.price_plafond
                    else product.lst_price * 1.005
                )
                product.preconisation_odoo = result_price
                product.status_repricing = (
                    "buybox_with_concurrent"
                    if round(product.preconisation_odoo, 2)
                    < round(product.price_plafond, 2)
                    else "buybox_with_concurrent_plafond"
                )
                product.scrapping_status = "all_conforme"
                product.product_tmpl_id.lst_price = (
                    product.preconisation_odoo
                    if product.preconisation_odoo > 0
                    else product.lst_price
                )

            # Pas de Buybox
            if (
                not product.status_repricing
                and product.buybox_seller_name not in OUTILLAGE_ONLINE
                and product.virtual_available_without_incoming_qty_second <= 0
            ):
                result_price = (
                    product.price_plancher
                    if product.lst_price * 0.995 <= product.price_plancher
                    else product.lst_price * 0.995
                )
                product.preconisation_odoo = result_price
                product.status_repricing = (
                    "no_buybox_price_down"
                    if round(product.preconisation_odoo, 2)
                    > round(product.price_plancher, 2)
                    else "no_buybox_price_plancher"
                )
                product.scrapping_status = "all_conforme"
                product.product_tmpl_id.lst_price = (
                    product.preconisation_odoo
                    if product.preconisation_odoo > 0
                    else product.lst_price
                )

            # Pas de Buybox MF
            if (
                not product.status_repricing
                and product.buybox_seller_name not in OUTILLAGE_ONLINE
                and product.virtual_available_without_incoming_qty_second >= 1
            ):
                price_sale = product.lst_price * 0.995
                price_purchase = (product.purchase_price_seller * 0.9) * 1.2
                result_price = (
                    price_purchase if price_sale <= price_purchase else price_sale
                )

                if result_price <= product.price_plancher:
                    product.x_studio_fin_de_cycle_de_vie = True
                    # Archive Rules replenishment
                    for orderpoint in product.orderpoint_ids:
                        orderpoint.active = False

                result_price_preconisation = (
                    price_sale if price_sale >= price_purchase else price_purchase
                )
                product.preconisation_odoo = result_price_preconisation
                product.product_tmpl_id.lst_price = (
                    product.preconisation_odoo
                    if product.preconisation_odoo > 0
                    else product.lst_price
                )
                product.status_repricing = (
                    "no_buybox_mf_price_lost"
                    if round(product.preconisation_odoo, 2) <= round(price_purchase, 2)
                    else "no_buybox_mf"
                )

    @api.model
    def _update_products_price_plafond_plancher(self):
        CRON = self.env.ref("repricing.update_product_price_plafond_plancher")
        PRODUCT = self.env["product.product"]
        domain = [
            ("type", "=", "product"),
            ("active", "=", True),
            ("is_cron_price_plancher_synchronized", "=", False),
        ]
        products = PRODUCT.search(domain, limit=5000)
        all_products = PRODUCT.search([("type", "=", "product"), ("active", "=", True)])

        products_synchronized = PRODUCT.search_count(
            [
                ("type", "=", "product"),
                ("active", "=", True),
                ("is_cron_price_plancher_synchronized", "=", True),
            ]
        )

        next_call_date = (fields.Datetime.now() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d 00:00:00"
        )
        numbercall = 7
        # RESET Synchronization Products
        if len(all_products) == products_synchronized:
            _logger.info("condition checked ********** !!!!!!!!!!!!!!!!")
            all_products.write({"is_cron_price_plancher_synchronized": False})
            self._cr.execute(
                "UPDATE ir_cron SET nextcall=%s, numbercall=%s WHERE id=%s",
                (next_call_date, numbercall, CRON.id),
            )

        for product in products:
            product.is_cron_price_plancher_synchronized = True

            if product.status_repricing_old in [
                "no_buybox_mf",
                "no_buybox_mf_price_lost",
            ]:
                continue

            if product.lst_price < product.price_plancher:
                product.lst_price = product.price_plancher

            elif product.lst_price > product.price_plafond:
                product.lst_price = product.price_plafond

    # ----------------------------------------------------------------------------------------------------
    # 7- Technical methods (name must reflect the use)
    # ----------------------------------------------------------------------------------------------------

    def get_price_plafond(self, coeff):
        result = 0
        if coeff:
            price_1 = (
                self.x_studio_prix_dachat
                + self.price_logistique
                + self.price_transport
                + self.fee_approche
            ) - (self.x_studio_prix_dachat * self.bfa_incon)
            price_2 = (price_1 * float(coeff.replace(",", "."))) * 1.2
            result = price_2 - self.port_client
        return result

    def _calculate_price_plafond(self):
        PRODUCT_CEILING_PRICE = self.env["product.ceiling.price"]
        celing_price = PRODUCT_CEILING_PRICE.search([], limit=1)
        today = fields.Datetime.now()
        if not self.is_price_plafond_off:
            template_id = self.env.ref("repricing.repricing_error_email")
            price_plafond = 0
            create_date_start = (today.date() - self.create_date.date()).days
            for route in self.route_ids:
                # Route Acheter
                if route.name == "Acheter":
                    order_point = (
                        self.orderpoint_ids[0] if self.orderpoint_ids else False
                    )
                    available_days = 0
                    if order_point:
                        available_days = max(
                            order_point.number_of_availability_days,
                            order_point.number_of_availability_days_second,
                        )

                    coeff = celing_price.price_list_route_buy.filtered(
                        lambda c: c.order_number == self.order_number_oo_mf
                        and c.number_of_availability_days
                        <= available_days
                        <= c.number_of_availability_days_2
                    ).multiplier
                    price_plafond = self.get_price_plafond(coeff)
                    break

                # Route Livraison Directe
                elif route.name == "Livraison directe":
                    coeff = celing_price.price_list_route_direct_delivery.filtered(
                        lambda c: c.sales == self.order_number_oo_mf
                        and c.create_date_to >= create_date_start >= c.create_date_from
                    ).multiplier

                    price_plafond = self.get_price_plafond(coeff)
                # Send Mail
                else:
                    template_id.send_mail(
                        self.id, force_send=True, raise_exception=True
                    )

            self.price_plafond = price_plafond

    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    # ----------------------------------------------------------------------------------------------------
    # 8- overridden methods
    # ----------------------------------------------------------------------------------------------------
