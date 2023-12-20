import logging
import traceback

import openstack
from django.core.management import BaseCommand
from django.utils import timezone
from core.feature.unpaid_invoice_handle.command import UnpaidInvoiceHandlerCommand

from core.models import Invoice
from core.notification import send_notification
from core.utils.dynamic_setting import get_dynamic_setting, BILLING_ENABLED
from yuyu import settings

LOG = logging.getLogger("yuyu")


class Command(BaseCommand):
    unpaid_invoice_command = UnpaidInvoiceHandlerCommand()
    
    def handle(self, *args, **options):
        self.unpaid_invoice_command.handle()