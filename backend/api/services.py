from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
)

from .models import FILE, History, Item

RESPONSE_VALIDATION_ERROR = Response(
    {'code': HTTP_400_BAD_REQUEST, 'message': 'Validation Failed'},
    status=HTTP_400_BAD_REQUEST,
)

RESPONSE_ITEM_NOT_FOUND = Response(
    {'code': HTTP_404_NOT_FOUND, 'message': 'Item not found'},
    status=HTTP_404_NOT_FOUND,
)

RESPONSE_OK = Response(status=HTTP_200_OK)


def get_object_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def get_datetime_object(date_str):
    try:
        return datetime.strptime(date_str, settings.DATE_TIME_FORMAT)
    except ValueError:
        raise ValidationError('Дата обрабатывается согласно ISO 8601')


def get_date_range(range_end):
    range_start = range_end - timedelta(days=1)
    return range_start, range_end


def get_uuid(uuid, version=4):
    try:
        return UUID(uuid, version=version)
    except ValueError:
        raise ValidationError('Недопустимый UUID')


def update_folders_date(items, date):
    folders_ids = {item['parent'].id for item in items if item.get('parent')}
    print(folders_ids)
    updated = set()

    def update_date(folder):
        if folder.parent and folder not in updated:
            updated.add(folder)
            folder.date = date
            folder.save()
            update_date(folder.parent)
        else:
            updated.add(folder)
            folder.date = date
            folder.save()

    for folder_id in folders_ids:
        folder = Item.objects.get(pk=folder_id)
        update_date(folder)


def update_sizes():
    def traverse_and_update(item, sum_size=0):
        if item.type == FILE:
            return item.size
        else:
            children = item.children.all()
            if children:
                for child in children:
                    sum_size += traverse_and_update(child)
                item.size = sum_size
                item.save()
            else:
                item.size = None
                item.save()
            return sum_size

    root_items = Item.objects.filter(parent=None)
    for root_item in root_items:
        traverse_and_update(root_item)


def save_updated_items_in_history(date):
    updated_items = Item.objects.filter(date=date)
    History.objects.bulk_create(
        [History(
            url=item.url,
            type=item.type,
            date=item.date,
            parentId=item.parent.id if item.parent else None,
            size=item.size,
            item=item
        ) for item in updated_items]
    )


def update_unit(unit, item):
    if unit.type != item.get('type'):
        raise ValidationError('Элемент не может менять тип')
    unit.url = item.get('url')
    unit.date = item.get('date')
    unit.size = item.get('size')
    unit.parent = item.get('parent')
    unit.save()
