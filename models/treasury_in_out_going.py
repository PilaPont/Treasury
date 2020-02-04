# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TreasuryInOut(models.AbstractModel):
    _name = "treasury.in_out_going"
    _inherit = 'mail.thread'
    _description = "Treasury In&Outgoing"

    name = fields.Char(string='Internal Number ', copy=False, readonly=True, index=True)
    number = fields.Char(string='Number', required=True)
    due_date = fields.Date(string='Due Date')
    amount = fields.Monetary(currency_field='currency_id', string='Amount')
    currency_id = fields.Many2one('res.currency', string='currency_id',
                                  default=lambda self: self.env.ref('base.IRR').id)
    guaranty = fields.Boolean(string='Guaranty')
    company_id = fields.Many2one('res.company', string='company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    security_type_id = fields.Many2one('treasury.security_type', string='Security type')
    expected_return_by = fields.Date(string='Expected return by')
    type = fields.Selection([
        ('check', 'Check'),
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        required=True)
    _sql_constraints = [('unique_type_name', 'unique(number, type)',
                         'This name is duplicate!')]

    @api.onchange('type')
    def _onchange_type(self):
        self.security_type_id = None
        self.guaranty = False

        if self.type in ['bank_guaranty', 'promissory_note']:
            self.guaranty = True
        return {'domain': {'security_type_id': [('type', '=', self.type)]}}

    @api.model
    def create(self, vals):
        if not vals.get('guaranty') and vals['type'] in ['bank_guaranty', 'promissory_note']:
            vals['guaranty'] = True

        vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super().create(vals)
