from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'
    price_visible = fields.Boolean(default=False, string='Price Visible')
