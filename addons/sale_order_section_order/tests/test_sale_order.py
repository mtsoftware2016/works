from odoo.tests.common import TransactionCase


class TestSaleOrderLineAppliedMargin(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Partner = cls.env["res.partner"]
        cls.SaleOrder = cls.env["sale.order"]

        cls.product_1 = cls.Product.create(
            {"name": "product_1", "standard_price": 50, "lst_price": 50}
        )

        cls.partner = cls.Partner.create({"name": "partner"})

        cls.company = cls.env.ref("base.main_company")

    def test_sale_order_generate_equipments(self):
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    [
                        0,
                        "virtual_94",
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 1,
                            "product_uom": 1,
                            "price_unit": 50,
                        },
                    ]
                ],
            }
        )
        for line in order.order_line:
            line.margin_percentage = 100
            line._compute_amount()

        self.assertEqual(line.price_subtotal, 100)
