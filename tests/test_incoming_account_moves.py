from odoo.tests.common import TransactionCase, tagged
from datetime import date


@tagged('-at_install', 'post_install')
class TestIncomingAccountMove(TransactionCase):
    def setUp(self):
        super(TestIncomingAccountMove, self).setUp()

        self.promissory_test = self.env['treasury.incoming'].create({
            'number': 'promissory_test',
            'type': 'promissory_note',
            'expected_return_by': date(2020, 6, 1),
            'received_date': date(2020, 6, 1),
            'security_type_id': self.env['treasury.security_type'].search(
                [('type', '=', 'promissory_note')], limit=1).id,
            'amount': 50000,
            'consignee_id': 1
        })

        self.check_test1 = self.env['treasury.incoming'].create({
            'number': 'check_test1',
            'type': 'check',
            'guaranty': True,
            'expected_return_by': date(2020, 6, 1),
            'received_date': date(2020, 6, 1),
            'security_type_id': self.env['treasury.security_type'].search(
                [('type', '=', 'check')], limit=1).id,
            'amount': 10000,
            'consignee_id': 1
        })

        self.check_test2 = self.env['treasury.incoming'].create({
            'number': 'check_test2',
            'type': 'check',
            'received_date': date(2020, 6, 1),
            'security_type_id': self.env['treasury.security_type'].search(
                [('type', '=', 'check')], limit=1).id,
            'amount': 20000,
            'consignee_id': 1
        })

        self.check_test3 = self.env['treasury.incoming'].create({
            'number': 'check_test3',
            'type': 'check',
            'received_date': date(2020, 6, 1),
            'security_type_id': self.env['treasury.security_type'].search(
                [('type', '=', 'check')], limit=1).id,
            'amount': 30000,
            'consignee_id': 1
        })

    def test_confirm_account_move(self):
        """

        """
        self.promissory_test.action_confirm()
        self.assertEqual(len(self.env['account.move.line'].search(
            [('name', '=', self.promissory_test.name)])), 0)

        self.check_test1.action_confirm()
        self.assertEqual(len(self.env['account.move.line'].search(
            [('name', '=', self.check_test1.name)])), 0)

        self.check_test2.action_confirm()
        check_test2_debit_line = self.env['account.move.line'].search(
            [('name', '=', self.check_test2.name), ('debit', '=', self.check_test2.amount),
             ('account_id', '=', self.check_test2.company_id.incoming_securities_account_id.id)])
        check_test2_credit_line = self.env['account.move.line'].search(
            [('name', '=', self.check_test2.name), ('credit', '=', self.check_test2.amount),
             ('account_id', '=', self.check_test2.consignee_id.property_account_receivable_id.id)])
        self.assertEqual(len(check_test2_debit_line), 1)
        self.assertEqual(len(check_test2_credit_line), 1)
        check_test2_account_move = self.env['account.move'].search(
            [('line_ids', 'in', [check_test2_debit_line.id, check_test2_credit_line.id])])

        self.check_test3.action_confirm()
        check_test3_debit_line = self.env['account.move.line'].search(
            [('name', '=', self.check_test3.name), ('debit', '=', self.check_test3.amount),
             ('account_id', '=', self.check_test3.company_id.incoming_securities_account_id.id)])
        check_test3_credit_line = self.env['account.move.line'].search(
            [('name', '=', self.check_test3.name), ('credit', '=', self.check_test3.amount),
             ('account_id', '=', self.check_test3.consignee_id.property_account_receivable_id.id)])
        self.assertEqual(len(check_test3_debit_line), 1)
        self.assertEqual(len(check_test3_credit_line), 1)
