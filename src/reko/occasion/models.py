from __future__ import annotations
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self) -> str:
        return f"{self.time_start}-{self.time_end} {self.name}"


class OccasionManager(models.Manager):
    def get_current(self) -> Occasion:
        # TODO: Look at the current date and find the proper occasion
        return self.get()


class Occasion(models.Model):
    date = models.DateField()
    is_published = models.BooleanField()

    locations = models.ManyToManyField(Location)
    producers = models.ManyToManyField("producer.producer")

    objects = OccasionManager()
