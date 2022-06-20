# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo import api


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'my new first database ORM created!'
    
#    Basic Attributes
    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Available From',
                                    # available date from today
                                    default=lambda self: fields.datetime.now())
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (sqm)')
#    The selection list is defined as a list of tuples
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West'),],
        string='Garden Orientation',)
    state = fields.Selection(
        [('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        string='Status',
        required=True,
        copy=False,
        default='new',)
    active = fields.Boolean(string='Active', default=True)
    
#    Relation Attributes
#        Many2one
    property_type_id = fields.Many2one('estate.property.type', string='Property Types')
    buyer = fields.Many2one('res.partner', string="Buyer", copy=False)
    salesperson = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
#        Many2many
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
#        One2many
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Property Offers")
    
#    Computed Attributes
    total_area = fields.Float(compute="_compute_total", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_max", string="Best Offer")

#    Define computed function
    @api.depends('living_area', 'garden_area')
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            
    @api.depends('offer_ids.price')
    def _compute_max(self):
        self.best_price = max(self.mapped('offer_ids.price'))
