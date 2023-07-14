# -*- coding: utf-8 -*-
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerUserPortal(CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        current_user = request.env['res.users'].browse(request.uid)
        group_user = current_user.is_user
        group_manager = current_user.is_manager
        domain = []
        if group_user:
            domain += [('user_id', '=', request.uid)]
        order_requests = request.env['order.request'].search_count(domain)
        values = self._prepare_portal_layout_values()
        values.update({
            'order_requests': order_requests,
            'group_manager': group_manager,
            'group_user': group_user
        })
        return request.render("portal.portal_my_home", values)
