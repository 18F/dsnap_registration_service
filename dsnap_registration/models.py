from django.contrib.postgres.fields import JSONField
from django.db import models


class Registration(models.Model):
    class Meta:
        db_table = "registration"
    created_date = models.DateField(null=False, auto_now_add=True,
                                    editable=False)
    modified_date = models.DateField(null=False, auto_now=True, editable=False)
    original_data = JSONField(editable=False)
    latest_data = JSONField()
