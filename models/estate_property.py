from odoo import Command, _, models
from odoo.exceptions import UserError


class InheritedProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        result = super().action_sold()
        for record in self:
            journal = (
                self.env["account.move"]
                .with_context(default_move_type="out_invoice")
                ._get_default_journal()
            )
            if not journal:
                raise UserError(_("define an accounting sales journal for the company %s (%s).") % (self.company_id.name, self.company_id.id))

            values = {
                "partner_id": record.buyer_ids,
                "move_type": "out_invoice",
                "journal_id": journal.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "6% of the selling price",
                            "quantity": 1,
                            "price_unit": record.selling_price * 0.06,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Administrative fees",
                            "quantity": 1,
                            "price_unit": 100,
                        }
                    ),
                ],
            }
            self.env["account.move"].create(values)
        print("DATO:", result)
        return result