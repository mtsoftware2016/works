# Copyright 2022 Maki Turki
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
from xml.dom import minidom

from lxml import etree, html
from odoo import api, models
from pexpect import run

_logger = logging.getLogger(__name__)

PASSWORD_ARG = "(?i)password"
PASSWORD_VALUE = "82dv7P7uHTd8uVW#G5c\r"
TARGET_FOLDER = "/var/www/kobleo/google/"
FILE = "/home/odoo/flux_google_shopping_France.xml"
BUYBOX_STATUS = [
    "buybox_recuperee",
    "buybox_consolide",
    "buybox_without_concurrent",
    "buybox_with_concurrent",
    "buybox_with_concurrent_plafond",
]


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _check_availability_stock(self, product):
        """Check Availabitlity stock.
        :param  product:
        :return Stock Availability (str)
        """

        stock = "out_of_stock"
        if (
            product.virtual_available_without_incoming_qty_main >= 1
            or product.stock_virtual_drop >= 1
            or product.announced_sale_delay <= 5
        ):
            stock = "in_stock"
        return stock

    def _check_product_condition(self, product):
        """Check Product Condition.
        :param  product:
        :return Product Condition (str)
        """

        product_state = ""
        if product.product_state == "new":
            product_state = "new"
        elif product.product_state in ["good_case", "right_case"]:
            product_state = "refurbished"
        elif product.product_state in ["used_good_case", "used_good_case_right"]:
            product_state = "used "

        return product_state

    def _prepare_custom_label(self, product):
        """Prepare Custom Label.
        :param  product:
        :return Product Custom Label(str)
        """
        custom_label = ""
        if (
            product.order_count_12 >= 20
            and product.status_repricing_old in BUYBOX_STATUS
            and (
                product.virtual_available_without_incoming_qty_main >= 1
                or product.stock_virtual_drop >= 1
                or product.announced_sale_delay <= 5
            )
        ):
            custom_label = "Ventes &gt;=20, Stock et Buybox "

        elif (
            19 >= product.order_count_12 >= 5
            and product.status_repricing_old in BUYBOX_STATUS
            and (
                product.virtual_available_without_incoming_qty_main >= 1
                or product.stock_virtual_drop >= 1
                or product.announced_sale_delay <= 5
            )
        ):
            custom_label = "Ventes =5-19, Stock et Buybox "

        elif (
            1 <= product.order_count_12 <= 4
            and product.status_repricing_old in BUYBOX_STATUS
            and (
                product.virtual_available_without_incoming_qty_main >= 1
                or product.stock_virtual_drop >= 1
                or product.announced_sale_delay <= 5
            )
        ):
            custom_label = "Ventes =1-4, Stock et Buybox "

        elif (
            product.order_count_12 < 1
            and product.status_repricing_old in BUYBOX_STATUS
            and (
                product.virtual_available_without_incoming_qty_main >= 1
                or product.stock_virtual_drop >= 1
                or product.announced_sale_delay <= 5
            )
        ):
            custom_label = "Pas de ventes, Stock et Buybox "

        return custom_label

    def _prepare_additional_image_link(self, root, item, product):
        """Prepare Additional Image Link.
        :param  root:
        :param  item:
        :param  product:
        :return Create additional Image Links
        """

        additional_link_tag = "g:additional_image_link"
        additional_image_link_1 = root.createElement(additional_link_tag)
        additional_image_link_2 = root.createElement(additional_link_tag)
        additional_image_link_3 = root.createElement(additional_link_tag)
        additional_image_link_4 = root.createElement(additional_link_tag)
        additional_image_link_5 = root.createElement(additional_link_tag)

        if product.x_studio_url_image2:
            additional_image_link_1.appendChild(
                root.createTextNode(product.x_studio_url_image2)
            )
            item.appendChild(additional_image_link_1)

        if product.x_studio_url_image3_1:
            additional_image_link_2.appendChild(
                root.createTextNode(product.x_studio_url_image3_1)
            )
            item.appendChild(additional_image_link_2)

        if product.x_studio_url_image4:
            additional_image_link_3.appendChild(
                root.createTextNode(product.x_studio_url_image4)
            )
            item.appendChild(additional_image_link_3)

        if product.x_studio_url_image5:
            additional_image_link_4.appendChild(
                root.createTextNode(product.x_studio_url_image5)
            )
            item.appendChild(additional_image_link_4)

        if product.x_studio_url_image6:
            additional_image_link_5.appendChild(
                root.createTextNode(product.x_studio_url_image6)
            )
            item.appendChild(additional_image_link_5)

    def text_from_html(self, html_content):
        """Extract text from an HTML field in a generator.

        :param  html_content:
            HTML contents from where to extract the text.
        :return Text (str)

        """
        try:
            doc = html.fromstring(html_content)
        except (TypeError, etree.XMLSyntaxError, etree.ParserError):
            _logger.exception("Failure parsing this HTML:\n%s", html_content)
            return ""
        words = "".join(doc.xpath("//text()")).split()
        text = " ".join(words)
        return text

    def _export_merchant_google_file_to_server(self):
        """Export Merchant Google XML File to Server.
        :return XML File in Server
        """

        cmd = f"rsync -rav {FILE} maki@35.181.31.152:{TARGET_FOLDER}"
        run(cmd, events={PASSWORD_ARG: PASSWORD_VALUE})
        os.remove(FILE)

    @api.model
    def _create_google_merchant_product_file(self):
        PRODUCT_PRODUCT = self.env["product.product"]

        domain = [
            ("sale_ok", "=", True),
            ("active", "=", True),
            ("default_code", "!=", False),
            ("name", "!=", False),
            ("website_description", "!=", False),
            ("x_studio_url_image1", "!=", False),
            ("categ_id", "!=", False),
            ("x_studio_url_site_magento", "!=", False),
            ("lst_price", ">=", 1),
        ]

        products = PRODUCT_PRODUCT.with_context(lang="fr_FR").search(domain)
        _logger.info("product %", products)
        root = minidom.Document()
        root.toxml(encoding="utf-8")
        rss = root.createElement("rss")
        channel = root.createElement("channel")
        title = root.createElement("title")
        title.appendChild(root.createTextNode("Kobleo.com"))
        link = root.createElement("link")
        link.appendChild(root.createTextNode("https://kobleo.com"))
        description = root.createElement("description")
        description.appendChild(
            root.createTextNode("Kobleo by Outillage Online: bricoler, rénover, bâtir")
        )
        rss.setAttribute("xmlns:g", "http://base.google.com/ns/1.0")
        rss.setAttribute("version", "2.0")
        channel.appendChild(title)
        channel.appendChild(link)
        channel.appendChild(description)

        for product in products:
            item = root.createElement("item")
            id = root.createElement("g:id")
            title = root.createElement("g:title")
            description = root.createElement("g:description")
            link = root.createElement("g:link")
            image_link = root.createElement("g:image_link")
            availability = root.createElement("g:availability")
            condition = root.createElement("g:condition")
            price = root.createElement("g:price")
            custom_label_0 = root.createElement("g:custom_label_0")
            custom_label_1 = root.createElement("g:custom_label_1")
            brand = root.createElement("g:brand")
            gtin = root.createElement("g:gtin")
            mpn = root.createElement("g:mpn")
            gender = root.createElement("g:gender")
            adult = root.createElement("g:adult")
            ships_from_country = root.createElement("g:ships_from_country")
            cost_of_goods_sold = root.createElement("g:cost_of_goods_sold")
            product_length = root.createElement("g:product_length")
            product_width = root.createElement("g:product_width")
            product_height = root.createElement("g:product_height")
            product_weight = root.createElement("g:product_weight")
            id.appendChild(
                root.createTextNode(
                    str(product.x_studio_odoo_id) if product.x_studio_odoo_id else ""
                )
            )
            title.appendChild(
                root.createTextNode(product.long_name if product.long_name else "")
            )
            description.appendChild(
                root.createTextNode(
                    self.text_from_html(product.website_description)
                    if product.website_description
                    else ""
                )
            )
            link.appendChild(root.createTextNode(product.x_studio_url_site_magento))
            image_link.appendChild(root.createTextNode(product.x_studio_url_image1))
            availability.appendChild(
                root.createTextNode(self._check_availability_stock(product))
            )
            lst_price = (
                f"{str(round(product.sale_price_kobleo, 2))} {product.currency_id.name}"
                if product.sale_price_kobleo
                else ""
            )
            price_cost_of_goods_sold = (
                f"{str(round(product.price, 2))} {product.currency_id.name}"
                if product.price
                else ""
            )
            price.appendChild(root.createTextNode(lst_price))
            condition.appendChild(
                root.createTextNode(self._check_product_condition(product))
            )
            custom_label_0.appendChild(
                root.createTextNode(self._prepare_custom_label(product))
            )
            if product.benefice_net >= 15:
                custom_label_1.appendChild(root.createTextNode("Mage nette >= 15€ "))
            brand.appendChild(
                root.createTextNode(
                    product.product_brand_id.name if product.product_brand_id else ""
                )
            )
            mpn.appendChild(root.createTextNode(product.default_code))
            gender.appendChild(root.createTextNode("unisex"))
            adult.appendChild(root.createTextNode("no"))
            gtin.appendChild(
                root.createTextNode(
                    product.x_studio_code_barre if product.x_studio_code_barre else ""
                )
            )
            ships_from_country.appendChild(root.createTextNode("FR"))
            cost_of_goods_sold.appendChild(
                root.createTextNode(price_cost_of_goods_sold)
            )
            product_length.appendChild(
                root.createTextNode(
                    str(product.length) + " cm" if product.length else ""
                )
            )
            product_width.appendChild(
                root.createTextNode(str(product.width) + " cm" if product.width else "")
            )
            product_height.appendChild(
                root.createTextNode(
                    str(product.height) + " cm" if product.height else ""
                )
            )
            product_weight.appendChild(
                root.createTextNode(
                    str(product.weight) + " kg" if product.weight else ""
                )
            )
            item.appendChild(id)
            item.appendChild(title)
            item.appendChild(description)
            item.appendChild(link)
            item.appendChild(image_link)
            item.appendChild(condition)
            item.appendChild(availability)
            item.appendChild(price)
            item.appendChild(cost_of_goods_sold)
            item.appendChild(ships_from_country)
            item.appendChild(gtin)
            item.appendChild(brand)
            item.appendChild(gender)
            item.appendChild(product_length)
            item.appendChild(product_width)
            item.appendChild(product_height)
            item.appendChild(product_weight)
            item.appendChild(adult)
            item.appendChild(mpn)
            item.appendChild(custom_label_0)
            item.appendChild(custom_label_1)
            self._prepare_additional_image_link(root, item, product)
            channel.appendChild(item)

        rss.appendChild(channel)
        root.appendChild(rss)
        xml_str = root.toprettyxml(encoding="utf-8")
        with open(FILE, "wb") as f:
            f.write(xml_str)
        self._export_merchant_google_file_to_server()
