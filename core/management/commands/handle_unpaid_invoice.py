import logging
import traceback

import openstack
from django.core.management import BaseCommand
from django.utils import timezone

from core.models import Invoice
from core.notification import send_notification
from core.utils.dynamic_setting import get_dynamic_setting, BILLING_ENABLED
from yuyu import settings

LOG = logging.getLogger("yuyu_unpaid_invoice_handler")


class Command(BaseCommand):
    help = 'Yuyu Unpaid Invoice Handler'

    def handle(self, *args, **options):
        print("Processing Unpaid Invoice")
        # Initialize connection
        if not get_dynamic_setting(BILLING_ENABLED):
            return

        schedule_config = settings.UNPAID_INVOICE_HANDLER_CONFIG
        expired_unpaid_invoices = Invoice.objects.filter(state=Invoice.InvoiceState.UNPAID).all()
        for invoice in expired_unpaid_invoices:
            date_diff = timezone.now() - invoice.end_date
            past_day = date_diff.days
            for config in schedule_config:
                if config['day'] == past_day:
                    try:
                        if config['action'] == 'send_message':
                            self._send_message(invoice, config)

                        if config['action'] == 'stop_instance':
                            self._stop_component(invoice)

                        if config['action'] == 'delete_instance':
                            self._delete_component(invoice)
                    except Exception:
                        send_notification(
                            project=None,
                            title='[Error] Error when processing unpaid invoice',
                            short_description=f'There is an error when processing unpaid invoice',
                            content=f'There is an error when handling unpaid invoice \n {traceback.format_exc()}',
                        )

        print("Processing Done")

    def _stop_component(self, invoice: Invoice):
        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)

        # Stop Instance
        for server in conn.compute.servers(project_id=invoice.project.tenant_id):
            conn.compute.stop_server(server)

    def _delete_component(self, invoice: Invoice):
        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)

        # Delete Instance
        for server in conn.compute.servers(project_id=invoice.project.tenant_id):
            conn.compute.delete_server(server)

        # Delete Image
        for image in conn.compute.images(project_id=invoice.project.tenant_id):
            conn.compute.delete_image(image)

        # Delete Floating Ips
        for ip in conn.network.ips(project_id=invoice.project.tenant_id):
            conn.network.delete_ip(ip)

        # Delete Router
        for route in conn.network.routers(project_id=invoice.project.tenant_id):
            conn.network.delete_router(route)

        # Delete Volume
        for volume in conn.block_storage.volumes(project_id=invoice.project.tenant_id):
            conn.block_storage.delete_volume(volume)

        # Delete Snapshot
        for snapshot in conn.block_storage.snapshots(project_id=invoice.project.tenant_id):
            conn.block_storage.delete_snapshot(snapshot)

    def _send_message(self, invoice: Invoice, message_config):
        print('Sending Message')
        send_notification(
            project=invoice.project,
            title=message_config['message_title'],
            short_description=message_config['message_short_description'],
            content=message_config['message_content'],
        )
