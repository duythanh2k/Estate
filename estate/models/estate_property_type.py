# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'name'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=1)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer('Offer Count', compute='_compute_offer_count')

    # SQL CONSTRAINTS
    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)',
         'The type name must be unique!')
    ]

    # COMPUTE
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            if record.offer_ids:
                record.offer_count = len(record.mapped('offer_ids'))
            else:
                record.offer_count = 0
