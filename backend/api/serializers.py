from rest_framework.exceptions import ValidationError
from rest_framework.fields import DateTimeField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    CharField, ChoiceField, IntegerField, ModelSerializer, Serializer,
    SerializerMethodField, UUIDField
)

from .models import CHOICES, FILE, FOLDER, History, Item
from .services import get_object_or_none


class ItemSerializer(ModelSerializer):
    parentId = PrimaryKeyRelatedField(
        source='parent',
        queryset=Item.objects.all(),
        allow_null=True,
    )
    children = SerializerMethodField(read_only=True)
    type = ChoiceField(choices=CHOICES)

    class Meta:
        model = Item
        exclude = ('parent',)

    def get_children(self, obj):
        if obj.type == FILE:
            return None
        return self.__class__(obj.children.all(), many=True).data


class ItemImportSerializer(ModelSerializer):
    id = UUIDField()
    parentId = UUIDField(default=None, allow_null=True)
    url = CharField(default=None, required=False)
    size = IntegerField(default=None, required=False)
    type = ChoiceField(choices=CHOICES)

    class Meta:
        model = Item
        exclude = ('date', 'parent')

    def validate_url(self, url):
        if url is None:
            return url
        if url[0] != '/':
            raise ValidationError('Url должен начинаться с прямого слэша')
        return url

    def validate_size(self, size):
        if size is None:
            return size
        if int(size) <= 0:
            raise ValidationError('Недопустимое значение размера')
        return size

    def validate(self, data):
        if data.get('type') == FOLDER and data.get('size'):
            raise ValidationError('У папки не может быть размера')
        if data.get('url') == FOLDER and data.get('url'):
            raise ValidationError('У папки не может быть url')
        return data


class ItemRequest:
    def __init__(self, items, updateDate):
        self.items = items
        self.updateDate = updateDate


class ItemRequestImportSerializer(Serializer):
    items = ItemImportSerializer(many=True)
    updateDate = DateTimeField()

    def validate_items(self, items):
        ids = set()
        for item in items:
            item_id = item.get('id')
            if item_id in ids:
                raise ValidationError('В запросе id не должны повторяться')
            ids.add(item_id)
        return items

    def create(self, validated_data):
        instance = ItemRequest(**validated_data)
        items = validated_data.get('items')
        for item in items:
            item['date'] = validated_data['updateDate']
            parent_id = item.pop('parentId')
            if parent_id:
                try:
                    item['parent'] = Item.objects.get(pk=parent_id)
                    if item['parent'].type == FILE:
                        raise ValueError
                except (Item.DoesNotExist, ValueError):
                    raise ValidationError('Отсутствует родитель с таким id')
            unit = get_object_or_none(Item, pk=item.get('id'))
            if unit:
                History.objects.create(
                    url=unit.url,
                    type=unit.type,
                    date=unit.date,
                    size=unit.size,
                    parentId=unit.parent.id,
                    item=unit,
                )
                unit.url = item.url if item.get('url') else None
                unit.type = item.type
                unit.date = item.date
                unit.size = item.size if item.get('size') else None
                unit.parent = item.parent if item.get('parent') else None
                unit.save()
            else:
                Item.objects.create(**item)
        return instance


class HistorySerializer(ModelSerializer):

    class Meta:
        model = History
        fields = '__all__'
