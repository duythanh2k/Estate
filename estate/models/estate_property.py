# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
from odoo.tools.float_utils import float_is_zero


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    postCode = fields.Char(string='Postcode')
    date_availability = fields.Date(
        string='Available From',
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=+3)
    )
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')]
    )
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(
        string='Status',
        selection=[('new', 'New'), ('offer received', 'Offer Received'),
                   ('offer accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('canceled', 'Canceled')],
        required=True,
        copy=False,
        default='new'
    )
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area = fields.Integer(compute='_compute_total_area', string='Total Area')
    best_price = fields.Float(compute='_compute_best_offer', string='Best Offer')

    # SQL CONSTRAINTS
    _sql_constraints = [
        ('expected_price_strictly_positive', 'CHECK(expected_price > 0)',
         'The expected price must be strictly positive.')
    ]

    # PYTHON CONSTRAINS
    @api.constrains('selling_price', 'expected_price')
    def _check_lower_90(self):
        for record in self:
            if not record.buyer and \
                    float_is_zero(record.selling_price, precision_digits=2) is True:
                pass
            else:
                if float_compare(record.selling_price,
                                 record.expected_price * 90 / 100,
                                 precision_digits=2) != 1:
                    raise ValidationError(
                        "The selling price must be at least 90% of expected price. "
                        "You must reduce the expected price if you want to accept this offer.")

    # COMPUTE
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    # ONCHANGE
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    # ACTION
    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError('Canceled properties cannot be sold!')
            record.state = 'sold'
        return True

    def action_canceled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold properties cannot be canceled!')
            record.state = 'canceled'
        return True

    # INHERITENCE
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state != 'new' and record.state != 'canceled':
                raise UserError("Only new and canceled properties can be delete.")
