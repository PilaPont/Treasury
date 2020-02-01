from odoo import api, fields, models, _, exceptions
from odoo.tools.num2fawords import ordinal_words, words
from odoo.tools import jadatetime as jd


class TreasuryOutgoing(models.Model):
    _name = "treasury.outgoing"
    _inherit = 'mail.thread'
    _description = "Treasury Outgoing"

    name = fields.Char(string='Number', required=True)
    date_issue = fields.Datetime(string='Issue Date')
    date_due = fields.Date(string='Due Date')
    date_due_text = fields.Char(string='Due Date Text', compute='_compute_due_date_text')
    amount = fields.Monetary(currency_field='currency_id', string='Amount')
    amount_text = fields.Char(string='Amount Text', compute='_compute_amount_text')
    currency_id = fields.Many2one('res.currency', related='checkbook_id.journal_id.currency_id')
    reason = fields.Char(string='Reason')
    beneficiary = fields.Many2one('res.partner', string='Beneficiary')
    description = fields.Char(string='Description', compute='_compute_description')
    checkbook_id = fields.Many2one('treasury.checkbook', string='Checkbook', readonly=True)
    date_delivery = fields.Date(string='Delivery Date')
    security_type = fields.Many2one('treasury.security_type', string='Security type')
    company_id = fields.Many2one('res.company', string='company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    guaranty = fields.Boolean(string='Guaranty', readonly=True)
    expected_return_by = fields.Date(string='Expected return by')
    type = fields.Selection([
        ('check', 'Check'),
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        required=True)
    select_type = fields.Selection([
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank_guaranty')],
        compute='_compute_display_type',
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

    _sql_constraints = [('unique_type_name', 'unique(name, type)',
                         'This name is duplicate!')]

    @api.multi
    def _compute_due_date_text(self):
        for doc in self:
            doc.date_due_text = ordinal_words(jd.date.fromgregorian(date=self.date_due).day) \
                                  + jd.date.fromgregorian(date=self.date_due).aslocale('fa_IR').strftime(' %B ') \
                                  + words(jd.date.fromgregorian(date=self.date_due).year)

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
    def _compute_display_type(self):
        for doc in self:
            doc.select_type = doc.type if doc.type != 'check' else False

    @api.onchange('select_type')
    def _set_select_type(self):
        for doc in self:
            doc.type = doc.select_type

    @api.onchange('type')
    def _onchange_type(self):
        self.security_type = None
        self.guaranty = False
        if self.type in ['bank_guaranty', 'promissory_note']:
            self.guaranty = True
        return {'domain': {'security_type': [('type', '=', self.type)]}}


    @api.multi
    def print_check(self):
        self.state = 'printed'
        return self.env.ref('treasury.action_print_check').report_action(self, config=False)

    @api.multi
    def deliver_check(self):
        self.state = 'delivered'
