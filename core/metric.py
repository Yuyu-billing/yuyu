import prometheus_client

from core.component.component import INVOICE_COMPONENT_MODEL
from core.component.labels import INVOICE_COMPONENT_LABELS

# Cost Explorer (Summary)
TOTAL_COST_METRIC = prometheus_client.Gauge('total_cost', 'Total Cost of resource for current invoice period', labelnames=['job', 'resources'])

# Detailed Cost
INSTANCE_COST_METRIC = prometheus_client.Gauge('instance_cost', 'Cost of instance usage', labelnames=['job', 'flavor', 'name', 'project_id'])
INSTANCE_USAGE_METRIC = prometheus_client.Gauge('instance_usage', 'Usage time of instance', labelnames=['job', 'flavor', 'name', 'project_id'])

VOLUME_COST_METRIC = prometheus_client.Gauge('volume_cost', 'Cost of volume usage', labelnames=['job', 'type', 'name', 'project_id'])
VOLUME_USAGE_METRIC = prometheus_client.Gauge('volume_usage', 'Usage time of volume', labelnames=['job', 'type', 'name', 'project_id'])

FLOATINGIP_COST_METRIC = prometheus_client.Gauge('floatingip_cost', 'Cost of floatingip usage', labelnames=['job', 'name', 'project_id'])
FLOATINGIP_USAGE_METRIC = prometheus_client.Gauge('floatingip_usage', 'Usage time of floatingip', labelnames=['job', 'name', 'project_id'])

ROUTER_COST_METRIC = prometheus_client.Gauge('router_cost', 'Cost of router usage', labelnames=['job', 'name', 'project_id'])
ROUTER_USAGE_METRIC = prometheus_client.Gauge('router_usage', 'Usage time of router', labelnames=['job', 'name', 'project_id'])

SNAPSHOT_COST_METRIC = prometheus_client.Gauge('snapshot_cost', 'Cost of snapshot usage', labelnames=['job', 'name', 'project_id'])
SNAPSHOT_USAGE_METRIC = prometheus_client.Gauge('snapshot_usage', 'Usage time of snapshot', labelnames=['job', 'name', 'project_id'])

IMAGE_COST_METRIC = prometheus_client.Gauge('image_cost', 'Cost of image usage', labelnames=['job', 'name', 'project_id'])
IMAGE_USAGE_METRIC = prometheus_client.Gauge('image_usage', 'Usage time of image', labelnames=['job', 'name', 'project_id'])

# Resource growth
TOTAL_RESOURCE_METRIC = prometheus_client.Gauge('total_resource', 'Total Active Resource', labelnames=['job', 'resources'])

