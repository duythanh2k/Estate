# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color')

    # SQL CONSTRAINTS
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)',
         'The tag name must be unique!')
    ]
