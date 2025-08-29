from odoo import api, fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "analytic.mixin"]

    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    @api.depends("invoice_line_ids.analytic_distribution")
    def _compute_analytic_distribution(self):
        """If all lines have the same analytic distribution, set it on the order.

        If no lines exist, respect the value given by the user.
        """
        for am in self:
            if am.invoice_line_ids:
                al = am.invoice_line_ids[0].analytic_distribution or False
                for ol in am.invoice_line_ids:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                am.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """When setting the analytic distribution`, apply it to all order lines."""
        for am in self:
            if am.analytic_distribution:
                am.invoice_line_ids.write(
                    {"analytic_distribution": am.analytic_distribution}
                )

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When changing the analytic distribution, apply it to all order lines."""
        if self.analytic_distribution:
            self.invoice_line_ids.update(
                {"analytic_distribution": self.analytic_distribution}
            )
