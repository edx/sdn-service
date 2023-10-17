"""
Models for the sanctions app
"""
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class SanctionsCheckFailure(TimeStampedModel):
    """ Record of SDN and ISN check failure. """
    history = HistoricalRecords()
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    lms_user_id = models.IntegerField(null=True, db_index=True)
    city = models.CharField(max_length=32, default='')
    country = models.CharField(max_length=2)
    sanctions_type = models.CharField(max_length=255)
    system_identifier = models.CharField(max_length=255)
    order_identifier = models.CharField(max_length=128, default=None, null=True)
    order_type = models.CharField(max_length=255)
    order_total = models.DecimalField(null=True, decimal_places=2, max_digits=12)
    sdn_check_response = models.JSONField()

    class Meta:
        verbose_name = 'Sanctions Check Failure'

    def __str__(self):
        return 'Sanctions check failure [{username}]'.format(
            username=self.username
        )
