from django.db import models


class SystemProfile(models.Model):
    name = models.CharField(max_length=255)
    cpu = models.IntegerField()
    memory = models.IntegerField()
    nodes = models.IntegerField()

    def __str__(self):
        return self.name
