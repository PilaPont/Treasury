from odoo import api, fields, models, _
from odoo.addons.treasury.tools.num2fawords import ordinal_words, words
from odoo.addons.treasury.tools import jadatetime as jd


class TreasuryOutgoing(models.Model):
    _name = "treasury.outgoing"
    _inherit = 'treasury.entry'
    _description = "Treasury Outgoing"

    date_issue = fields.Datetime(string='Issue Date')
    due_date_text = fields.Char(string='Due Date Text', compute='_compute_due_date_text')
    amount_text = fields.Char(string='Amount Text', compute='_compute_amount_text')
    beneficiary_id = fields.Many2one(comodel_name='res.partner', string='Beneficiary')
    description = fields.Char(string='Description', compute='_compute_description')
    checkbook_id = fields.Many2one(comodel_name='treasury.checkbook', string='Checkbook', readonly=True)
    date_delivery = fields.Date(string='Delivery Date')
    account_move_line_ids = fields.One2many(comodel_name='account.move.line', inverse_name='treasury_outgoing_id',
                                            string='Journal items', readonly=True)
    account_move_ids = fields.One2many(comodel_name='account.move', string='Journal entries',
                                       compute='_compute_account_moves')
    display_name = fields.Char(compute='_compute_display_name', store=True)
    select_type = fields.Selection(selection=[
        ('promissory_note', 'Promissory note'),
        ('bond', 'Bond'),
        ('lc', 'LC'),
        ('bank_guaranty', 'Bank guaranty')],
        compute='_compute_select_type',
        inverse='_set_select_type',
        store=False,
        required=True)
    state = fields.Selection(selection=[
        ('new', 'New'),
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('delivered', 'Delivered'),
        ('cashed', 'Cashed'),
        ('bounced', 'Bounced'),
        ('canceled', 'Canceled')],
        default='new', readonly=True,
        tracking=True)

    def name_get(self):
        return '{}_{}'.format(self.checkbook_id.journal_id.name, self.number)

    def _compute_due_date_text(self):
        for doc in self:
            doc.due_date_text = ordinal_words(jd.date.fromgregorian(date=self.due_date).day) \
                                + jd.date.fromgregorian(date=self.due_date).aslocale('fa_IR').strftime(' %B ') \
                                + words(jd.date.fromgregorian(date=self.due_date).year)

    def _compute_amount_text(self):
        for doc in self:
            doc.amount_text = words(self.amount)

    def _compute_description(self):
        for doc in self:
            doc.description = '{} {} {}'.format(self.beneficiary_id.name, _('for'), self.reason)

    @api.depends('type')
    def _compute_select_type(self):
        for doc in self:
            doc.select_type = doc.type if doc.type != 'check' else False

    @api.depends('account_move_line_ids')
    def _compute_account_moves(self):
        for doc in self:
            doc.account_move_ids = doc.mapped('account_move_line_ids.move_id')

    @api.depends('checkbook_id.journal_id.name', 'number')
    def _compute_display_name(self):
        for doc in self:
            doc.display_name = '{} {}'.format(doc.checkbook_id.journal_id.name, doc.number)

    @api.onchange('select_type')
    def _set_select_type(self):
        for doc in self:
            doc.type = doc.select_type

    def action_print(self):
        self.state = 'issued'
        return self.env.ref('treasury.action_print_check').report_action(self, config=False)

    def action_issue(self):
        self.state = 'issued'

    def action_deliver(self):
        self.state = 'delivered'

    def action_cancel(self):
        self.state = 'canceled'

    def action_return(self):
        self.state = 'issued'
