# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo import api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_is_zero

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'my new first database ORM created!'
    _order = 'id desc'
    
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
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer = fields.Many2one('res.partner', string="Buyer", copy=False)
    salesperson = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
#        Many2many
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
#        One2many
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Property Offers")
    
#    Computed Attributes
    total_area = fields.Float(compute="_compute_total", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_max", string="Best Offer")
    
    
#    SQL Constraints
    _sql_constraints = [
        ("expected_price_strictly_positive", "CHECK(expected_price > 0)",
         "The expected price must be strictly positive.")
    ]
    _sql_constraints = [
        ("selling_price_strictly_positive", "CHECK(selling_price > 0)",
         "The selling price must be strictly positive.")
    ]

#    PYTHON Constrains
    @api.constrains('selling_price', 'expected_price')
    def _check_lower_90(self):
        for record in self:
            if float_compare(record.selling_price, 
                             record.expected_price*90/100,
                             precision_digits=2) != 1 and \
                float_is_zero(record.selling_price, precision_digits=2) == False:
                raise ValidationError("The selling price must be at least 90% of expected price. You must reduce the expected price if you want to accept this offer.")


#    Define computed function
    @api.depends('living_area', 'garden_area')
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            
    @api.depends('offer_ids.price')
    def _compute_max(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.mapped('offer_ids.price'))
            else:
                record.best_price = 0
                        
#    Define onchange function
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""
            # return {'warning': {
            #     'title': ("Warning"),
            #     'message': ('This property must have a garden!')}}
            
#    Define some actions
    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise UserError("Canceled properties cannot be sold.")
            elif record.state == "sold":
                raise UserError("Property has already sold.")
            elif record.state != "offer_accepted":
                raise UserError("No offer has accepted. Cannot sold.")
            else:
                record.state = "sold"
        return True
    
    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be canceled.")
            elif record.state == "canceled":
                raise UserError("Property has already canceled.")
            else:
                record.state = "canceled"
        return True
    
    
#    Define Inheritance
#    PYTHON
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state != "new" and record.state != "canceled":
                raise UserError("Only new and canceled properties can be delete.")
            # else:
            #     return super().unlink(record)
            
            
    #    records.filtered(age_greater_30)
    def age_greater_30(self):
        for record in self:
            if record.age > 30:
                return record
    