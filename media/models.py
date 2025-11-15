from django.db import models

from actor.models import Actor

# Create your models here.
class Media(models.Model):
    id = models.TextField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, null=True)
    category = models.TextField(null=True)
    tags = models.TextField(null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_video = models.BooleanField(db_index=True, default=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    length = models.IntegerField(default=0)


class OneWeekVideoStatics(models.Model):
    id = models.OneToOneField(Media, on_delete=models.CASCADE, primary_key=True)
    points = models.IntegerField()