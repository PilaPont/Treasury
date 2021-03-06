from odoo import fields, models


class TreasurySecurityType(models.Model):
    _name = "treasury.security_type"
    _description = "Security Type"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='active', default=True)
    type = fields.Selection([
        ('check', 'check'),
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        required=True)
