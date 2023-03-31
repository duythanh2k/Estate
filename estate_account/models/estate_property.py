# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

#   @Override method
    def action_sold(self):
        res = super().action_sold()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        # Another way to get the journal:
        # journal = self.env["account.move"].with_context(default_move_type="out_invoice")._get_default_journal()
        for record in self:
            self.env["account.move"].create(
                {
                    "partner_id": record.buyer.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": record.name,
                                "quantity": 1.0,
                                "price_unit": record.selling_price * 6.0 / 100.0,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Administrative fees",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                }
            )

        return res
