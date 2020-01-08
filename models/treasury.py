from odoo import api, fields, models, _, exceptions
from odoo.tools.num2fawords import ordinal_words, words
from odoo.tools import jadatetime as jd


class TreasuryCheckbook(models.Model):
    _name = "treasury.checkbook"
    _description = "Treasury Checkbook"

    @api.multi
    @api.depends('check_ids.state')
    def _compute_remained_state(self):
        for check_book in self:
            if all(check.state in ('cleaned', 'canceled') for check in check_book.check_ids):
                check_book.state = 'done'
                check_book.remained = 0
            else:
                check_book.remained = len(check_book.check_ids.filtered(lambda x: x.state in ('draft', 'new')))
                check_book.state = 'open' if check_book.remained else 'finished'

    @api.multi
    @api.depends('journal_id.name', 'first_serial_no', 'count')
    def _compute_display_name(self):
        for check_book in self:
            check_book.display_name = '{}- {} ({})'.format(self.journal_id.name, self.first_serial_no, self.count)

    @api.onchange('select_count')
    def _onchange_select_count(self):
        try:
            self.count = int(self.select_count)
        except Exception as e:
            print(e)

    @api.model
    def create(self, vals):
        check_book = super(TreasuryCheckbook, self).create(vals)
        for n in range(check_book.count):
            self.env['treasury.check'].create({
                'name': '{}/{}'.format(check_book.series_no, int(check_book.first_serial_no) + n),
                'checkbook_id': check_book.id
            })
        return check_book

    @api.model
    def unlink(self):
        for checkbook in self:
            if any(check.state not in ('new', 'draft') for check in checkbook.check_ids):
                raise exceptions.UserError('There is at least one check with state other than new and draft.')
        return super(TreasuryCheckbook, self).unlink()

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type', '=', 'bank')])
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account',
                                      related='journal_id.bank_account_id', readonly=True)
    check_ids = fields.One2many('treasury.check', string='Check', inverse_name='checkbook_id',
                                required=True)
    first_serial_no = fields.Integer(string='First Check Serial No.', required=True)
    series_no = fields.Integer(string='Series No.', required=True)
    select_count = fields.Selection(selection=[
        ('10', '10'),
        ('20', '20'),
        ('50', '50'),
        ('custom_count', 'Custom Count')], string='Select Count')
    count = fields.Integer(string='Count')
    remained = fields.Integer(string='# Remained', compute='_compute_remained_state', store=True)
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('finished', 'Finished'),
        ('done', 'Done'),
    ], default='open', compute='_compute_remained_state', store=True)


class TreasuryCheck(models.Model):
    _name = "treasury.check"
    _description = "Treasury Check"

    @api.multi
    def _compute_due_date_text(self):
        for check in self:
            check.date_due_text = ordinal_words(jd.date.fromgregorian(date=self.date_due).day) \
                                  + jd.date.fromgregorian(date=self.date_due).strftime(' %B ') \
                                  + words(jd.date.fromgregorian(date=self.date_due).year)

    @api.multi
    def _compute_description(self):
        for check in self:
            check.description = '{} {} {}'.format(self.beneficiary, _('for'), self.reason)

    @api.multi
    def _compute_amount_text(self):
        for check in self:
            check.amount_text = words(self.amount)

    name = fields.Char(string='Check No.', readonly=True, required=True)
    date_issue = fields.Datetime(string='Issue Date')
    date_due = fields.Date(string='Due Date')
    date_due_text = fields.Char(string='Due Date Text', compute='_compute_due_date_text')
    amount = fields.Monetary(currency_field='currency_id', string='Amount')
    currency_id = fields.Many2one('res.currency', related='checkbook_id.journal_id.currency_id')
    reason = fields.Char(string='Reason')
    beneficiary = fields.Many2one('res.partner', string='Beneficiary')
    description = fields.Char(string='Description', compute='_compute_description')
    checkbook_id = fields.Many2one('treasury.checkbook', string='Checkbook')
    amount_text = fields.Char(string='Amount Text', compute='_compute_amount_text')
    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Draft'),
        ('printed', 'Printed'),
        ('delivered', 'Delivered'),
        ('cleaned', 'Cleaned'),
        ('bounced', 'Bounced'),
        ('canceled', 'Canceled'),
    ], required=True, default='new')
