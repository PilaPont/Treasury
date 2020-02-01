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
                         'This name is duplicate!')]  # todo: Make sure it works!

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
    def _onchange_guaranty_type(self):
        if self.type in ['promissory_note', 'bank_guaranty']:
            self.guaranty = True
        if self.type == 'check':
            self.type = 'promissory_note'
            raise exceptions.UserError('You can not create a check from here. Please create a checkbook!')

    # @api.model
    # def create(self, vals):
    #     if self.type == 'check' and not self.checkbook_id:
    #         raise exceptions.UserError('You can not create a check from here. Please create a checkbook!')
    #     else:
    #         return super(TreasuryOutgoing, self).create(vals)

    @api.multi
    def print_check(self):
        self.state = 'printed'
        return self.env.ref('treasury.action_print_check').report_action(self, config=False)

    @api.multi
    def deliver_check(self):
        self.state = 'delivered'
