# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Property type'
    _order = 'sequence, name'
    
    name = fields.Char(string='Type Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1, help="Used to order types.")
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Property Offers")
    offer_count = fields.Integer(compute="_offer_count", string="Offers")
    
    
#   SQL Constraints 
    _sql_constraints = [
        ("unique_type_name", "UNIQUE(name)",
         "The type must be unique.")
    ]
    
    
#    Computed fields
    @api.depends("offer_ids")
    def _offer_count(self):
        for record in self:
            if record.offer_ids:
                record.offer_count = len(record.mapped("offer_ids"))
            else:
                record.offer_count = 0
    