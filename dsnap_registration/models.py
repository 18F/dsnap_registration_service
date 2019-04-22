from django.contrib.postgres.fields import JSONField
from django.db import models


class Registration(models.Model):
    class Meta:
        db_table = "registration"
    original_data = JSONField(editable=False)
    latest_data = JSONField()
    rules_service_approved = models.BooleanField(null=True)
    user_approved = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=False, auto_now_add=True,
                                      editable=False)
    modified_by = models.ForeignKey('auth.User', null=True,
                                    related_name='+',
                                    on_delete=models.PROTECT)
    modified_at = models.DateTimeField(null=False, auto_now=True,
                                       editable=False)
    approved_by = models.ForeignKey('auth.User', null=True,
                                    related_name='registrations',
                                    on_delete=models.PROTECT)
    approved_at = models.DateTimeField(null=True)
