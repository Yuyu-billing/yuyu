import logging
import traceback
from typing import Dict, Iterable

from django.core.management import BaseCommand
from django.utils import timezone

from core.component import component, labels
from core.models import Invoice, InvoiceComponentMixin, Balance
from core.notification import send_notification_from_template, send_notification
from core.utils.dynamic_setting import get_dynamic_setting, BILLING_ENABLED, INVOICE_TAX, COMPANY_NAME, \
    COMPANY_ADDRESS, INVOICE_AUTO_DEDUCT_BALANCE
from yuyu import settings

LOG = logging.getLogger("yuyu")


class Command(BaseCommand):
    help = 'Yuyu New Invoice'

    def handle(self, *args, **options):
        LOG.info("Processing Invoice")
        try:
            if not get_dynamic_setting(BILLING_ENABLED):
                LOG.info("Billing not activated")
                return

            self.close_date = timezone.now()
            self.tax_pertentage = get_dynamic_setting(INVOICE_TAX)

            active_invoices = Invoice.objects.filter(state=Invoice.InvoiceState.IN_PROGRESS).all()
            for active_invoice in active_invoices:
                self.close_active_invoice(active_invoice)
        except Exception:
            LOG.exception("Error Processing Invoice")
            send_notification(
                project=None,
                title='[Error] Error when processing Invoice',
                short_description=f'There is an error when Processing Invoice',
                content=f'There is an error when handling Processing Invoice \n {traceback.format_exc()}',
            )
        
        LOG.info("Processing Invoice Done")

    def close_active_invoice(self, active_invoice: Invoice):
        active_components_map: Dict[str, Iterable[InvoiceComponentMixin]] = {}

        for label in labels.INVOICE_COMPONENT_LABELS:
            active_components_map[label] = getattr(active_invoice, label).filter(end_date=None).all()

            # Close Invoice Component
            for active_component in active_components_map[label]:
                active_component.close(self.close_date)

        # Finish current invoice
        active_invoice.close(self.close_date, self.tax_pertentage)

        # Creating new Invoice
        new_invoice = Invoice.objects.create(
            project=active_invoice.project,
            start_date=self.close_date,
            state=Invoice.InvoiceState.IN_PROGRESS
        )
        new_invoice.save()

        # Cloning active component to continue in next invoice
        for label, active_components in active_components_map.items():
            handler = component.INVOICE_HANDLER[label]
            for active_component in active_components:
                handler.roll(active_component, self.close_date, update_payload={
                    "invoice": new_invoice
                }, fallback_price=True)

        # Auto Finish Deduct Balance
        if get_dynamic_setting(INVOICE_AUTO_DEDUCT_BALANCE):
            balance = Balance.get_balance_for_project(active_invoice.project)

            deduct_transaction = f"Automatic balance deduction for invoice #{active_invoice.id}"
            if balance.top_down_if_amount_is_good(active_invoice.total, deduct_transaction):
                # Auto finish invoice
                active_invoice.finish()
                send_notification_from_template(
                    project=active_invoice.project,
                    title=settings.EMAIL_TAG + f' Invoice #{active_invoice.id} has been Paid from Balance',
                    short_description=f'Invoice is paid with total of {active_invoice.total}',
                    template='invoice.html',
                    context={
                        'invoice': active_invoice,
                        'company_name': get_dynamic_setting(COMPANY_NAME),
                        'address': get_dynamic_setting(COMPANY_ADDRESS),
                    }
                )
                return

        # Not Auto Finish
        send_notification_from_template(
            project=active_invoice.project,
            title=settings.EMAIL_TAG + f' Your Invoice #{active_invoice.id} is Ready',
            short_description=f'Invoice is ready with total of {active_invoice.total}',
            template='invoice.html',
            context={
                'invoice': active_invoice,
                'company_name': get_dynamic_setting(COMPANY_NAME),
                'address': get_dynamic_setting(COMPANY_ADDRESS),
            }
        )
