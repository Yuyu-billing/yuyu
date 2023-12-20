import logging
import traceback

import openstack
from django.utils import timezone
from core.feature.unpaid_invoice_handle.actions import UnpainInvoiceAction

from core.models import Invoice
from core.notification import send_notification
from core.utils.date_utils import current_localtime
from core.utils.dynamic_setting import get_dynamic_setting, BILLING_ENABLED
from yuyu import settings


LOG = logging.getLogger("yuyu")

class UnpaidInvoiceHandlerCommand:
    def handle(self):
        LOG.info("Processing Unpaid Invoice")

        # Initialize connection
        if not get_dynamic_setting(BILLING_ENABLED):
            return
        
        if not hasattr(settings, 'UNPAID_INVOICE_HANDLER_CONFIG'):
            LOG.exception("Missing UNPAID_INVOICE_HANDLER_CONFIG in settings")
            return

        expired_unpaid_invoices = Invoice.objects.filter(state=Invoice.InvoiceState.UNPAID).all()
        for invoice in expired_unpaid_invoices:
            self.run_action_on_config(invoice)
                
        LOG.info("Processing Unpaid Invoice Done")
    
    def run_action_on_config(self, invoice):
        schedule_config = settings.UNPAID_INVOICE_HANDLER_CONFIG
        date_diff = current_localtime() - invoice.end_date
        past_day = date_diff.days
        LOG.info(f"Processing Unpaid Invoice {invoice.id} with past day {past_day}")
        for config in schedule_config:
            if config['day'] == past_day:
                LOG.info('Running action')
                self.run_action(invoice, config['action'], config)

    def run_action(self, invoice, action, config=None):
        LOG.info(f"Running action {action} with config {config}")
        try:
            if action == UnpainInvoiceAction.SEND_MESSAGE.value:
                self._send_message(invoice, config)

            if action == UnpainInvoiceAction.STOP_INSTANCE.value:
                self._stop_component(invoice)

            if action == UnpainInvoiceAction.SUSPEND_INSTANCE.value:
                self._stop_component(invoice)

            if action == UnpainInvoiceAction.PAUSE_INSTANCE.value:
                self._stop_component(invoice)

            if action == UnpainInvoiceAction.DELETE_INSTANCE.value:
                self._delete_component(invoice)
        except Exception:
            LOG.exception("Failed to process Unpaid Invoice")
            send_notification(
                project=None,
                title='[Error] Error when processing unpaid invoice',
                short_description=f'There is an error when processing unpaid invoice',
                content=f'There is an error when handling unpaid invoice \n {traceback.format_exc()}',
            )
    
    def _stop_component(self, invoice: Invoice):
        LOG.info("Stopping Component")
        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)

        # Stop Instance
        for server in conn.compute.servers(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Stopping server {server.id}")
            conn.compute.stop_server(server)

    def _suspend_component(self, invoice: Invoice):
        LOG.info("Suspending Component")
        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)

        # Suspend Instance
        for server in conn.compute.servers(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Suspending server {server.id}")
            
            conn.compute.suspend_server(server)

    def _pause_component(self, invoice: Invoice):
        LOG.info("Pausing Component")
        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)

        # Pause Instance
        for server in conn.compute.servers(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Pausing server {server.id}")
            
            conn.compute.pause_server(server)

    def _delete_component(self, invoice: Invoice):
        LOG.info("Deleting Component")
        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)

        # Delete Instance
        for server in conn.compute.servers(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Deleting server {server.id}")
            
            conn.compute.delete_server(server)

        # Delete Image
        for image in conn.compute.images(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Deleting image {image.id}")
            conn.compute.delete_image(image)

        # Delete Floating Ips
        for ip in conn.network.ips(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Deleting ip {ip.id}")
            
            conn.network.delete_ip(ip)

        # Delete Router
        for route in conn.network.routers(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Deleting route {route.id}")
            
            conn.network.delete_router(route)

        # Delete Volume
        for volume in conn.block_storage.volumes(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Deleting volume {volume.id}")
            
            conn.block_storage.delete_volume(volume)

        # Delete Snapshot
        for snapshot in conn.block_storage.snapshots(all_projects=True, project_id=invoice.project.tenant_id):
            LOG.info(f"Deleting snapshot {snapshot.id}")
            
            conn.block_storage.delete_snapshot(snapshot)

    def _send_message(self, invoice: Invoice, message_config):
        LOG.info("Sending Message")
        send_notification(
            project=invoice.project,
            title=message_config['message_title'],
            short_description=message_config['message_short_description'],
            content=message_config['message_content'],
        )