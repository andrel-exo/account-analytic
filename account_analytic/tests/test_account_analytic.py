# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.tests import Form, TransactionCase


class TestAccountAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("analytic.group_analytic_accounting")
        cls.partner = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_9")
        cls.uom = cls.env.ref("uom.product_uom_unit")
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        analytic_account_manual = cls.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution_manual = {str(analytic_account_manual.id): 100}
        cls.analytic_distribution_manual2 = {str(analytic_account_manual.id): 50}

    def add_am_line(self, move, product=None):
        if not product:
            product = self.product
        move.line_ids = [
            Command.create(
                {
                    "product_id": product.id,
                    "account_id": self.partner.with_company(
                        self.env.company
                    ).property_account_receivable_id.id,
                }
            )
        ]

    def test_analytic_distribution_with_create(self):
        """Create an account move (create)
        Set analytic distribution on account
        Check analytic distribution and line is set
        """
        am = self.env["account.move"].create({"partner_id": self.partner.id})

        # Test setting analytic distribution without lines
        am.analytic_distribution = self.analytic_distribution_manual
        self.assertEqual(am.analytic_distribution, self.analytic_distribution_manual)

        # Test setting analytic distribution with a line
        self.add_am_line(am)
        am.analytic_distribution = self.analytic_distribution_manual2
        self.assertEqual(am.analytic_distribution, self.analytic_distribution_manual2)
        self.assertEqual(
            am.line_ids.analytic_distribution, self.analytic_distribution_manual2
        )

        # Test clearing analytic distribution with a line
        am.analytic_distribution = False
        self.assertEqual(
            am.line_ids.analytic_distribution, self.analytic_distribution_manual2
        )

    def test_analytic_distribution_with_form(self):
        """Create a account move (form)
        Set analytic distribution on account
        Check analytic distribution and line is set
        """
        move = Form(
            self.env["account.move"].with_context(default_partner_id=self.partner.id)
        )

        # Test setting analytic distribution without lines
        move.analytic_distribution = self.analytic_distribution_manual
        self.assertEqual(move.analytic_distribution, self.analytic_distribution_manual)

        # Test setting analytic distribution with a line
        move = move.save()
        self.add_am_line(move)
        with Form(move) as am:
            am.analytic_distribution = self.analytic_distribution_manual2
            self.assertEqual(
                am.analytic_distribution, self.analytic_distribution_manual2
            )
            self.assertEqual(
                am.invoice_line_ids._field_value.get_vals(move.invoice_line_ids.id)[
                    "analytic_distribution"
                ],
                self.analytic_distribution_manual2,
            )

            # Test clearing analytic distribution with a line
            am.analytic_distribution = False
            self.assertEqual(
                am.invoice_line_ids._field_value.get_vals(move.invoice_line_ids.id)[
                    "analytic_distribution"
                ],
                self.analytic_distribution_manual2,
            )
