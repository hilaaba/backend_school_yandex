from rest_framework.exceptions import ValidationError
from rest_framework.fields import DateTimeField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    CharField, ChoiceField, IntegerField, ModelSerializer, Serializer,
    SerializerMethodField, UUIDField
)

from items.models import CHOICES, FILE, FOLDER, History, Item
from .services import get_object_or_none, update_unit


class ItemSerializer(ModelSerializer):
    """
    Сериализатор модели Item для GET запроса.
    """
    parentId = PrimaryKeyRelatedField(
        source='parent',
        queryset=Item.objects.all(),
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
    """
    Сериализатор модели Item для POST запроса.
    """
    id = UUIDField()
    parentId = UUIDField(source='parent', default=None, allow_null=True)
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
        if data.get('type') == FILE and data.get('size') is None:
            raise ValidationError('У файла должен быть размер')

        if data.get('type') == FILE and data.get('parent') is None:
            raise ValidationError('У файла должна быть родительская папка')

        if data.get('type') == FOLDER and data.get('size'):
            raise ValidationError('У папки не может быть размера')

        if data.get('url') == FOLDER and data.get('url'):
            raise ValidationError('У папки не может быть url')

        if data.get('id') == data.get('parentId'):
            raise ValidationError(
                'Элемент не может быть родителем самого себя'
            )
        return data


class ItemRequest:
    """
    Вспомогательный класс для сериализатора ItemRequestImportSerializer.
    """
    def __init__(self, items, updateDate):
        self.items = items
        self.updateDate = updateDate


class ItemRequestImportSerializer(Serializer):
    """
    Сериализатор для POST запроса на эндпоинт /imports.
    """
    items = ItemImportSerializer(many=True)
    updateDate = DateTimeField()

    def validate_items(self, items):
        ids = set()
        for item in items:
            item_id = item.get('id')
            if item_id in ids:
                raise ValidationError(
                    'В запросе id элементов не должны повторяться'
                )
            ids.add(item_id)
        return items

    def create(self, validated_data):
        instance = ItemRequest(**validated_data)
        items = validated_data.get('items')
        for item in items:
            item['date'] = validated_data['updateDate']
            parent_id = item.get('parent')
            if parent_id:
                try:
                    item['parent'] = Item.objects.get(pk=parent_id)
                    if item['parent'].type == FILE:
                        raise ValueError('Родителем может быть только папка')
                except (Item.DoesNotExist, ValueError):
                    raise ValidationError('Отсутствует родитель с таким id')
            unit = get_object_or_none(Item, pk=item.get('id'))
            if unit:
                if unit.type != item.get('type'):
                    raise ValidationError('Элемент не может менять тип')
                update_unit(unit, item)
            else:
                Item.objects.create(**item)
        return instance


class HistorySerializer(ModelSerializer):
    """
    Сериализатор модели History.
    """
    id = PrimaryKeyRelatedField(source='item', queryset=Item.objects.all())
    parentId = UUIDField(source='parent_id')

    class Meta:
        model = History
        exclude = ('parent_id', 'item')
