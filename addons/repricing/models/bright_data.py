# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from pexpect import run
import requests
import json
import logging
import os
import pandas as pd
import shutil
import subprocess
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
from odoo.tools import ustr

_logger = logging.getLogger(__name__)
PASSWORD_ARG = '(?i)password'
PASSWORD_VALUE = '82dv7P7uHTd8uVW#G5c\r'
TARGET_FOLDER = '/var/www/kobleo/brightdata'
HOST = '35.181.31.152'
USER = 'maki'


class BrightDataCollector(models.Model):
    _name = 'bright.data.collector'
    _description = 'Bright Data Collector'

    name = fields.Char(
        string='API Name'
    )
    collector = fields.Char(
        string='Collecteur',
        required=True
    )
    bearer_token = fields.Char(
        string="Bearer Token",
        required=True
    )
    is_activated = fields.Boolean(
        string='Active'
    )

    def can_convert_to_int(self, string):
        try:
            int(string)

            return True
        except ValueError:
            return False

    def import_files_csv_bright_data(self):
        """
        @params:
        @return: Import Files from SSH server to Odoo Server
        """
        PATH = '/home/odoo/brightdata/'
        if not os.path.exists(PATH):
            os.makedirs(PATH)
        cmd = "rsync -avzhe ssh maki@35.181.31.152:/var/www/kobleo/brightdata/ /home/odoo/brightdata"
        run(cmd, events={PASSWORD_ARG: PASSWORD_VALUE})
        for count, filename in enumerate(os.listdir("/home/odoo/brightdata/")):
            dst = "Download_" + str(count) + ".xlsx"
            src = '/home/odoo/brightdata/' + filename
            dst = '/home/odoo/brightdata/' + dst
            os.rename(src, dst)

    def update_product_values(self):
        _logger.info('--------------------------------------------------------------------')
        _logger.info('--------------------------------------------------------------------')
        _logger.info('--------------------------------------------------------------------')
        _logger.info('___________ Starting Update Product Value From Excel ___________')
        _logger.info('--------------------------------------------------------------------')
        _logger.info('--------------------------------------------------------------------')
        _logger.info('--------------------------------------------------------------------')
        PRODUCT = self.env['product.product']
        self.import_files_csv_bright_data()
        self._clean_repository_bright_data_from_server()
        file_count = subprocess.getoutput('ls /home/odoo/brightdata | wc -l')
        for i in range(0, int(file_count)):
            date_now = str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
            xml_file = '/home/odoo/brightdata/Download_'
            xml_file = xml_file + str(i) + '.xlsx'
            file_size = os.path.getsize(xml_file)
            if file_size > 0:
                data = pd.read_excel(xml_file, encoding="utf-8")
                for index, row in data.iterrows():
                    column_id = row['ID']
                    if pd.isnull(column_id) or not column_id:
                        continue

                    product_id = int(column_id) if self.can_convert_to_int(column_id) else False

                    if not product_id:
                        continue
                    # SET EXCEL COLUMNS
                    product = PRODUCT.browse(product_id)
                    column_buybox_seller_price = row['Buybox seller price']
                    column_buybox_seller_name = row['Buybox seller name']
                    column_first_seller_name = row['First seller name']
                    column_first_seller_price = row['First seller price']
                    column_products_review = row['Products reviews']
                    column_buybox_shipping = row['Buybox Shipping']
                    column_buybox_stock = row['Buybox stock']
                    column_buybox_mf = row['Buybox MF']
                    column_date_scrapping = row['Date scrapping']
                    column_input = row['input']
                    column_seller_outillage_online = row['Seller Outillage Online']
                    buybox_seller_price = product.buybox_seller_price if pd.isnull(
                        column_buybox_seller_price) else float(
                        column_buybox_seller_price)
                    buybox_seller_name = product.buybox_seller_name if pd.isnull(
                        column_buybox_seller_name) else column_buybox_seller_name
                    first_seller_name = product.first_seller_name if pd.isnull(
                        column_first_seller_name) else column_first_seller_name
                    first_seller_price = product.first_seller_price if pd.isnull(column_first_seller_price) else float(
                        column_first_seller_price)
                    rating_mano = product.x_studio_ratings_mano_1 if pd.isnull(column_products_review) else int(
                        column_products_review)
                    buybox_shipping = product.x_studio_ratings_mano_1 if pd.isnull(column_buybox_shipping) else int(
                        column_buybox_shipping)
                    buybox_stock = product.x_studio_ratings_mano_1 if pd.isnull(column_buybox_stock) else int(
                        column_buybox_stock)
                    buybox_mf = product.buybox_mf if pd.isnull(column_buybox_mf) else column_buybox_mf
                    date_value = False
                    if column_date_scrapping:
                        date_scrapping_excel = column_date_scrapping.replace('/', '-')
                        date_value = datetime.strptime(date_scrapping_excel, "%d-%m-%Y").date()
                    date_scrapping = product.date_scrapping if not date_value else date_value

                    product.write({
                        'buybox_seller_price': buybox_seller_price,
                        'buybox_seller_name': buybox_seller_name,
                        'first_seller_name': first_seller_name,
                        'first_seller_price': first_seller_price,
                        'x_studio_ratings_mano_1': rating_mano,
                        'buybox_shipping': buybox_shipping,
                        'buybox_stock': buybox_stock,
                        'buybox_mf': buybox_mf,
                        'product_not_found': column_input,
                        'date_scrapping': date_scrapping,
                        'seller_outtilage_online': float(column_seller_outillage_online),
                    })
                shutil.move(xml_file, '/home/odoo/old_scrapping/scrapping' + '_' + date_now + '.xlsx')
            break

    def _clean_repository_bright_data_from_server(self):
        cmd = f'ssh {USER}@{HOST} rm {TARGET_FOLDER}/*'
        run(cmd, events={PASSWORD_ARG: PASSWORD_VALUE})

    def _post_data_collector(self, data):
        """
        This Method will send REQUEST POST to Brightdata
        @params data []
        @return: Json response
        """

        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.bearer_token}
        url = 'https://api.luminati.io/dca/trigger?collector=' + self.collector
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return json.loads(r.content)

    def collect_data_products(self):
        """
        This Method will send Products to  Brightdata to collect Data
        @return: XML File in Server
        """
        PRODUCT = self.env['product.product']
        CRON = self.env.ref('repricing.bright_data_collect_data_cron')
        domain = safe_eval(ustr(CRON.product_domain))
        fields = [
            'id',
            'default_code',
            'lst_price',
            'x_studio_url_mano'
        ]

        products = PRODUCT.with_context(lang='fr_FR').search_read(
            domain=domain,
            fields=fields,
        )
        data = []
        collectors = self.env['bright.data.collector'].search([('is_activated', '=', True)])
        # Clean repository
        self._clean_repository_bright_data_from_server()
        for product in products:
            data.append({
                "ID": product.get('id'),
                "Référence interne": product.get('default_code'),
                "Brand/Brand Name": product.get('lst_price'),
                "URL Mano": product.get('x_studio_url_mano')
            })
        _logger.info('data %s =', data)
        for collector in collectors:
            response = collector._post_data_collector(data)
            _logger.info('-------------------response---------------------- %s', response)
