from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Actor(models.Model):
    id = models.ForeignKey(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    about = models.TextField()
    subscribers = models.IntegerField()
    videos = models.IntegerField()

class ActorDetails(models.Model):
    actor = models.OneToOneField(Actor, on_delete=models.CASCADE, primary_key=True)
    relationship = models.IntegerField(null=True) # 0: 없음, 1: 연애 중,  2: 결혼함
    interests = models.TextField(null=True)
    gender = models.TextField(null=True)
    birth_date = models.DateField(null=True)
    birth_location = models.TextField(null=True)
    endowment = models.IntegerField(null=True) # 사이즈 (cm)
    height = models.IntegerField() # (cm로)
    weight = models.IntegerField() # (kg로)
    ethnicity = models.TextField() # 인종
    hair_color = models.TextField(null=True) # 머리 색상
    foreskin = models.TextField(null=True) # 네 .. 번역기 돌려보세요..
    facial_hair = models.TextField(null=True) # 수염
    tattoos = models.BooleanField(null=True) # 타투 여부
    piercing = models.BooleanField(null=True) # 피어싱 여부
    interest = models.TextField(null=True) # 관심 분야
    turns_on = models.IntegerField(null=True) # 흥분 시키는 무언가
    turns_off = models.IntegerField(null=True) # 극혐하는거