# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

ABSOLUTE_POSITIONS = ("start", "end")


class SaleOrderSectionWizard(models.TransientModel):
    _name = "sale.order.section.wizard"
    _description = "Sale Order Section wizard"

    order_id = fields.Many2one(
        string="Order", comodel_name="sale.order", ondelete="cascade", required=True
    )

    section_id = fields.Many2one(
        string="Section",
        comodel_name="sale.order.line",
        ondelete="cascade",
        domain="[('display_type','=', 'line_section')]",
        required=True,
    )

    target_section_id = fields.Many2one(
        string="Target Section",
        comodel_name="sale.order.line",
        ondelete="cascade",
        domain="[('display_type','=', 'line_section')]",
        required=False,
    )

    shift_mode = fields.Selection(
        selection=[
            ("start", "Order Start"),
            ("end", "Order End"),
            ("before", "Before"),
            ("after", "After"),
        ],
        default="start",
        required=True,
    )

    # ----------------------------------------------------------------------------------------------------
    # 1- ORM Methods (create, write, unlink)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 2- Constraints methods (_check_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 3- Compute methods (namely _compute_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 4- Onchange methods (namely onchange_***)
    # ----------------------------------------------------------------------------------------------------

    @api.onchange("shift_mode")
    def onchange_shift_mode(self):
        self.ensure_one()
        if self.shift_mode in ABSOLUTE_POSITIONS:
            self.target_section_id = False

    # ----------------------------------------------------------------------------------------------------
    # 5- Actions methods (namely action_***)
    # ----------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------
    # 6- Technical methods (name must reflect the use)
    # ----------------------------------------------------------------------------------------------------

    def save_section_sequence(self):
        self.ensure_one()

        section = self.section_id

        # Store re-order information on the section.
        section.write(
            {
                "target_section_id": self.target_section_id
                and self.target_section_id.id,
                "shift_mode": self.shift_mode,
            }
        )

        # No point in having two sections to put at the start of the order,
        # we keep only the most recent one.
        if self.shift_mode in ABSOLUTE_POSITIONS:
            order_lines = section.order_id.order_line
            absolute_position_sections = order_lines.filtered(
                lambda l: l.display_type == "line_section"
                and l.shift_mode == self.shift_mode
                and l != section
            )
            absolute_position_sections.write(
                {"target_section_id": False, "shift_mode": False}
            )

    # ----------------------------------------------------------------------------------------------------
    # 6- Overridden methods
    # ----------------------------------------------------------------------------------------------------

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        context = self.env.context
        active_id = context.get("active_model") == "sale.order" and context.get(
            "active_id", False
        )
        res["order_id"] = active_id
        return res
