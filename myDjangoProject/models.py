from django.db import models


class Ident(models.Model):
   Username = models.CharField(max_length=128, blank=True, null=True)
   Password = models.CharField(max_length=128, blank=True, null=True)
   Password2 = models.CharField(max_length=128, blank=True, null=True)


class Log(models.Model):
   Username = models.CharField(max_length=30)
   Password = models.CharField(max_length=30)
   Date = models.DateTimeField()
   Connection= models.CharField(max_length=30)
   Is_delete= models.BooleanField()
   Date_retard= models.DateTimeField()


