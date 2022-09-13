from rest_framework.exceptions import ValidationError
from rest_framework.fields import DateTimeField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    CharField, ChoiceField, IntegerField, ModelSerializer, Serializer,
    SerializerMethodField, UUIDField
)

from .models import CHOICES, FILE, FOLDER, History, Item


class ItemGetSerializer(ModelSerializer):
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


class ItemPostSerializer(ModelSerializer):
    parentId = UUIDField(default=None, allow_null=True)
    url = CharField(default=None, required=False)
    size = IntegerField(default=None, required=False)
    type = ChoiceField(choices=CHOICES)

    class Meta:
        model = Item
        exclude = ('date', 'parent')

    def validate_url(self, url):
        if url is None:
            return None
        if url[0] != '/':
            raise ValidationError('Url должен начинаться с прямого слэша')
        return url

    def validate_size(self, size):
        if size is None:
            return None
        if int(size) < 0:
            raise ValidationError('Недопустимое значение размера')
        return size

    def validate(self, data):
        if data.get('type') == FOLDER and data.get('size'):
            raise ValidationError('У папки не может быть размера')
        return data


class ItemRequest:
    def __init__(self, items, updateDate):
        self.items = items
        self.updateDate = updateDate


class ItemRequestImportSerializer(Serializer):
    items = ItemPostSerializer(many=True)
    updateDate = DateTimeField()

    def create(self, validated_data):
        instance = ItemRequest(**validated_data)
        items = validated_data.get('items')
        for item in items:
            item['date'] = validated_data['updateDate']
            parentId = item.pop('parentId')
            if parentId is not None:
                try:
                    item['parent'] = Item.objects.get(pk=parentId)
                except Item.DoesNotExist:
                    raise ValidationError('Отсутствует родитель с таким id')
            Item.objects.update_or_create(**item)
        return instance


class HistorySerializer(ModelSerializer):
    type = CharField(default=FILE)

    class Meta:
        model = History
        fields = '__all__'
