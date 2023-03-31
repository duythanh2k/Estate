# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(string='Price')
    status = fields.Selection(string='Status', copy=False,
                              selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one('res.partner', required=True, string='Partner')
    property_id = fields.Many2one('estate.property', required=True, string='Property')
    validity = fields.Integer(string='Validity (days)', default=7)
    date_deadline = fields.Date(string='Deadline', compute='_compute_deadline', inverse='_inverse_deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    # SQL CONSTRAINTS
    _sql_constraints = [
        ('offer_price_strictly_positive', 'CHECK(price > 0)',
         'The offer price must be strictly positive.')
    ]

    # COMPUTE
    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date.date() + relativedelta(days=+record.validity)
            else:
                record.date_deadline = datetime.date.today() + relativedelta(days=+record.validity)

    def _inverse_deadline(self):
        for record in self:
            if record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.validity = (record.date_deadline - record.date.today()).days

    # ------------------------------------------ CRUD Methods -------------------------------------

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)

    # ---------------------------------------- Action Methods -------------------------------------

    def action_accept(self):
        if "accepted" in self.mapped("property_id.offer_ids.status"):
            raise UserError("An offer as already been accepted.")
        self.write(
            {
                "status": "accepted",
            }
        )
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer": self.partner_id.id,
            }
        )

    def action_refuse(self):
        return self.write(
            {
                "status": "refused",
            }
        )
