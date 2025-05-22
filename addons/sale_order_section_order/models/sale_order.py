# -*- coding: utf-8 -*-


from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # ----------------------------------------------------------------------------------------------------
    # 1- ORM Methods (create, write, unlink)
    # ----------------------------------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, values_list):
        records = super(SaleOrder, self).create(values_list)
        # Add section ids.
        self._update_section_ids(records)
        return records

    def write(self, values):
        res = super(SaleOrder, self).write(values)

        # Add section ids.
        if values.get("order_line", False):
            for order in self:
                order._update_section_ids(order)

        return res

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

    def open_section_order_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order.section.wizard",
            "view_type": "form",
            "name": "Section Order",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"default_order_id": self.id},
        }

    def action_reorder_section_lines(self):
        for order in self:
            ordered_sections = order._get_ordered_sections()
            sequence_count = 0

            for section in ordered_sections:
                sequence_count += 10
                section.sequence = sequence_count
                section_lines = section.order_id.order_line.filtered(
                    lambda l: l.section_id == section
                )
                for line in section_lines:
                    sequence_count += 10
                    line.sequence = sequence_count

    # ----------------------------------------------------------------------------------------------------
    # 6- CRONs methods
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 7- Technical methods (name must reflect the use)
    # ----------------------------------------------------------------------------------------------------

    def _update_section_ids(self, orders):
        # Update section_id in lines here
        last_section_id = False

        for order in orders:
            for line in order.order_line:
                if line.display_type == "line_section":
                    last_section_id = line
                    continue

                if last_section_id:
                    line.section_id = last_section_id

    def _get_ordered_sections(self):
        self.ensure_one()
        sections = self.order_line.filtered(lambda l: l.display_type == "line_section")
        ordered_sections = list(sections)

        for section in sections:
            # We do nothing, the section keeps its location.
            if not section.shift_mode:
                continue

            shift_mode = section.shift_mode
            if shift_mode == "start":
                ordered_sections.remove(section)
                ordered_sections.insert(0, section)

            elif shift_mode == "end":
                ordered_sections.remove(section)
                ordered_sections.append(section)

            elif shift_mode == "before":
                ordered_sections.remove(section)
                position = ordered_sections.index(section.target_section_id)
                ordered_sections.insert(position, section)

            elif shift_mode == "after":
                ordered_sections.remove(section)
                position = ordered_sections.index(section.target_section_id)
                ordered_sections.insert(position + 1, section)

        return ordered_sections

    def _reset_section_order_information(self):
        order_lines = self.mapped("order_line")
        order_lines.write({"target_section_id": False, "shift_mode": False})

    # ----------------------------------------------------------------------------------------------------
    # 8- overridden methods
    # ----------------------------------------------------------------------------------------------------

    def action_confirm(self):
        self.action_reorder_section_lines()
        self._reset_section_order_information()
        return super(SaleOrder, self).action_confirm()
