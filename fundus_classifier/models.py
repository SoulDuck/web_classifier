# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class UploadFile(models.Model):
    file = models.FileField(null=True ,  )#, upload_to='media'



# Create your models here.
