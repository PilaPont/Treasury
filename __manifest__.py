{
    'name': 'Treasury',
    'version': '1.0',
    'category': 'Localization',
    'description': """
    To handle checks and bonds
    """,
    'author': "Maryam Kia",
    'website': "",
    'depends': ['l10n_ir'
                ],
    'data': ['security/treasury_groups.xml',
             'security/ir.model.access.csv',
             'data/account_journal_data.xml',
             'data/ir_sequence_data.xml',
             'data/treasury_security_type_data.xml',
             'report/print_check.xml',
             'report/check_report.xml',
             'views/treasury_checkbook_views.xml',
             'views/treasury_outgoing_views.xml',
             'views/treasury_incoming_views.xml',
             'views/treasury_menus.xml',
             'views/res_config_settings_views.xml',
             'views/res_company_views.xml',
             ],
    'demo': [],
}
