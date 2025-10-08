# Copyright 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line.agent_ids.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = sum(record.mapped("order_line.agent_ids.amount"))

    commission_total = fields.Float(
        string="Commissions",
        compute="_compute_commission_total",
        store=True,
    )

    partner_agent_ids = fields.Many2many(
        string="Agents",
        comodel_name="res.partner",
        compute="_compute_agents",
        search="_search_agents",
    )

    @api.depends("partner_agent_ids", "order_line.agent_ids.agent_id")
    def _compute_agents(self):
        for po in self:
            po.partner_agent_ids = [
                (6, 0, po.mapped("order_line.agent_ids.agent_id").ids)
            ]

    @api.model
    def _search_agents(self, operator, value):
        pol_agents = self.env["purchase.order.line.agent"].search(
            [("agent_id", operator, value)]
        )
        return [("id", "in", pol_agents.mapped("object_id.order_id").ids)]

    def recompute_lines_agents(self):
        self.mapped("order_line").recompute_agents()

    def recompute_lines_agents_amount(self):
        self.mapped("order_line").agent_ids._compute_amount()


class PurchaseOrderLine(models.Model):
    _inherit = [
        "purchase.order.line",
        "commission.mixin",
    ]
    _name = "purchase.order.line"

    agent_ids = fields.One2many(comodel_name="purchase.order.line.agent")

    @api.depends("order_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # reset previous agents
        for record in self:
            if record.order_id.partner_id and not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.order_id.partner_id, settlement_type="purchase_invoice"
                )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["agent_ids"] = [
            (0, 0, {"agent_id": x.agent_id.id, "commission_id": x.commission_id.id})
            for x in self.agent_ids
        ]
        return vals


class PurchaseOrderLineAgent(models.Model):
    _inherit = "commission.line.mixin"
    _name = "purchase.order.line.agent"
    _description = "Agent detail of commission line in purchase order lines"

    object_id = fields.Many2one(comodel_name="purchase.order.line")

    @api.depends(
        "commission_id",
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_qty",
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_qty,
            )
