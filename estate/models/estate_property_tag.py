# -*- coding: utf-8 -*-

from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Property tag'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')
    
    
#   SQL Constraints 
    _sql_constraints = [
        ("unique_tag_name", "UNIQUE(name)",
         "The tag must be unique.")
    ]
    