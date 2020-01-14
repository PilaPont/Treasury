# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _


class TreasuryIncoming(models.Model):
    _name = "treasury.incoming"
    _inherit = 'mail.thread'
    _description = "Treasury Incoming"

    number = fields.Char(string='Number', required=True)
    name = fields.Char(string='Domestic Number ', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    received_date = fields.Date(string='Receive Date', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    currency_id = fields.Many2one('res.currency', string='currency_id',
                                  default=lambda self: self.env.ref('base.IRR').id)
    amount = fields.Monetary(currency_field='currency_id', string='Amount', required=True)
    issuer = fields.Many2one('res.partner', string='Issuer', required=True)
    active = fields.Boolean(string='active', compute='_compute_active', store=True)
    transferred_to = fields.Many2one('res.partner', string='Transferred To')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    due_state = fields.Selection([
        ('undue', 'Undue'),
        ('due', 'Due'),
        ('overdue', 'overdue')],
        compute='_compute_due',
        search='_search_due')

    purpose = fields.Selection([
        ('normal', 'Normal'),
        ('guaranty', 'Guaranty')],
        required=True, default='normal')
    type = fields.Selection([
        ('check', 'Check'),
        ('promissory note', 'Promissory note'),
        ('bond', 'Bond')],
        required=True, default='check')

    state = fields.Selection([
        ('undeposited', 'Undeposited'),
        ('in bank', 'in bank'),
        ('collected', 'Collected'),
        ('transferred', 'Transferred'),
        ('bounced', 'Bounced'),
        ('sued', 'Sued'),
        ('returned', 'returned'),
        ('canceled', 'Canceled')],
        required=True, readonly=True,
        track_visibility='onchange',
        default='undeposited')

    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for check in self:
            check.active = False if check.state in ('collected', 'returned', 'canceled', 'transferred') else True

    @api.multi
    def _compute_due(self):
        current_date = datetime.date.today()
        if self.due_date < current_date:
            self.due_state = 'overdue'
        elif self.due_date == current_date:
            self.due_state = 'due'
        else:
            self.due_state = 'undue'

    @api.multi
    def _search_due(self, operator, value):
        current_date = datetime.date.today()
        if operator == '=':
            if value == 'overdue':
                return self.search([('due_date', '<', current_date)])
            elif value == 'due':
                return self.search([('due_date', '=', current_date)])
            elif value == 'undue':
                return self.search([('due_date', '>', current_date)])
        elif operator == '!=':
            if value == 'overdue':
                return self.search([('due_date', '>=', current_date)])
            elif value == 'due':
                return self.search(['|', ('due_date', '<', current_date), ('due_date', '>', current_date)])
            elif value == 'undue':
                return self.search([('due_date', '<=', current_date)])
        else:
            raise NotImplementedError

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('treasury.incoming')
        return super(TreasuryIncoming, self).create(vals)

    @api.multi
    def set_in_bank(self):
        self.state = 'in bank'

    @api.multi
    def set_bounced(self):
        self.state = 'bounced'

    @api.multi
    def set_sued(self):
        self.state = 'sued'

    @api.multi
    def set_returned(self):
        self.state = 'returned'

    @api.multi
    def set_canceled(self):
        self.state = 'canceled'
