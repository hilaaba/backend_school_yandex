from django.db import models

CHOICES = (
    ('FILE', 'файл'),
    ('FOLDER', 'папка'),
)


class Item(models.Model):
    id = models.UUIDField(primary_key=True)
    type = models.CharField(max_length=6, choices=CHOICES)
    date = models.DateTimeField()
    url = models.TextField(null=True)
    size = models.PositiveIntegerField(null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.type}({self.url}, {self.date}, {self.size})'


class History(models.Model):
    url = models.CharField(max_length=255, null=True)
    size = models.PositiveIntegerField(null=True)
    date = models.DateField()
    parentId = models.UUIDField(null=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)

    def __str__(self):
        return (
            f'History({self.url}, {self.date}, {self.size}, {self.parentId})'
        )
