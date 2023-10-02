from djmoney.contrib.django_rest_framework import MoneyField
from djmoney.settings import DECIMAL_PLACES
from rest_framework import serializers

from api import custom_validator
from core.models import Invoice, BillingProject, Notification, Balance, BalanceTransaction
from core.component import component


class InvoiceComponentSerializer(serializers.ModelSerializer):
    adjusted_end_date = serializers.DateTimeField()
    price_charged = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    price_charged_currency = serializers.CharField(source="price_charged.currency")


def generate_invoice_component_serializer(model):
    """
    Generate Invoice Component Serializer for particular model
    :param model: The invoice component model
    :return: serializer for particular model
    """
    name = type(model).__name__
    meta_params = {
        "model": model,
        "fields": "__all__"
    }
    meta_class = type("Meta", (object,), meta_params)
    serializer_class = type(f"{name}Serializer", (InvoiceComponentSerializer,), {"Meta": meta_class})

    return serializer_class


class InvoiceSerializer(serializers.ModelSerializer):
    subtotal = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    subtotal_currency = serializers.CharField(source="subtotal.currency")
    total = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    total_currency = serializers.CharField(source="total.currency", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field, model in component.INVOICE_COMPONENT_MODEL.items():
            self.fields[field] = generate_invoice_component_serializer(model)(many=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class SimpleInvoiceSerializer(serializers.ModelSerializer):
    subtotal = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    subtotal_currency = serializers.CharField(source="subtotal.currency")
    total = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    total_currency = serializers.CharField(source="total.currency", required=False)

    class Meta:
        model = Invoice
        fields = ['id', 'start_date', 'end_date', 'state', 'tax', 'subtotal', 'subtotal_currency', 'total',
                  'total_currency']


class BillingProjectSerializer(serializers.ModelSerializer):
    tenant_id = serializers.CharField(required=False, read_only=True)
    email_notification = serializers.CharField(required=False, validators=[custom_validator.email_list])

    class Meta:
        model = BillingProject
        fields = ['tenant_id', 'email_notification']


class NotificationSerializer(serializers.ModelSerializer):
    project = BillingProjectSerializer()
    recipient = serializers.CharField()

    class Meta:
        model = Notification
        fields = ['id', 'project', 'title', 'short_description', 'content', 'sent_status', 'is_read', 'created_at',
                  'recipient']


class BalanceSerializer(serializers.ModelSerializer):
    project = BillingProjectSerializer()
    amount = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    amount_currency = serializers.CharField(source="amount.currency")

    class Meta:
        model = Balance
        fields = ['id', 'project', 'amount', 'amount_currency']


class BalanceTransactionSerializer(serializers.ModelSerializer):
    amount = MoneyField(max_digits=256, decimal_places=DECIMAL_PLACES)
    amount_currency = serializers.CharField(source="amount.currency")
    action = serializers.CharField(required=False)
    description = serializers.CharField()

    class Meta:
        model = BalanceTransaction
        fields = ['id', 'amount', 'amount_currency', 'action', 'description', 'created_at']


