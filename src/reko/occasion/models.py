from __future__ import annotations

from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self) -> str:
        return (
            f"{self.time_start.strftime('%H:%M')}"
            " – "
            f"{self.time_end.strftime('%H:%M')} {self.name}"
        )


class OccasionManager(models.Manager["Occasion"]):
    pass


class Occasion(models.Model):
    date = models.DateField()
    is_published = models.BooleanField()

    locations = models.ManyToManyField(Location)
    producers = models.ManyToManyField("producer.Producer")

    objects = OccasionManager()
