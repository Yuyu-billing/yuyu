from datetime import timezone
import logging
from core.feature.unpaid_invoice_handle.actions import UnpainInvoiceAction
from core.feature.unpaid_invoice_handle.command import UnpaidInvoiceHandlerCommand
from core.models import Invoice
from yuyu import settings

LOG = logging.getLogger("yuyu")

class UnpaidInvoiceEventHandler:
    filter_action = [
        UnpainInvoiceAction.STOP_INSTANCE,
        UnpainInvoiceAction.SUSPEND_INSTANCE,
        UnpainInvoiceAction.PAUSE_INSTANCE,
        UnpainInvoiceAction.DELETE_INSTANCE,
    ]

    def filter_event_project_id(event_type, raw_payload):
        if event_type == 'floatingip.create.end':
            return raw_payload['floatingip']['tenant_id']
        if event_type == 'image.activate':
            return raw_payload['owner']
        if event_type == 'compute.instance.update':
            return raw_payload['tenant_id']
        if event_type == 'router.create.end':
            return raw_payload['router']['tenant_id']
        if event_type == 'router.update.end':
            return raw_payload['router']['tenant_id']
        if event_type == 'snapshot.create.end':
            return raw_payload['tenant_id']
        if event_type == 'volume.create.end':
            return raw_payload['tenant_id']

        return None
    
    def handle(self, event_type, raw_payload):
        try:
            LOG.exception("Processing Unpaid Invoice Event")
            schedule_config = settings.UNPAID_INVOICE_HANDLER_CONFIG
            command = UnpaidInvoiceHandlerCommand()
            project_id = self.filter_event_project_id(event_type, raw_payload)
            if project_id:
                # Fetch All Unpaid Invoice
                unpaid_invoice = Invoice.objects.filter(project__tenant_id=project_id, state=Invoice.InvoiceState.UNPAID).first()
                used_config = {}
                used_day = 0

                if unpaid_invoice:
                    # Calculate Days
                    # Find last config that has beed runned in past days
                    date_diff = timezone.now() - unpaid_invoice.end_date
                    past_day = date_diff.days
                    for config in schedule_config:
                        if config['action'] not in self.filter_action:
                            continue

                        if config['day'] <= past_day and config['day'] > used_day:
                            used_day = config['day']
                            used_config = config

                    if used_config:
                        command.run_action(unpaid_invoice, used_config['action'], config)
        except Exception:
            LOG.exception("Failed to process Unpaid Invoice Event")
