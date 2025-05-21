# pylint: disable=pointless-statement
{
    "name": "Purchase Request",
    "summary": """
        This module allow employee to create request to purchase product from Portal """,
    "description": """
        Long description of module's purpose
    """,
    "author": "Maki Turki",
    "category": "Uncategorized",
    "version": "13",
    "depends": [
        "base",
        "sale",
        "website",
        "purchase",
        "mail",
        "hr",
        "stock",
        "sale_management",
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        # data
        "data/request_order_sequence.xml",
        "data/request_order_mail.xml",
        "data/notification_employee.xml",
        "data/notification_pickup_mail.xml",
        "data/manager_request_mail.xml",
        # views
        "views/hr_employee_form_view.xml",
        "views/order_request.xml",
        "views/product_form_view.xml",
        "views/product_category_form_view.xml",
        "views/res_users_form_view.xml",
        # Website
        "views/assets.xml",
        "views/portal_home.xml",
        "views/order_request_portal.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
