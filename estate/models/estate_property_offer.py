# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo import api
import datetime
from _datetime import timedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property offer'
    
    price = fields.Float(string='Price')
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        string='Status', copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity = fields.Integer(string='Validity (days)', default=7)
    date_deadline = fields.Date(compute='_compute_date', 
                                inverse='_inverse_date', string='Deadline', store=True)
    
    
#    SQL Constraints
    _sql_constraints = [
        ("offer_price_strictly_positive", "CHECK(price > 0)",
         "The offer price must be strictly positive.")    
    ]
    
    
#    Computed methods
    @api.depends('validity')
    def _compute_date(self):
        for record in self:
            record.date_deadline = fields.date.today() + datetime.timedelta(days=record.validity)
            
    def _inverse_date(self):
        fmt = '%Y-%m-%d'
        for record in self:
            record.validity = int(str((record.date_deadline - fields.date.today()).days))
            
#    Action methods
    def action_accept(self):
        if self.property_id.buyer:
            raise UserError('There was an offer of {} has accepted.'.format(self.property_id.buyer.name))
        for record in self:
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.buyer = record.partner_id
            record.property_id.selling_price = record.price
        return True
    
    def action_refuse(self):
        for record in self:
            # if record.status == 'accepted':
            #     raise UserError('Offer has been accepted! Cannot refuse this offer.')
            # else:
            record.status = 'refused'
            if record.property_id.buyer == record.partner_id:
                record.property_id.buyer = False
                record.property_id.state = 'offer_received'
        return True
    
    
#    Define Inheritance
#    PYTHON
    @api.model
    def create(self, vals):
        current_property = self.env['estate.property'].browse(vals['property_id']);
        if vals['price'] < current_property.best_price:
            raise UserError("The offer must be higher than {}.".format(current_property.best_price))
        else:
            current_property.state = "offer_received"
            return super().create(vals)
    