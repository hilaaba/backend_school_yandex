from django.db import models

FILE = 'FILE'
FOLDER = 'FOLDER'

CHOICES = (
    (FILE, 'файл'),
    (FOLDER, 'папка'),
)


class Item(models.Model):
    id = models.UUIDField(primary_key=True)
    type = models.CharField(max_length=6, choices=CHOICES, verbose_name='Тип')
    date = models.DateTimeField(verbose_name='Дата')
    url = models.TextField(null=True, verbose_name='Адрес')
    size = models.PositiveIntegerField(null=True, verbose_name='Размер')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Родитель',
        related_name='children',
    )

    class Meta:
        verbose_name = 'Элемент'
        verbose_name_plural = 'Элементы'

    def __str__(self):
        return f'{self.id}'


class History(models.Model):
    date = models.DateTimeField(verbose_name='Дата')
    url = models.TextField(null=True, verbose_name='Адрес')
    size = models.PositiveIntegerField(null=True, verbose_name='Размер')
    parentId = models.UUIDField(null=True)
    item = models.ForeignKey(
        Item,
        related_name='histories',
        on_delete=models.CASCADE,
        verbose_name='Элемент',
    )

    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'История'

    def __str__(self):
        return (
            f'url: {self.url}, '
            f'date: {self.date}, '
            f'size: {self.size}, '
            f'parentId: {self.parentId}'
        )
