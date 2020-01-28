from odoo import fields, models


class TreasuryBondType(models.Model):
    _name = "treasury.bond_type"
    _description = "National Bank Bond Type"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='active', compute='_compute_active', store=True)
