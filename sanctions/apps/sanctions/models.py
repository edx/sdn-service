"""
Models for the sanctions app
"""
import logging
from datetime import datetime

from django.core.validators import MinLengthValidator
from django.db import models
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

logger = logging.getLogger(__name__)


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
        sanctions_type='ISN,SDN',
        system_identifier='commerce-coordinator',
        metadata={'order_identifer': 'EDX-123456', 'purchase_type': 'program', 'order_total': '989.00'},
        sdn_check_response={'description': 'Looks a bit suspicious.'},
        )

    """
    history = HistoricalRecords()
    full_name = models.CharField(max_length=255)
    username = models.CharField(null=True, max_length=255)
    lms_user_id = models.IntegerField(null=True, db_index=True)
    city = models.CharField(max_length=32, default='')
    country = models.CharField(max_length=2)
    sanctions_type = models.CharField(max_length=255)
    system_identifier = models.CharField(null=True, max_length=255)
    metadata = models.JSONField(null=True)
    sanctions_response = models.JSONField(null=True)

    class Meta:
        verbose_name = 'Sanctions Check Failure'

    def __str__(self):
        return 'Sanctions check failure [{username}]'.format(
            username=self.username
        )


class SDNFallbackMetadata(TimeStampedModel):
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

    @classmethod
    def insert_new_sdn_fallback_metadata_entry(cls, file_checksum):
        """
        Insert a new SDNFallbackMetadata entry if the new CSV differs from the current one.
        If there is no current metadata entry, create a new one and log a warning.

        Args:
            file_checksum (str): Hash of the CSV content

        Returns:
            sdn_fallback_metadata_entry (SDNFallbackMetadata): Instance of the current SDNFallbackMetadata class
            or None if none exists
        """
        now = datetime.utcnow()
        try:
            if file_checksum == SDNFallbackMetadata.objects.get(import_state='Current').file_checksum:
                logger.info(
                    "Sanctions SDNFallback: The CSV file has not changed, so skipping import. The file_checksum was %s",
                    file_checksum)
                # Update download timestamp even though we're not importing this list
                SDNFallbackMetadata.objects.filter(import_state="New").update(download_timestamp=now)
                return None
        except SDNFallbackMetadata.DoesNotExist:
            logger.warning("Sanctions SDNFallback: SDNFallbackMetadata has no record with import_state Current")

        sdn_fallback_metadata_entry = SDNFallbackMetadata.objects.create(
            file_checksum=file_checksum,
            download_timestamp=now,
        )
        return sdn_fallback_metadata_entry

    @classmethod
    @atomic
    def swap_all_states(cls):
        """
        Shifts all of the existing metadata table rows to the next import_state
        in the row's lifecycle (see _swap_state).

        This method is done in a transaction to gurantee that existing metadata rows are
        shifted into their next states in sync and tries to ensure that there is always a row
        in the 'Current' state. Rollbacks of all row's import_state changes will happen if:
        1) There are multiple rows & none of them are 'Current', or
        2) There are any issues with the existing rows + updating them (e.g. a row with a
        duplicate import_state is manually inserted into the table during the transaction)
        """
        SDNFallbackMetadata._swap_state('Discard')
        SDNFallbackMetadata._swap_state('Current')
        SDNFallbackMetadata._swap_state('New')

        # After the above swaps happen:
        # If there are 0 rows in the table, there cannot be a row in the 'Current' status.
        # If there is 1 row in the table, it is expected to be in the 'Current' status
        # (e.g. when the first file is added + just swapped).
        # If there are 2 rows in the table, after the swaps, we expect to have one row in
        # the 'Current' status and one row in the 'Discard' status.
        if len(SDNFallbackMetadata.objects.all()) >= 1:
            try:
                SDNFallbackMetadata.objects.get(import_state='Current')
            except SDNFallbackMetadata.DoesNotExist:
                logger.warning(
                    "Sanctions SDNFallback: Expected a row in the 'Current' import_state after swapping,"
                    " but there are none.",
                )
                raise

    @classmethod
    def _swap_state(cls, import_state):
        """
        Update the row in the given import_state parameter to the next import_state.
        Rows in this table should progress from New -> Current -> Discard -> (row deleted).
        There can be at most one row in each import_state at a given time.
        """
        try:
            existing_metadata = SDNFallbackMetadata.objects.get(import_state=import_state)
            if import_state == 'Discard':
                existing_metadata.delete()
            else:
                if import_state == 'New':
                    existing_metadata.import_state = 'Current'
                elif import_state == 'Current':
                    existing_metadata.import_state = 'Discard'
                existing_metadata.full_clean()
                existing_metadata.save()
        except SDNFallbackMetadata.DoesNotExist:
            logger.info(
                "Sanctions SDNFallback: Cannot update import_state of %s row if there is no row in this state.",
                import_state
            )


class SDNFallbackData(models.Model):
    """
    Model used to record and process one row received from SDNFallbackMetadata.

    Fields:
    sdn_fallback_metadata (ForeignKey): Foreign Key field with the CSV import Primary Key
    referenced in SDNFallbackMetadata.

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
    sdn_fallback_metadata = models.ForeignKey(SDNFallbackMetadata, on_delete=models.CASCADE)
    source = models.CharField(default='', max_length=255, db_index=True)
    sdn_type = models.CharField(default='', max_length=255, db_index=True)
    names = models.TextField(default='')
    addresses = models.TextField(default='')
    countries = models.CharField(default='', max_length=255)

    @classmethod
    def get_current_records_and_filter_by_source_and_type(cls, source, sdn_type):
        """
        Query the records that have 'Current' import state, and filter by source and sdn_type.
        """
        try:
            current_metadata = SDNFallbackMetadata.objects.get(import_state='Current')

        # The 'get' relies on the manage command having been run. If it fails, tell engineer what's needed
        except SDNFallbackMetadata.DoesNotExist as fallback_metadata_no_exist:
            logger.warning(
                "Sanctions SDNFallback: SDNFallbackMetadata is empty! Run this: "
                "./manage.py populate_sdn_fallback_data_and_metadata"
            )
            raise Exception(
                'Sanctions SDNFallback empty error when calling checkSDNFallback, data is not yet populated.'
            ) from fallback_metadata_no_exist
        query_params = {'source': source, 'sdn_fallback_metadata': current_metadata, 'sdn_type': sdn_type}
        return SDNFallbackData.objects.filter(**query_params)
