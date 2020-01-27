from odoo import api, fields, models, _
from odoo.tools.num2fawords import ordinal_words, words
from odoo.tools import jadatetime as jd


class TreasuryCheck(models.Model):
    _name = "treasury.outgoing"
    _inherit = 'mail.thread'
    _description = "Treasury Outgoing"

    name = fields.Char(string='Number', readonly=True, required=True)
    date_issue = fields.Datetime(string='Issue Date')
    date_due = fields.Date(string='Due Date')
    date_due_text = fields.Char(string='Due Date Text', compute='_compute_due_date_text')
    amount = fields.Monetary(currency_field='currency_id', string='Amount')
    amount_text = fields.Char(string='Amount Text', compute='_compute_amount_text')
    currency_id = fields.Many2one('res.currency', related='checkbook_id.journal_id.currency_id')
    reason = fields.Char(string='Reason')
    beneficiary = fields.Many2one('res.partner', string='Beneficiary')
    description = fields.Char(string='Description', compute='_compute_description')
    checkbook_id = fields.Many2one('treasury.checkbook', string='Checkbook')
    date_delivery = fields.Date(string='Delivery Date')
    company_id = fields.Many2one('res.company', string='company',
                                 related='checkbook_id.company_id', readonly=True)
    type = fields.Selection([
        ('check', 'Check'),
        ('promissory note', 'Promissory note'),
        ('bank_guaranty', 'Bank_guaranty'), ],
        string='type')
    guaranty_type = fields.Selection([
        ('tender guaranty', 'Tender guaranty'),
        ('retention money guaranty', 'Retention money guaranty'),
        ('performance guaranty', 'Performance guaranty'),
        ('payment guaranty', 'Payment guaranty'),
        ('customs guaranty', 'Customs guaranty'),
        ('advanced payment guaranty', 'Advanced payment guaranty'),
        ('other', 'Other')],
        default='new', readonly=True,
        track_visibility='onchange')
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
    purpose = fields.Selection([
        ('normal', 'Normal'),
        ('guaranty', 'Guaranty')],
        required=True, default='normal')

    @api.multi
    def _compute_due_date_text(self):
        for check in self:
            check.date_due_text = ordinal_words(jd.date.fromgregorian(date=self.date_due).day) \
                                  + jd.date.fromgregorian(date=self.date_due).aslocale('fa_IR').strftime(' %B ') \
                                  + words(jd.date.fromgregorian(date=self.date_due).year)

    @api.multi
    def _compute_amount_text(self):
        for check in self:
            check.amount_text = words(self.amount)

    @api.multi
    def _compute_description(self):
        for check in self:
            check.description = '{} {} {}'.format(self.beneficiary.name, _('for'), self.reason)

    @api.onchange('type')
    def _onchange_select_count(self):
        try:
            self.count = int(self.select_count)
        except Exception as e:
            print(e)

    @api.multi
    def print_check(self):
        self.state = 'printed'
        return self.env.ref('treasury.action_print_check').report_action(self, config=False)

    @api.multi
    def deliver_check(self):
        self.state = 'delivered'
