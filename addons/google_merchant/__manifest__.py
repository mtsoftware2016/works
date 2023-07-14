# Copyright 2022 Maki Turki
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Google Merchant',
    'version': '16.0.0.0',
    'category': 'sale',
    'description': """Generate Google Merchant XML File
     """,
    'summary': 'Generate Google Merchant XML File',
    'author': 'Maki Turki',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'outillageonline_base',
    ],
    'data': [
        ### Views ######
        'data/google_merchant_cron.xml',
    ],
}
