# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestModel(TransactionCase):

    def setUp(self):
        super(TestModel, self).setUp()

    def test_some_action(self):
        # Create a new product
        product = self.env["product.product"].create(
            {"name": "Product Test V1", "default_code": "A10001"}
        )

        product_2 = self.env["product.product"].create(
            {"name": "Product Test V2", "default_code": "A10001"}
        )
        self.assertEqual(product.default_code, product_2.default_code)
