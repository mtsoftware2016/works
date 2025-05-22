# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta

from odoo import _, http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request
from odoo.osv.expression import OR

item_per_page = 10


class OrderRequest(http.Controller):

    @http.route("/buy_product", type="json", auth="public", website=True, csrf=False)
    def buy_product(self, **kw):
        order = request.env["order.request"].browse(int(kw.get("order_id")))
        line = []
        purchase = (
            request.env["purchase.order"]
            .sudo()
            .create(
                {
                    "partner_id": order.vendor_id.id,
                    "order_request": order.id,
                }
            )
        )
        line.append(
            (
                0,
                0,
                {
                    "order_id": purchase.id,
                    "product_id": order.line_ids.product_id.id,
                    "name": order.line_ids.product_id.sudo().name,
                    "product_qty": order.line_ids.quantity,
                    "price_unit": order.line_ids.unit_price,
                    "product_uom": order.line_ids.product_id.sudo().uom_po_id.id,
                    "date_planned": datetime.now(),
                    "taxes_id": order.line_ids.sudo().tax_ids.ids,
                },
            )
        )
        purchase.write(
            {
                "order_line": line,
            }
        )
        if purchase:
            order.write({"state": "purchase_in_progress"})
        return order.state

    @http.route("/reject_order", type="json", auth="public", website=True, csrf=False)
    def reject_orders(self, **kw):
        order = request.env["order.request"].browse(int(kw.get("order_id")))
        template_id = request.env.ref("portal_purchase_request.order_rejected_mail")
        url = "/order/" + slug(order)
        context = dict(request.env.context)
        context.update(
            {
                "name": order.sudo().user_id.name,
                "url": url,
                "order_number": order.name,
                "email_to": order.sudo().user_id.partner_id.email,
            }
        )
        request.env.context = context

        template_id.sudo().send_mail(order.id, force_send=True, raise_exception=True)
        order.write({"state": "rejected"})
        return order.state

    @http.route("/accept_order", type="json", auth="public", website=True, csrf=False)
    def accept_orders(self, **kw):
        order = request.env["order.request"].browse(int(kw.get("order_id")))
        template_id = request.env.ref("portal_purchase_request.order_approved_mail")
        url = "/order/" + slug(order)
        context = dict(request.env.context)
        context.update(
            {
                "name": order.sudo().user_id.name,
                "url": url,
                "order_number": order.name,
                "email_to": order.sudo().user_id.partner_id.email,
            }
        )
        request.env.context = context
        template_id.sudo().send_mail(order.id, force_send=True, raise_exception=True)
        order.write({"state": "approved"})
        return order.state

    # GET Vendors
    @http.route(
        "/get_vendors_list", type="json", auth="public", website=True, csrf=False
    )
    def get_vendors_list(self, **kw):
        vendors_list = []
        product = (
            request.env["product.product"].sudo().browse(int(kw.get("product_id")))
        )
        employee = (
            request.env["hr.employee"].sudo().search([("user_id", "=", request.uid)])
        )
        tax = employee.tax_id if employee.tax_id else product.sudo().supplier_taxes_id
        for seller in product.seller_ids:
            vendors_list.append((seller.name.id, seller.name.name, seller.price))
        return {"vendors": vendors_list, "taxes": tax.amount}

    def check_user_authorization(self, user):
        authorization = True if not user.date_baned else False
        baned_date = user.date_baned + timedelta(days=30) if user.date_baned else False
        if baned_date and datetime.now() >= baned_date:
            authorization = True
            user.sudo().date_baned = False
        return authorization

    @http.route(
        ["/order_requests", "/order_requests/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def display_order_requests(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        search=None,
        search_in="name",
        **kw
    ):
        authorization = False
        values = {}
        current_user = request.env["res.users"].browse(request.uid)
        group_user = current_user.is_user
        group_manager = current_user.is_manager
        if group_user:
            authorization = self.check_user_authorization(current_user)
        domain = []
        if group_user:
            domain += [("user_id", "=", request.uid)]

        searchbar_sortings = {
            "date_created": {"label": _("Date Created"), "order": "create_date desc"},
            "name": {"label": _(" Name"), "order": "name asc"},
            "state": {"label": _(" State"), "order": "state asc"},
        }

        searchbar_inputs = {
            "name": {
                "input": "name",
                "label": _('Search <span class="nolabel"> (in  Name)</span>'),
            },
        }
        if not sortby:
            sortby = "date_created"
        order = searchbar_sortings[sortby]["order"]
        # count for pager
        request_count = request.env["order.request"].search_count(domain)
        # pager
        pager = portal_pager(
            url="/order_requests",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=request_count,
            page=page,
            step=item_per_page,
        )
        # search
        if search:
            search_domain = []
            if search_in in ("name"):
                search_domain = OR([search_domain, [("name", "ilike", search)]])
            domain += search_domain

        order_requests = request.env["order.request"].search(
            domain, limit=item_per_page, offset=pager["offset"], order=order
        )

        values.update(
            {
                "page_name": "purchase",
                "pager": pager,
                "default_url": "/order_requests",
                "sortby": sortby,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "search": search,
                "requests_order": order_requests,
                "is_manager": group_manager,
                "authorization": authorization,
                "create": current_user.authorization_create,
            }
        )
        return request.render("portal_purchase_request.portal_order_requests", values)

    @http.route("/new/order", type="http", auth="public", website=True)
    def render_to_order_request_create(self, **kw):

        request.env.cr.execute(
            "SELECT * FROM  product_product_res_users_rel where res_users_id = %s",
            (request.uid,),
        )
        _res = request._cr.dictfetchall()
        product_ids = [item.get("product_product_id") for item in _res]
        products = request.env["product.product"].sudo().browse(product_ids)
        product_filtered = products.filtered(
            lambda product: product.categ_id.is_employee_autorised
        )
        vals = {
            "products": product_filtered,
            "page_name": "new_request",
        }
        return request.render("portal_purchase_request.create_order_request", vals)

    @http.route("/order_requests/create", type="http", auth="public", website=True)
    def save_order_request(self, **kw):
        current_user = request.env["res.users"].browse(request.uid)
        lines = []
        employee = (
            request.env["hr.employee"].sudo().search([("user_id", "=", request.uid)])
        )
        product = request.env["product.product"].browse(int(kw.get("product")))
        tax = (
            [employee.tax_id.id]
            if employee.tax_id
            else product.sudo().supplier_taxes_id.ids
        )
        lines.append(
            (
                0,
                0,
                {
                    "quantity": int(kw.get("quantity")),
                    "unit_price": float(kw.get("price")),
                    "product_id": int(kw.get("product")),
                    "tax_ids": [(6, 0, tax)],
                },
            )
        )
        list_attchement_ids = []
        upload_file_count = (
            int(kw.get("upload_file_count")) if kw.get("upload_file_count") else 0
        )
        list_attachment_stored = []
        for i in range(0, upload_file_count + 1):
            if kw.get(str(i)):
                list_attchement_ids.append(kw.get(str(i)))
        # Store Files in IR Attachment
        ir_attachment = request.env["ir.attachment"]
        for file in list_attchement_ids:
            if file:
                attachment = ir_attachment.sudo().create(
                    {
                        "name": file.filename,
                        "datas": base64.encodestring(file.read()),
                        "store_fname": file.filename,
                        "res_model": "order.request",
                        "res_id": request.env.user.id,
                        "type": "binary",
                    }
                )
                list_attachment_stored.append(attachment.id)

        # Create Order Request
        order_request = request.env["order.request"].create(
            {
                "vendor_id": int(kw.get("vendor")),
                "line_ids": lines,
                "user_id": request.uid,
                "attachment_ids": (
                    [(6, 0, list_attachment_stored)] if list_attachment_stored else None
                ),
            }
        )
        current_user.sudo().write({"authorization_create": False})
        # Send Email To Manager
        user_manager = (
            request.env["res.users"].sudo().search([("is_manager", "=", True)], limit=1)
        )
        template_id = request.env.ref("portal_purchase_request.manager_request_mail")
        url = "/order/" + slug(order_request)
        context = dict(request.env.context)
        context.update(
            {
                "url": url,
                "manager_mail": user_manager.partner_id.email,
                "manager_name": user_manager.partner_id.name,
            }
        )
        request.env.context = context
        template_id.sudo().send_mail(
            order_request.id, force_send=True, raise_exception=True
        )

        return http.request.redirect("/order_requests")

    @http.route(
        '/order/<model("order.request"):order>',
        type="http",
        auth="public",
        website=True,
    )
    def render_to_display_order_request(self, **kw):
        current_user = request.env["res.users"].browse(request.uid)
        group_user = current_user.is_user
        group_manager = current_user.is_manager
        vals = {
            "page_name": "order_request",
            "is_manager": group_manager,
            "is_user": group_user,
            "order": kw.get("order"),
            "vendor_name": kw.get("order").sudo().vendor_id.name,
            "partner": kw.get("order").user_id.sudo().partner_id,
        }
        return request.render("portal_purchase_request.display_order_request", vals)
