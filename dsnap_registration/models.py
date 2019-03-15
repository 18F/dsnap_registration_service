from django.db import models

from django.contrib.postgres.fields import JSONField

class Registration(models.Model):
    class Meta:
        db_table = "registration"
    created_date = models.DateField(null=False, auto_now_add=True)
    modified_date = models.DateField(null=False, auto_now=True)
    original_data = JSONField(editable=False)
    latest_data = JSONField()

    def __str__(self):
        return self.original_data['county']
