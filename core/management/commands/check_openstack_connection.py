import logging

import openstack
from django.core.management import BaseCommand

from yuyu import settings

LOG = logging.getLogger("check_openstack_connection")


class Command(BaseCommand):
    help = 'Yuyu Check Openstack Connection'

    def handle(self, *args, **options):
        print("Checking Openstack Connection")
        print("Will try to list instance on the project that configured in `clouds.yaml`")

        conn = openstack.connect(cloud=settings.CLOUD_CONFIG_NAME)
        for server in conn.compute.servers(all_projects=True):
            print(server.name)
