from odoo import fields, models


class TreasurySecurityType(models.Model):
    _name = "treasury.security_type"
    _description = "National Bank security Type"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='active', default=True)
    type = fields.Selection([
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        required=True)
