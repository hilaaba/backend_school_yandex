from datetime import datetime
from uuid import UUID

from django.core.exceptions import ValidationError
from django.conf import settings

from .models import Item


def validate_uuid(uuid, version=4):
    try:
        uuid_object = UUID(uuid, version=version)
    except ValueError:
        raise ValidationError('Invalid UUID')


def validate_type(value):
    try:
        assert value in ('FILE', 'FOLDER')
    except AssertionError:
        raise ValidationError('Invalid type (must be FOLDER or FILE)')


def validate_date(date):
    try:
        date_object = datetime.strptime(date, settings.DATE_TIME_FORMAT)
    except ValueError:
        raise ValidationError('Invalid date (must be ISO8601 formatted)')


def validate_parent(parent_id: str):
    if parent_id is None:
        return None
    try:
        parent = Item.objects.get(pk=parent_id)
    except Item.DoesNotExist:
        raise ValidationError('ParentId refers non-existing object')
    try:
        assert parent.type == 'FOLDER'
    except AssertionError:
        raise ValidationError('ParentId must refer folder object')


def validate_size(item):
    item_type = item['type']
    try:
        if item_type == 'FILE':
            size = item['size']
            assert isinstance(size, int) and size >= 0
        else:
            assert 'size' not in item
    except AssertionError:
        raise ValidationError('Invalid size')


def validate_url(url):
    if url is None:
        return None
    try:
        assert url[0] == '/'
    except AssertionError:
        raise ValidationError('Url must start with slash')


def validate_all_params(import_item, date):
    missing = []
    for param in ('id', 'type', 'parentId'):
        if param not in import_item:
            missing.append(param)
    try:
        assert not missing
    except AssertionError:
        missing = ', '.join(missing)
        raise ValidationError(f'Missing required parameter(s): {missing}')

    validate_date(date)
    validate_uuid(import_item['id'])
    validate_type(import_item['type'])
    validate_parent(import_item['parentId'])
    if 'url' in import_item:
        validate_url(import_item['url'])
    if 'size' in import_item:
        validate_size(import_item)
