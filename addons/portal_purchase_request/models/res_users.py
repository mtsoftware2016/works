# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.base.models.res_users import name_selection_groups
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_user = fields.Boolean(string='Purchase User')
    is_manager = fields.Boolean(string='Purchase Manager')
    authorization_create = fields.Boolean(string='Authorization For Creation Purchase', default=True)
    date_baned = fields.Datetime(string='Date Banned')

    @api.onchange('is_user')
    def is_user_on_change(self):
        if self.is_user:
            self.is_manager = False

    @api.onchange('is_manager')
    def is_manager_on_change(self):
        if self.is_manager:
            self.is_user = False

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        group_user_types = self.env['res.groups'].search(
            [('category_id', '=', self.env.ref('base.module_category_user_type').id)])
        field_user_type = name_selection_groups(group_user_types.ids)
        portal = vals.get(str(field_user_type))
        portal_id = self.env.ref('base.group_portal').id
        if portal != portal_id and (vals.get('is_user') or vals.get('is_manager')):
            raise ValidationError('Sorry you are not allowed please Change to portal User')
        return res

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        group_user_types = self.env['res.groups'].search(
            [('category_id', '=', self.env.ref('base.module_category_user_type').id)])
        field_user_type = name_selection_groups(group_user_types.ids)
        portal = vals.get(str(field_user_type))
        portal_id = self.env.ref('base.group_portal').id
        if portal and portal != portal_id and (
                vals.get('is_user') or vals.get('is_manager') or self.is_user or self.is_manager):
            raise ValidationError('Sorry you are not allowed please Change to portal User')
        return res
