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
            'consignee_id': 1,
            'issued_by': 'Issuer'
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
            'consignee_id': 1,
            'issued_by': 'Issuer'
        })

        self.check_test2 = self.env['treasury.incoming'].create({
            'number': 'check_test2',
            'type': 'check',
            'received_date': date(2020, 6, 1),
            'security_type_id': self.env['treasury.security_type'].search(
                [('type', '=', 'check')], limit=1).id,
            'amount': 20000,
            'consignee_id': 1,
            'issued_by': 'Issuer'
        })

    def test_confirm_account_move(self):
        """
        Check confirm action
        """

        self.promissory_test.action_confirm()
        self.assertEqual(self.promissory_test.state, 'undeposited')
        self.assertEqual(len(self.promissory_test.account_move_line_ids), 0)

        self.check_test1.action_confirm()
        self.assertEqual(self.check_test1.state, 'undeposited')
        self.assertEqual(len(self.check_test1.account_move_line_ids), 0)

        self.check_test2.action_confirm()
        self.assertEqual(self.check_test1.state, 'undeposited')
        self.assertEqual(len(self.check_test2.account_move_line_ids), 2)
        self.assertEqual(self.check_test2.account_move_line_ids[0].move_id, self.check_test2.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test2.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test2.account_move_line_ids))

    def test_in_bank_account_move(self):
        """
        Check in_bank action
        """

        self.promissory_test.action_in_bank()
        self.assertEqual(self.promissory_test.state, 'in_bank')
        self.assertEqual(len(self.promissory_test.account_move_line_ids), 2)
        self.assertEqual(self.promissory_test.account_move_line_ids[0].move_id, self.promissory_test.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.promissory_test.account_move_line_ids),
                         sum(ml.credit for ml in self.promissory_test.account_move_line_ids))

        self.check_test1.action_in_bank()
        self.assertEqual(self.check_test1.state, 'in_bank')
        self.assertEqual(len(self.check_test1.account_move_line_ids), 2)
        self.assertEqual(self.check_test1.account_move_line_ids[0].move_id, self.check_test1.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test1.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test1.account_move_line_ids))

        self.check_test2.action_in_bank()
        self.assertEqual(self.check_test1.state, 'in_bank')
        self.assertEqual(len(self.check_test2.account_move_line_ids), 2)
        self.assertEqual(self.check_test2.account_move_line_ids[0].move_id, self.check_test2.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test2.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test2.account_move_line_ids))

    def test_bounce_account_move(self):
        """
        Check bounce action
        """

        self.promissory_test.action_bounce()
        self.assertEqual(self.promissory_test.state, 'bounced')
        self.assertEqual(len(self.promissory_test.account_move_line_ids), 2)
        self.assertEqual(self.promissory_test.account_move_line_ids[0].move_id, self.promissory_test.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.promissory_test.account_move_line_ids),
                         sum(ml.credit for ml in self.promissory_test.account_move_line_ids))

        self.check_test1.action_bounce()
        self.assertEqual(self.check_test1.state, 'bounced')
        self.assertEqual(len(self.check_test1.account_move_line_ids), 2)
        self.assertEqual(self.check_test1.account_move_line_ids[0].move_id, self.check_test1.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test1.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test1.account_move_line_ids))

        self.check_test2.action_bounce()
        self.assertEqual(self.check_test1.state, 'bounced')
        self.assertEqual(len(self.check_test2.account_move_line_ids), 2)
        self.assertEqual(self.check_test2.account_move_line_ids[0].move_id, self.check_test2.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test2.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test2.account_move_line_ids))

    def test_sue_account_move(self):
        """
        Check sue action
        """

        self.promissory_test.action_sue()
        self.assertEqual(self.promissory_test.state, 'sued')
        self.assertEqual(len(self.promissory_test.account_move_line_ids), 0)

        self.check_test1.action_sue()
        self.assertEqual(self.check_test1.state, 'sued')
        self.assertEqual(len(self.check_test1.account_move_line_ids), 0)

        self.check_test2.action_sue()
        self.assertEqual(self.check_test1.state, 'sued')
        self.assertEqual(len(self.check_test2.account_move_line_ids), 2)
        self.assertEqual(self.check_test2.account_move_line_ids[0].move_id, self.check_test2.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test2.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test2.account_move_line_ids))

    def test_return_account_move(self):
        """
        Check sue action
        """

        self.promissory_test.action_return()
        self.assertEqual(self.promissory_test.state, 'returned')
        self.assertEqual(len(self.promissory_test.account_move_line_ids), 0)

        self.check_test1.action_return()
        self.assertEqual(self.check_test1.state, 'returned')
        self.assertEqual(len(self.check_test1.account_move_line_ids), 0)

        self.check_test2.action_return()
        self.assertEqual(self.check_test1.state, 'returned')
        self.assertEqual(len(self.check_test2.account_move_line_ids), 2)
        self.assertEqual(self.check_test2.account_move_line_ids[0].move_id, self.check_test2.account_move_ids)
        self.assertEqual(sum(ml.debit for ml in self.check_test2.account_move_line_ids),
                         sum(ml.credit for ml in self.check_test2.account_move_line_ids))
