# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo import api
import datetime
from _datetime import timedelta


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
    
    @api.depends('validity')
    def _compute_date(self):
        for record in self:
            record.date_deadline = fields.date.today() + datetime.timedelta(days=record.validity)
            
    def _inverse_date(self):
        fmt = '%Y-%m-%d'
        for record in self:
            record.validity = int(str((record.date_deadline - fields.date.today()).days))
    