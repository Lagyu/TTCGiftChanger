from django.db import models
import datetime
# Create your models here.


class Event(models.Model):
    creation_date = models.DateTimeField("date created")
    event_date = models.DateField(default=datetime.date.today)
    email = models.EmailField()
    number_of_gifts = models.IntegerField(default=8)
    show_name_before_match = models.BooleanField(default=False)
    show_name_after_match = models.BooleanField(default=True)
    password = models.CharField(max_length=30)
    event_name = models.CharField(max_length=50)
    event_id = models.CharField(max_length=36, primary_key=True)
    allow_picture = models.BooleanField(default=False)
    force_picture = models.BooleanField(default=False)


class Gift(models.Model):
    parent_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=20)
    gift_title = models.CharField(max_length=40, default="")
    gift_description = models.CharField(max_length=1000, default="")
    preference_list_str = models.CharField(max_length=10000, default="")
    not_selected_list_str = models.CharField(max_length=10000, default="")



