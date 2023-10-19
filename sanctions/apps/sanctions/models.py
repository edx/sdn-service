"""
Models for the sanctions app
"""
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class SanctionsCheckFailure(TimeStampedModel):
    """
    Model for recording SDN and ISN check failures.

    Fields:
    sanctions_type (Charfield): which type of check was done, ie. 'SDN' for now
    until another type of sanctions is added in the future.

    system_identifier (Charfield): which system/service is making the request to the sanctions service.

    metadata (JSONField): JSON containing information associated to the sanctions failure,
    like order_identifer, total, and purchase_type (single, program, bulk).

    sdn_check_response (JSONField): response received for a hit when calling the trade.gov SDN API.

    Example:
        >>> SanctionsCheckFailure.objects.create(
        full_name='Keyser Söze',
        username='UnusualSuspect',
        city='Boston',
        country='US',
        sanctions_type='SDN',
        system_identifier='commerce-coordinator',
        metadata={'order_identifer': 'EDX-123456', 'purchase_type': 'program', 'order_total': '989.00'},
        sdn_check_response={'description': 'Looks a bit suspicious.'},
        )

    """
    history = HistoricalRecords()
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    lms_user_id = models.IntegerField(null=True, db_index=True)
    city = models.CharField(max_length=32, default='')
    country = models.CharField(max_length=2)
    sanctions_type = models.CharField(max_length=255)
    system_identifier = models.CharField(max_length=255)
    metadata = models.JSONField()
    sdn_check_response = models.JSONField()

    class Meta:
        verbose_name = 'Sanctions Check Failure'

    def __str__(self):
        return 'Sanctions check failure [{username}]'.format(
            username=self.username
        )


class SanctionsFallbackMetadata(TimeStampedModel):
    """
    Record metadata about the SDN fallback CSV file download.
    This table is used to track the state of the SDN CSV file data that are currently
    being used or about to be updated/deprecated.
    This table does not keep track of the SDN files over time.
    """
    history = HistoricalRecords()
    file_checksum = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    download_timestamp = models.DateTimeField()
    import_timestamp = models.DateTimeField(null=True, blank=True)

    IMPORT_STATES = [
        ('New', 'New'),
        ('Current', 'Current'),
        ('Discard', 'Discard'),
    ]

    import_state = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(1)],
        unique=True,
        choices=IMPORT_STATES,
        default='New',
    )


class SanctionsFallbackData(models.Model):
    """
    Model used to record and process one row received from SanctionsFallbackMetadata.

    Fields:
    sanctions_fallback_metadata (ForeignKey): Foreign Key field with the CSV import Primary Key
    referenced in SanctionsFallbackMetadata.

    source (CharField): Origin of where the data comes from, since the CSV consolidates
    export screening lists of the Departments of Commerce, State and the Treasury.

    sdn_type (CharField): For a person with source 'Specially Designated Nationals (SDN) -
    Treasury Department', the type is 'Individual'. Other options include 'Entity' and
    'Vessel'. Other lists do not have a type.

    names (TextField): A space separated list of all lowercased names and alt names with
    punctuation also replaced by spaces.

    addresses (TextField): A space separated list of all lowercased addresses combined into one
    string. There are records that don't have an address, but because city is a required field
    in the Payment MFE, those records would not be matched in the API/fallback.

    countries (CharField): A space separated list of all countries combined into one string.
    Countries are extracted from the addresses field and in some instances the ID field in their
    2 letter abbreviation. There are records that don't have a country, but because country is a
    required field in billing information form, those records would not be matched in the API/fallback.
    """
    history = HistoricalRecords()
    sanctions_fallback_metadata = models.ForeignKey(SanctionsFallbackMetadata, on_delete=models.CASCADE)
    source = models.CharField(default='', max_length=255, db_index=True)
    sdn_type = models.CharField(default='', max_length=255, db_index=True)
    names = models.TextField(default='')
    addresses = models.TextField(default='')
    countries = models.CharField(default='', max_length=255)
