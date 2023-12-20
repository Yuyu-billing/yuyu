from typing import Any
from django.utils import timezone
from django.db import models

def current_localtime():
    return timezone.localtime(timezone.now())

# A DateTimeField that return local time instead of UTC to make it easier to calculate duration
class DateTimeLocalField(models.DateTimeField):
    def from_db_value(self, value, expression, connection) -> Any:
        if value is None:
            return None
        else:
            return timezone.localtime(value)
    