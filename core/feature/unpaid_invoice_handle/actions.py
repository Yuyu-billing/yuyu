from enum import Enum


class UnpainInvoiceAction(Enum):
    SEND_MESSAGE = "send_message"
    STOP_INSTANCE = "stop_instance"
    SUSPEND_INSTANCE = "suspend_instance"
    PAUSE_INSTANCE = "pause_instance"
    DELETE_INSTANCE = "delete_instance"
