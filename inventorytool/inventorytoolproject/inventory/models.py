from django.db import models


class Network(models.Model):
    name = models.CharField(max_length=255)
    partition_name = models.CharField(max_length=255)
    CIDR = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class VPOD(models.Model):
    network = models.ForeignKey(Network, related_name='VPODS', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    cluster_type = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Instance(models.Model):
    vpod = models.ForeignKey(VPOD, related_name='Instances', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    cpu_type = models.CharField(max_length=255)
    disk = models.CharField(max_length=255)
    cpu = models.IntegerField()
    memory = models.IntegerField()
    os = models.CharField(max_length=255)
    logical_site = models.CharField(max_length=255)

    def __str__(self):
        return self.name
