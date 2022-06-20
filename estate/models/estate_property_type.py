# -*- coding: utf-8 -*-

from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Property type'
    
    name = fields.Char(string='Type Name', required=True)
    