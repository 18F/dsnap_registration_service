from django.contrib.postgres.fields import JSONField
from django.db import models


class Registration(models.Model):
    class Meta:
        db_table = "registration"
    original_data = JSONField(editable=False)
    latest_data = JSONField()
    created_at = models.DateTimeField(null=False, auto_now_add=True,
                                      editable=False)
    modified_at = models.DateTimeField(null=False, auto_now=True,
                                       editable=False)
    modified_by = models.ForeignKey('auth.User', null=True,
                                    related_name='registrations',
                                    on_delete=models.PROTECT)
