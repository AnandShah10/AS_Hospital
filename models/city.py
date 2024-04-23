from odoo import api, fields, models, _


class StateCity(models.Model):
    _name = 'state.city'
    _description = 'City'

    name = fields.Char(string='City Name', translate=True)
    country = fields.Many2one('res.country', string='Country')
    state = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country)]")
