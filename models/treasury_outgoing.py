# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.num2fawords import ordinal_words, words
from odoo.tools import jadatetime as jd


class TreasuryOutgoing(models.Model):
    _name = "treasury.outgoing"
    _inherit = 'treasury.in_out_going'
    _description = "Treasury Outgoing"

    date_issue = fields.Datetime(string='Issue Date')
    due_date_text = fields.Char(string='Due Date Text', compute='_compute_due_date_text')

    reason = fields.Char(string='Reason')
    beneficiary = fields.Many2one('res.partner', string='Beneficiary')
    description = fields.Char(string='Description', compute='_compute_description')
    checkbook_id = fields.Many2one('treasury.checkbook', string='Checkbook', readonly=True)
    date_delivery = fields.Date(string='Delivery Date')

    select_type = fields.Selection([
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        compute='_compute_select_type',
        inverse='_set_select_type',
        store=False,
        required=True)

    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Draft'),
        ('printed', 'Printed'),
        ('delivered', 'Delivered'),
        ('cleaned', 'Cleaned'),
        ('bounced', 'Bounced'),
        ('canceled', 'Canceled')],
        default='new', readonly=True,
        track_visibility='onchange')



    @api.multi
    def _compute_due_date_text(self):
        for doc in self:
            doc.due_date_text = ordinal_words(jd.date.fromgregorian(date=self.due_date).day) \
                                + jd.date.fromgregorian(date=self.due_date).aslocale('fa_IR').strftime(' %B ') \
                                + words(jd.date.fromgregorian(date=self.due_date).year)

    @api.multi
    def _compute_amount_text(self):
        for doc in self:
            doc.amount_text = words(self.amount)

    @api.multi
    def _compute_description(self):
        for doc in self:
            doc.description = '{} {} {}'.format(self.beneficiary.name, _('for'), self.reason)

    @api.multi
    @api.depends('type')
    def _compute_select_type(self):
        for doc in self:
            doc.select_type = doc.type if doc.type != 'check' else False

    @api.onchange('select_type')
    def _set_select_type(self):
        for doc in self:
            doc.type = doc.select_type

    @api.multi
    def print_check(self):
        self.state = 'printed'
        return self.env.ref('treasury.action_print_check').report_action(self, config=False)

    @api.multi
    def deliver_check(self):
        self.state = 'delivered'
