from datetime import datetime
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_uuid(uuid, version=4):
    try:
        _ = UUID(uuid, version=version)
    except ValueError:
        raise ValidationError('Invalid UUID')


def validate_date(date):
    try:
        _ = datetime.strptime(date, settings.DATE_TIME_FORMAT)
    except ValueError:
        raise ValidationError('Invalid date (must be ISO8601 formatted)')
