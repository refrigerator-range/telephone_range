
from django.db import models
from django.utils import timezone


class Cast(models.Model):
    name = models.CharField(max_length=200)
    resume = models.TextField()

    def __str__(self):
        return self.name


class Genre(models.Model):
    genre = models.CharField(max_length=200)
    create_date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return self.genre


class Director(models.Model):
    name = models.CharField(max_length=200)
    resume = models.TextField()

    def __str__(self):
        return self.name


class Content(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='image', null=True, blank=True)
    payback_time = models.DurationField(null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    release = models.DateTimeField(default=timezone.now(), null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True)
    director = models.ForeignKey(Director, on_delete=models.CASCADE, null=True, blank=True)
    cast = models.ManyToManyField(Cast, null=True, blank=True)
    award = models.CharField(max_length=200, null=True, blank=True)
    # votes = models.IntegerField(default=0)

    def __str__(self):
        return self.title
