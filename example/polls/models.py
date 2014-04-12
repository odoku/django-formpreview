import os

from django.db import models


class Poll(models.Model):
    def upload_to(self, filepath):
        filename = os.path.basename(filepath)
        return os.path.join('poll', filename)

    question = models.CharField(max_length=200)
    main_image = models.ImageField('main image', upload_to=upload_to)
    sub_image = models.ImageField('sub image', upload_to=upload_to, blank=True, null=True)
