from datetime import datetime, timedelta

from django.conf import settings

from .models import History, Item, FILE


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def get_date_range(request_date):
    range_end = datetime.strptime(request_date, settings.DATE_TIME_FORMAT)
    range_start = range_end - timedelta(days=1)
    return [range_start, range_end]


def get_datetime_object(date_str):
    return datetime.strptime(date_str, settings.DATE_TIME_FORMAT)


def get_update_data(items):
    affected_folders_ids = set()
    updated_or_added_ids = set()
    for item in items:
        if item.get('parentId') is not None:
            affected_folders_ids.add(item['parentId'])
        updated_or_added_ids.add(item['id'])
    return affected_folders_ids, updated_or_added_ids


def update_dates(affected_folders_ids, date):
    def traverse_and_update(folder):
        if folder.parent and folder not in updated:
            updated.add(folder)
            folder.date = date
            folder.save()
            folder = folder.parent
            traverse_and_update(folder)
        else:
            updated.add(folder)
            folder.date = date
            folder.save()

    updated = set()
    for folder_id in affected_folders_ids:
        folder = Item.objects.get(pk=folder_id)
        traverse_and_update(folder)
    return None


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


def save_history(item_id):
    item = Item.objects.get(pk=item_id)
    if item.type == FILE:
        values = {
            'url': item.url,
            'date': item.date,
            'size': item.size,
            'parentId': item.parent.id if item.parent else None,
            'item': item,
        }
        obj = History(**values)
        obj.save()
