# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _


class TreasuryEntry(models.AbstractModel):
    _name = "treasury.entry"
    _inherit = 'mail.thread'
    _description = "Treasury Entry"

    name = fields.Char(string='Internal Number ', copy=False, readonly=True, index=True)
    number = fields.Char(string='Number', required=True)
    due_date = fields.Date(string='Due Date')
    amount = fields.Monetary(currency_field='currency_id', string='Amount')
    currency_id = fields.Many2one('res.currency', string='currency',
                                  default=lambda self: self.env['res.company']._company_default_get().currency_id)
    guaranty = fields.Boolean(string='Guaranty')
    company_id = fields.Many2one(comodel_name='res.company', string='company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    security_type_id = fields.Many2one(comodel_name='treasury.security_type', string='Security type')
    expected_return_by = fields.Date(string='Expected return by')
    reason = fields.Char(string='Reason')
    due_state = fields.Selection(selection=[
        ('undue', 'Undue'),
        ('due', 'Due'),
        ('overdue', 'overdue')],
        compute='_compute_due',
        search='_search_due')
    type = fields.Selection(selection=[
        ('check', 'Check'),
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        required=True)
    _sql_constraints = [('unique_type_name', 'unique(number, type)',
                         'This name is duplicate!')]

    @api.multi
    @api.depends('due_date')
    def _compute_due(self):
        for doc in self:
            if not doc.due_date:
                doc.due_state = 'undue'
            else:
                current_date = datetime.date.today()
                if doc.due_date < current_date:
                    doc.due_state = 'overdue'
                elif doc.due_date == current_date:
                    doc.due_state = 'due'
                else:
                    doc.due_state = 'undue'

    @api.onchange('type')
    def _onchange_type(self):
        self.security_type_id = None
        self.guaranty = False

        if self.type in ['bank_guaranty', 'promissory_note']:
            self.guaranty = True
        return {'domain': {'security_type_id': [('type', '=', self.type)]}}

    def _search_due(self, operator, value):
        current_date = datetime.date.today()
        if operator == '=':
            if value == 'overdue':
                return [('due_date', '<', current_date)]
            elif value == 'due':
                return [('due_date', '=', current_date)]
            elif value == 'undue':
                return [('due_date', '>', current_date)]
            else:
                return [('due_date', '=', False)]
        elif operator == '!=':
            if value == 'overdue':
                return [('due_date', '>=', current_date)]
            elif value == 'due':
                return ['|', ('due_date', '<', current_date), ('due_date', '>', current_date)]
            elif value == 'undue':
                return [('due_date', '<=', current_date)]
            else:
                return [('due_date', '=', False)]
        else:
            raise NotImplementedError

    @api.model
    def create(self, vals):
        if not vals.get('guaranty') and vals['type'] in ['bank_guaranty', 'promissory_note']:
            vals['guaranty'] = True

        vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super().create(vals)
