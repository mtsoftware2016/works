# -*- coding: utf-8 -*-
import json
import logging
from datetime import date, timedelta

import lxml.etree as et
import requests
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ManoMano(models.Model):
    _name = "mano.mano"

    # ----------------------------------------------------------------------------------------------------
    # 1- Fields
    # ----------------------------------------------------------------------------------------------------

    name = fields.Char(string="Name")

    login = fields.Char(string="Login")

    password = fields.Char(string="Password")

    # ----------------------------------------------------------------------------------------------------
    # 2- ORM Methods (create, write, unlink)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 2- Constraints methods (_check_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 3- Compute methods (namely _compute_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 4- Onchange methods (namely onchange_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 5- Actions methods (namely action_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 6- Technical methods (name must reflect the use)
    # ----------------------------------------------------------------------------------------------------

    def check_quantity_products(self, ids):
        check_qty = 0
        products = self.env["product.product"].browse(ids)
        for product in products:
            if product.virtual_available_without_incoming_qty_main <= 0:
                check_qty += 1
        if check_qty == len(products):
            return False
        else:
            return True

    @api.model
    def get_default_payment_method(self, journal_id):
        """@params journal_id: Journal Id for making payment
        @params context : Must have key 'ecommerce' and then return payment payment method based on Odoo Bridge used else return the default payment method for Journal
        @return: Payment method ID(integer)"""
        payment_method_ids = (
            self.env["account.journal"]
            .browse(journal_id)
            ._default_inbound_payment_methods()
        )
        if payment_method_ids:
            return payment_method_ids[0].id
        return False

    def test_connexion_mano(self):
        request = requests.get(
            "https://ws.monechelle.com/?login="
            + self.login
            + "&password="
            + self.password
            + "&method=get_orders"
        )
        text = request.text.replace("<![CDATA[", "").replace("]]>", "")
        if request.status_code == 200 and "Incorrect" not in text:
            raise UserError(_("Connexion avec Mano sucess"))
        else:
            raise UserError(_("Incorrect login or password"))

    def get_orders_mf(self, mano_connexion):
        """@params mano_connexion: credentials connexion to mano
        @return: Orders Mano method (list)"""

        date_arg = date.today() + timedelta(days=1)
        url = (
            "https://ws.monechelle.com/?login="
            + mano_connexion.login
            + "&password="
            + mano_connexion.password
            + "&method=get_last_orders"
            + "&date="
            + str(date_arg)
        )
        r = requests.get(url)
        _logger.info("request %s", r)
        data = et.fromstring(r.text.encode("utf-8"))
        return data.xpath("//order")

    def get_orders(self, mano_connexion):
        """@params mano_connexion: credentials connexion to mano
        @return: Orders Mano method (list)"""
        url = (
            "https://ws.monechelle.com/?login="
            + mano_connexion.login
            + "&password="
            + mano_connexion.password
            + "&method=get_orders"
        )
        r = requests.get(url)
        data = et.fromstring(r.text.encode("utf-8"))
        return data.xpath("//order")

    def get_last_orders(self, mano_connexion, date):
        """@params mano_connexion: credentials connexion to mano
        @return: Orders Mano method (list)"""
        url = (
            "https://ws.monechelle.com/?login="
            + mano_connexion.login
            + "&password="
            + mano_connexion.password
            + "&method=get_last_orders"
            + "&date="
            + date
        )
        r = requests.get(url)
        data = et.fromstring(r.text.encode("utf-8"))
        return data.xpath("//order")

    def accept_order(self, order_ref, mano_connexion):
        """@params order_ref: reference product
        @params mano_connexion : credentials connexion to mano
        @return: Confirm Order In Mano"""
        url = (
            "https://ws.monechelle.com/?login="
            + mano_connexion.login
            + "&password="
            + mano_connexion.password
            + "&method=accept_order&order_ref="
            + order_ref
        )
        requests.get(url)

    def refuse_order(self, order_ref, mano_connexion):
        """@params order_ref: reference product
        @params mano_connexion : credentials for connexion to mano
        @return: Refuse Order In Mano"""
        url = (
            "https://ws.monechelle.com/?login="
            + mano_connexion.login
            + "&password="
            + mano_connexion.password
            + "&method=refuse_order&order_ref="
            + order_ref
        )
        requests.get(url)

    # ----------------------------------------------------------------------------------------------------
    # 7- CRONs methods
    # ----------------------------------------------------------------------------------------------------

    @api.model
    def create_order_from_mano_mf(self):
        mano_connexion_mf = self.env.ref("mano_connexion.mano_connexion_is_mf")
        mano_connexion_mf_fr = self.env.ref("mano_connexion.mano_connexion_is_mf_fr")
        orders = self.get_orders_mf(mano_connexion_mf)
        orders_mf_fr = self.get_orders_mf(mano_connexion_mf_fr)

        for i, order in enumerate(orders):
            if not self.env["sale.order"].search(
                [("x_studio_rfrence_marketplace", "=", order.find("order_ref").text)]
            ):
                _logger.info("ref %s", order.find("order_ref").text)
                self.create_sale_order(order, "is_mf")
                self.env.cr.commit()

        for i, order in enumerate(orders_mf_fr):
            if not self.env["sale.order"].search(
                [("x_studio_rfrence_marketplace", "=", order.find("order_ref").text)]
            ):
                self.create_sale_order(order, "is_mf")
                self.env.cr.commit()

    def create_shipping(self, order, mano_connexion):
        """@params order: reference sale_order
        @params mano_connexion : credentials for connexion to mano
        @return: create shipping Order In Mano"""
        picking = False
        for item in order.picking_ids:
            if item.state == "done" and item.carrier_tracking_ref:
                picking = item
                break

        if (
            picking
            and not picking.shiping_mano_active
            and picking.carrier_tracking_ref
            and picking.carrier_id.tracking_url
        ):
            tracking_url_carrier = picking.carrier_id.tracking_url.replace(
                "@", picking.carrier_tracking_ref
            )
            url = (
                "https://ws.monechelle.com/?login="
                + mano_connexion.login
                + "&password="
                + mano_connexion.password
                + "&method=create_shipping&order_ref="
                + order.x_studio_rfrence_marketplace
                + "&tracking_number="
                + picking.carrier_tracking_ref
                + "&carrier="
                + picking.carrier_id.name
                + "&tracking_url="
                + tracking_url_carrier
            )
            requests.get(url)
            picking.shiping_mano_active = True

    def create_sale_order(self, order, country):
        template_id = self.env.ref("mano_connexion.mannon_error_email")
        template_id_creation = self.env.ref(
            "mano_connexion.mannon_error_email_creation"
        )
        # Create partner shipping address
        partners = []
        country_by_name_shipping = (
            self.env["res.country"]
            .search([("name", "like", order.find("shipping_address/country").text)])
            .id
        )
        country_by_code_shipping = (
            self.env["res.country"]
            .search([("code", "like", order.find("shipping_address/country_iso").text)])
            .id
        )

        partners.append(
            (
                0,
                0,
                {
                    "type": "delivery",
                    "street": order.find("shipping_address/address_1").text,
                    "street2": order.find("shipping_address/address_2").text,
                    "zip": order.find("shipping_address/zipcode").text,
                    "name": order.find("shipping_address/firstname").text
                    + " "
                    + order.find("shipping_address/lastname").text,
                    "mobile": order.find("shipping_address/phone").text,
                    "phone": order.find("shipping_address/phone").text,
                    "email": order.find("shipping_address/email").text,
                    "city": order.find("shipping_address/city").text,
                    "country_id": (
                        country_by_name_shipping
                        if country_by_name_shipping
                        else country_by_code_shipping
                    ),
                    "company_mano": order.find("shipping_address/company").text,
                },
            )
        )
        # Create partner billing address
        country_by_name = (
            self.env["res.country"]
            .search([("name", "like", order.find("billing_address/country").text)])
            .id
        )
        country_by_code = (
            self.env["res.country"]
            .search([("code", "like", order.find("billing_address/country_iso").text)])
            .id
        )

        partners.append(
            (
                0,
                0,
                {
                    "type": "invoice",
                    "is_professional": order.find(
                        "billing_address/is_professional"
                    ).text,
                    "street": order.find("billing_address/address_1").text,
                    "street2": order.find("billing_address/address_2").text,
                    "zip": order.find("billing_address/zipcode").text,
                    "name": order.find("billing_address/firstname").text
                    + " "
                    + order.find("billing_address/lastname").text,
                    "mobile": order.find("billing_address/phone").text,
                    "phone": order.find("billing_address/phone").text,
                    "email": order.find("billing_address/email").text,
                    "city": order.find("billing_address/city").text,
                    "country_id": (
                        country_by_name if country_by_name else country_by_code
                    ),
                    "company_mano": order.find("billing_address/company").text,
                },
            )
        )
        partner = self.env["res.partner"].create(
            {
                "name": order.find("firstname").text
                + " "
                + order.find("lastname").text,
                "email": order.find("billing_address/email").text,
                "customer_rank": 1,
                "child_ids": partners,
            }
        )
        lines = []
        sale_order_rejected = False
        is_dropshiping = False
        is_tnt_express = False
        for i in range(1, int(len(order.findall("products/product")) + 1)):
            product = self.env["product.product"].search(
                [
                    (
                        "default_code",
                        "=",
                        order.find("products/product[" + str(i) + "]/sku").text,
                    )
                ]
            )
            if len(product) >= 2:
                context = dict(self.env.context)
                context.update({"product_1": product[0].default_code})
                self.env.context = context
                template_id.send_mail(1, force_send=True, raise_exception=True)
                sale_order_rejected = True
                break
            if not product:
                context = dict(self.env.context)
                context.update(
                    {
                        "product_1": order.find(
                            "products/product[" + str(i) + "]/sku"
                        ).text
                    }
                )
                self.env.context = context
                template_id_creation.send_mail(1, force_send=True, raise_exception=True)
                sale_order_rejected = True
                break

            if (
                "TNT Express"
                in order.find("products/product[" + str(i) + "]/carrier").text
            ):
                is_tnt_express = True
            lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": self.env["product.product"]
                        .search(
                            [
                                (
                                    "default_code",
                                    "=",
                                    order.find(
                                        "products/product[" + str(i) + "]/sku"
                                    ).text,
                                )
                            ]
                        )
                        .id,
                        "product_uom_qty": order.find(
                            "products/product[" + str(i) + "]/quantity"
                        ).text,
                        "price_unit": float(
                            order.find("products/product[" + str(i) + "]/price").text
                        ),
                        "name": order.find(
                            "products/product[" + str(i) + "]/title"
                        ).text,
                    },
                )
            )
            # SHipping Price
            for route in product.route_ids:
                if route.name == "Livraison directe":
                    is_dropshiping = True
        if (
            "is_mf" not in country
            and not self.check_quantity_products(product.ids)
            and not is_dropshiping
        ):
            return False

        if float(order.find("shipping_price").text) > 0:
            lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": self.env["product.product"]
                        .search([("default_code", "=", "SHIP")])
                        .id,
                        "product_uom_qty": 1,
                        "price_unit": float(order.find("shipping_price").text),
                    },
                )
            )
        if not sale_order_rejected:
            vals = {
                "x_studio_rfrence_marketplace": order.find("order_ref").text,
                "date_order_mano": order.find("order_time").text,
                "update_order_mano": order.find("update_time").text,
                "is_mmf": (
                    "Mano Fulfillment"
                    if order.find("is_mmf").text == "1"
                    else "Outillage Online Fulfillment"
                ),
                "status_mano": order.find("status").text,
                "partner_id": partner.id,
                "order_line": lines,
                "is_mano": True,
                "is_french": True if country == "France" else False,
                "is_french_pro": True if country == "France Pro" else False,
                "is_germany": True if country == "Germany" else False,
                "is_spain": True if country == "Spain" else False,
                "is_italy": True if country == "Italy" else False,
                "relay_id": (
                    order.find("relay/id").text
                    if order.find("relay/id") is not None
                    else ""
                ),
                "relay_name": (
                    order.find("relay/name").text
                    if order.find("relay/name") is not None
                    else ""
                ),
                "relay_zipcode": (
                    order.find("relay/zipcode").text
                    if order.find("relay/zipcode") is not None
                    else ""
                ),
                "relay_city": (
                    order.find("relay/city").text
                    if order.find("relay/city") is not None
                    else ""
                ),
                "relay_country": (
                    order.find("relay/country").text
                    if order.find("relay/country") is not None
                    else ""
                ),
                "relay_address": (
                    order.find("relay/address").text
                    if order.find("relay/address") is not None
                    else ""
                ),
            }
            if country == "is_mf":
                vals.update({"warehouse_id": 2})
            sale_order = self.env["sale.order"].create(vals)
            sale_order.action_confirm()

            if country in ["France", "France Pro"] and is_tnt_express:
                for picking in sale_order.picking_ids:
                    picking.carrier_id = 90

            if country == "is_mf":
                for picking in sale_order.picking_ids:
                    for line in picking.move_ids_without_package:
                        line.quantity_done = line.product_uom_qty
                    picking.action_confirm()
                    picking.action_assign()
                    res_dict = picking.button_validate()
                    if res_dict:
                        wizard = self.env[(res_dict.get("res_model"))].browse(
                            res_dict.get("res_id")
                        )
                        wizard.process()

            invoice_id = sale_order.action_invoice_create()
            invoice = self.env["account.move"].browse(invoice_id[0])
            invoice.action_invoice_open()
            journal_id = 17
            if country == "is_mf":
                journal_id = 24
            context = {}
            if invoice:
                ctx = {
                    "default_invoice_ids": [[4, invoice.id, None]],
                    "active_model": "account.move",
                    "journal_type": "sale",
                    "search_disable_custom_filters": True,
                    "active_ids": [invoice.id],
                    "type": "out_invoice",
                    "active_id": invoice.id,
                }
                context.update(ctx)
                fields = [
                    "communication",
                    "currency_id",
                    "invoice_ids",
                    "payment_difference",
                    "partner_id",
                    "payment_method_id",
                    "payment_difference_handling",
                    "journal_id",
                    "state",
                    "writeoff_account_id",
                    "payment_date",
                    "partner_type",
                    "hide_payment_method",
                    "payment_method_code",
                    "amount",
                    "payment_type",
                ]
                default_vals = self.env["account.payment"].default_get(fields)
                payment_method_id = self.with_context(
                    context
                ).get_default_payment_method(journal_id)
                default_vals.update(
                    {"journal_id": journal_id, "payment_method_id": payment_method_id}
                )
                payment_obj = (
                    self.env["account.payment"]
                    .with_context(context)
                    .create(default_vals)
                )
                payment_obj.with_context(context).post()
            return sale_order

    @api.model
    def create_order_from_mano(self):
        mano_connexion_germany = self.env.ref("mano_connexion.mano_connexion_germany")
        mano_connexion_spain = self.env.ref("mano_connexion.mano_connexion_spain")
        mano_connexion_italy = self.env.ref("mano_connexion.mano_connexion_italie")
        mano_connexion = self.env.ref("mano_connexion.mano_connexion")
        mano_connexion_france_pro = self.env.ref("mano_connexion.mano_france_pro")

        orders = self.get_orders(mano_connexion)
        orders_germany = self.get_orders(mano_connexion_germany)
        orders_spain = self.get_orders(mano_connexion_spain)
        orders_italy = self.get_orders(mano_connexion_italy)
        orders_pro_france = self.get_orders(mano_connexion_france_pro)

        for order in orders:
            if not self.env["sale.order"].search(
                [("x_studio_rfrence_marketplace", "=", order.find("order_ref").text)]
            ):
                sale_order = self.create_sale_order(order, "France")
                if sale_order:
                    self.accept_order(order.find("order_ref").text, mano_connexion)
                else:
                    self.refuse_order(order.find("order_ref").text, mano_connexion)

        for order_germany in orders_germany:
            if not self.env["sale.order"].search(
                [
                    (
                        "x_studio_rfrence_marketplace",
                        "=",
                        order_germany.find("order_ref").text,
                    )
                ]
            ):
                sale_order = self.create_sale_order(order_germany, "Germany")
                if sale_order:
                    self.accept_order(
                        order_germany.find("order_ref").text, mano_connexion_germany
                    )
                else:
                    self.refuse_order(
                        order_germany.find("order_ref").text, mano_connexion_germany
                    )

        for order_spain in orders_spain:
            if not self.env["sale.order"].search(
                [
                    (
                        "x_studio_rfrence_marketplace",
                        "=",
                        order_spain.find("order_ref").text,
                    )
                ]
            ):
                sale_order = self.create_sale_order(order_spain, "Spain")
                if sale_order:
                    self.accept_order(
                        order_spain.find("order_ref").text, mano_connexion_spain
                    )
                else:
                    self.refuse_order(
                        order_spain.find("order_ref").text, mano_connexion_spain
                    )

        for order_italy in orders_italy:
            if not self.env["sale.order"].search(
                [
                    (
                        "x_studio_rfrence_marketplace",
                        "=",
                        order_italy.find("order_ref").text,
                    )
                ]
            ):
                sale_order = self.create_sale_order(order_italy, "Italy")
                if sale_order:
                    self.accept_order(
                        order_italy.find("order_ref").text, mano_connexion_italy
                    )
                else:
                    self.refuse_order(
                        order_italy.find("order_ref").text, mano_connexion_italy
                    )

        for order_pro in orders_pro_france:
            if not self.env["sale.order"].search(
                [
                    (
                        "x_studio_rfrence_marketplace",
                        "=",
                        order_pro.find("order_ref").text,
                    )
                ]
            ):
                sale_order = self.create_sale_order(order_pro, "France Pro")
                if sale_order:
                    self.accept_order(
                        order_pro.find("order_ref").text, mano_connexion_france_pro
                    )
                else:
                    self.refuse_order(
                        order_pro.find("order_ref").text, mano_connexion_france_pro
                    )

    @api.model
    def create_shipping_cron(self):
        mano_connexion = self.env.ref("mano_connexion.mano_connexion")
        mano_connexion_france_pro = self.env.ref("mano_connexion.mano_france_pro")
        orders_french_pro = self.env["sale.order"].search(
            [("is_mano", "=", True), ("is_french_pro", "=", True)]
        )
        orders = self.env["sale.order"].search(
            [("is_mano", "=", True), ("is_french", "=", True)]
        )

        for order_french in orders_french_pro:
            self.create_shipping(order_french, mano_connexion_france_pro)

        for order in orders:
            self.create_shipping(order, mano_connexion)

    @api.model
    def create_shipping_cron_spain(self):
        mano_connexion_spain = self.env.ref("mano_connexion.mano_connexion_spain")
        orders = self.env["sale.order"].search(
            [("is_mano", "=", True), ("is_spain", "=", True)]
        )
        for order in orders:
            self.create_shipping(order, mano_connexion_spain)

    @api.model
    def create_shipping_cron_italy(self):
        mano_connexion_italy = self.env.ref("mano_connexion.mano_connexion_italie")
        orders = self.env["sale.order"].search(
            [("is_mano", "=", True), ("is_italy", "=", True)]
        )
        for order in orders:
            self.create_shipping(order, mano_connexion_italy)

    @api.model
    def create_shipping_cron_germany(self):
        mano_connexion_germany = self.env.ref("mano_connexion.mano_connexion_germany")
        orders = self.env["sale.order"].search(
            [("is_mano", "=", True), ("is_germany", "=", True)]
        )
        for order in orders:
            self.create_shipping(order, mano_connexion_germany)

    @api.model
    def update_offers_mano(self):
        PRODUCT = self.env["product.product"]
        Param = self.env["ir.config_parameter"]
        API_KEY = Param.sudo().get_param("api_key_mano")
        SELLER_CONTRACT_ID = Param.sudo().get_param("seller_contract_id")
        CRON = self.env.ref("mano_connexion.mano_update_offers")
        template_mail = self.env.ref("mano_connexion.mano_error_update_offers")
        domain = safe_eval(ustr(CRON.product_domain))
        items = []
        products = PRODUCT.search(domain)
        headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
        url = "https://partnersapi.manomano.com/api/v2/offer-information/offers"
        for product in products:
            items.append(
                {
                    "sku": product.default_code,
                    "price": {"price_vat_included": product.lst_price},
                    "stock": {
                        "quantity": int(
                            product.virtual_available_without_incoming_qty_main
                        )
                    },
                }
            )
        payload = {
            "content": [{"seller_contract_id": int(SELLER_CONTRACT_ID), "items": items}]
        }
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(payload)
        )
        errors = json.loads(response.text)
        result = errors.get("content").get("errors")
        RESPONSE_ERRORS = result[0].get("errors")

        if RESPONSE_ERRORS:
            ERRORS_DATA = []
            for error in RESPONSE_ERRORS:
                if error.get("api_error_code") not in [
                    "10404",
                    "10405",
                    "10412",
                    "10409",
                ]:
                    ERRORS_DATA.append(error)

            context = dict(self.env.context)
            context.update({"errors": ERRORS_DATA})
            self.env.context = context
            _logger.info("ERRORS_DATA %s", ERRORS_DATA)
            if ERRORS_DATA:
                template_mail.send_mail(1, force_send=True, raise_exception=True)

    @api.model
    def update_offers_mano_fr(self):
        PRODUCT = self.env["product.product"]
        Param = self.env["ir.config_parameter"]
        API_KEY = Param.sudo().get_param("api_key_mano")
        SELLER_CONTRACT_ID = Param.sudo().get_param("contract_id_fr")
        CRON = self.env.ref("mano_connexion.mano_update_offers_fr")
        template_mail = self.env.ref("mano_connexion.mano_error_update_offers")
        domain = safe_eval(ustr(CRON.product_domain))
        items = []
        products = PRODUCT.search(domain)
        headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
        url = "https://partnersapi.manomano.com/api/v2/offer-information/offers"
        for product in products:
            route = product.route_ids.filtered(
                lambda route: route.name == "Livraison directe"
            )
            check_route = (
                5
                if route
                and product.announced_sale_delay <= 25
                and product.virtual_available_without_incoming_qty_main == 0
                else product.virtual_available_without_incoming_qty_main
            )
            if check_route < 0:
                check_route = 0

            items.append(
                {
                    "sku": product.default_code,
                    "price": {"price_vat_included": product.lst_price},
                    "stock": {"quantity": int(check_route)},
                }
            )
        payload = {
            "content": [{"seller_contract_id": int(SELLER_CONTRACT_ID), "items": items}]
        }
        data = json.dumps(payload)
        response = requests.request("PATCH", url, headers=headers, data=data)
        errors = json.loads(response.text)
        result = errors.get("content").get("errors")
        RESPONSE_ERRORS = result[0].get("errors")
        if RESPONSE_ERRORS:
            ERRORS_DATA = []
            for error in RESPONSE_ERRORS:
                if error.get("api_error_code") not in [
                    "10404",
                    "10405",
                    "10412",
                    "10409",
                ]:
                    ERRORS_DATA.append(error)

            context = dict(self.env.context)
            context.update({"errors": ERRORS_DATA})
            self.env.context = context
            _logger.info("ERRORS_DATA %s", ERRORS_DATA)
            if ERRORS_DATA:
                template_mail.send_mail(1, force_send=True, raise_exception=True)
