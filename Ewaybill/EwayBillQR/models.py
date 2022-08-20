from django.db import models

# Create your models here.
class qrdata(models.Model):
    ewb_no = models.CharField(max_length=70) 
    ewb_date = models.CharField(max_length=70)
    gen_date = models.CharField(max_length=70)
    ewb_valid_till = models.CharField(max_length=70)
    gen_by = models.CharField(max_length=70)
