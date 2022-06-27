# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

#    @Override method
    def action_sold(self):
        invoice_vals = {}
        # Add invoice_line_ids
        line_ids = [
            Command.create({
                "name": "6% of the selling price",
                "quantity": 5,
                "price_unit": self.selling_price * 6/100,
            }),
            Command.create({
                "name": "An additional 100.00 from administrative fees",
                "quantity": 5,
                "price_unit": 100.00,
            }),
        ]
        # Invoice values
        invoice_vals['partner_id'] = self.buyer
        invoice_vals['move_type'] = "out_invoice"
        invoice_vals['journal_id'] = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal().id
        invoice_vals['invoice_line_ids'] = line_ids
        # Create an empty account.move object
        self.env['account.move'].create(invoice_vals)
        # print('FUCK: {}'.format(self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal().id))
        
        return super().action_sold()
