"""
Tests for Sanctions models.
"""
from datetime import datetime

from django.test import TestCase
from testfixtures import LogCapture

# from ecommerce.extensions.payment.exceptions import SDNFallbackDataEmptyError
from sanctions.apps.sanctions.models import (
    SanctionsCheckFailure,
    SDNFallbackData,
    SDNFallbackMetadata
)
from sanctions.apps.sanctions.tests.factories import (
    SDNFallbackMetadataFactory,
    SDNFallbackDataFactory
)


class SanctionsCheckFailureTests(TestCase):
    """
    Tests for SanctionsCheckFailure model.
    """
    def setUp(self):
        super().setUp()
        self.full_name = 'Keyser Söze'
        self.username = 'UnusualSuspect'
        self.country = 'US'
        self.sdn_check_response = {'description': 'Looks a bit suspicious.'}

    def test_unicode(self):
        """ Verify the __unicode__ method returns the correct value. """
        hit = SanctionsCheckFailure.objects.create(
            full_name=self.full_name,
            username=self.username,
            country=self.country,
            sanctions_type='SDN',
            system_identifier='commerce-coordinator',
            metadata={'order_identifer': 'EDX-123456', 'purchase_type': 'program', 'order_total': '989.00'},
            sdn_check_response=self.sdn_check_response
        )
        expected = 'Sanctions check failure [{username}]'.format(
            username=self.username
        )

        self.assertEqual(str(hit), expected)


class SDNFallbackMetadataTests(TestCase):
    """
    Tests for SDNFallbackMetadata model.
    """
    LOGGER_NAME = 'sanctions.apps.sanctions.models'

    def test_minimum_requirements(self):
        """Make sure the row is created correctly with the minimum dataset + defaults."""
        new_metadata = SDNFallbackMetadata(
            file_checksum="foobar",
            download_timestamp=datetime.now(),
        )
        new_metadata.full_clean()
        new_metadata.save()

        self.assertEqual(len(SDNFallbackMetadata.objects.all()), 1)

        actual_metadata = SDNFallbackMetadata.objects.all()[0]
        self.assertEqual(actual_metadata.file_checksum, "foobar")
        self.assertIsInstance(actual_metadata.download_timestamp, datetime)
        self.assertEqual(actual_metadata.import_timestamp, None)
        self.assertEqual(actual_metadata.import_state, 'New')
        self.assertIsInstance(actual_metadata.created, datetime)
        self.assertIsInstance(actual_metadata.modified, datetime)

    def test_swap_new_row(self):
        """Swap New row to Current row."""
        SDNFallbackMetadataFactory.create(import_state='New')

        SDNFallbackMetadata.swap_all_states()

        actual_rows = SDNFallbackMetadata.objects.all()
        self.assertEqual(len(actual_rows), 1)
        self.assertEqual(actual_rows[0].import_state, 'Current')

    def test_swap_current_row(self):
        """Swap Current row to Discard row."""
        original = SDNFallbackMetadataFactory.create(import_state="Current")
        # this is needed to bypass the requirement to always have a 'Current'
        SDNFallbackMetadataFactory.create(import_state="New")

        SDNFallbackMetadata.swap_all_states()

        actual_row = SDNFallbackMetadata.objects.filter(file_checksum=original.file_checksum)[0]
        self.assertEqual(actual_row.import_state, 'Discard')

    def test_swap_discard_row(self):
        """Discard row gets deleted when swapping rows."""
        SDNFallbackMetadataFactory.create(import_state="Discard")

        SDNFallbackMetadata.swap_all_states()

        actual_rows = SDNFallbackMetadata.objects.all()
        self.assertEqual(len(actual_rows), 0)

    def test_swap_twice_one_row(self):
        """Swapping one row twice without adding a new file should result in an error."""
        original = SDNFallbackMetadataFactory.create(import_state="New")
        expected_logs = [
            (
                self.LOGGER_NAME,
                'WARNING',
                "Expected a row in the 'Current' import_state after swapping, but there are none."
            ),
        ]

        SDNFallbackMetadata.swap_all_states()
        with self.assertRaises(SDNFallbackMetadata.DoesNotExist):
            with LogCapture(self.LOGGER_NAME) as log:
                SDNFallbackMetadata.swap_all_states()
                log.check_present(*expected_logs)

        self.assertEqual(len(SDNFallbackMetadata.objects.all()), 1)
        former_new_metadata = SDNFallbackMetadata.objects.filter(file_checksum=original.file_checksum)[0]
        self.assertEqual(former_new_metadata.import_state, 'Current')

    def test_swap_all_non_existent_rows(self):
        """Swapping all shouldn't break / do anything if there are no existing rows."""

        SDNFallbackMetadata.swap_all_states()
        self.assertEqual(len(SDNFallbackMetadata.objects.all()), 0)

    def test_swap_all_to_use_new_metadata_row(self):
        """
        Test what happens when we want to set the 'New' row to the 'Current' row in a
        normal scenario (e.g. when rows exist in all three import_states).
        """
        original_new = SDNFallbackMetadataFactory.create(import_state="New")
        original_current = SDNFallbackMetadataFactory.create(import_state="Current")
        original_discard = SDNFallbackMetadataFactory.create(import_state="Discard")

        SDNFallbackMetadata.swap_all_states()

        self.assertEqual(len(SDNFallbackMetadata.objects.all()), 2)

        former_new_metadata = SDNFallbackMetadata.objects.filter(
            file_checksum=original_new.file_checksum)[0]
        self.assertEqual(former_new_metadata.import_state, 'Current')
        former_current_metadata = SDNFallbackMetadata.objects.filter(
            file_checksum=original_current.file_checksum)[0]
        self.assertEqual(former_current_metadata.import_state, 'Discard')
        former_discard_metadata = SDNFallbackMetadata.objects.filter(
            file_checksum=original_discard.file_checksum)
        self.assertEqual(len(former_discard_metadata), 0)

    def test_swap_all_rollback(self):
        """
        Make sure that the rollback works if there are issues when swapping all of the rows.
        """
        original_current = SDNFallbackMetadataFactory.create(import_state="Current")
        original_discard = SDNFallbackMetadataFactory.create(import_state="Discard")

        expected_logs = [
            (
                self.LOGGER_NAME,
                'WARNING',
                "Expected a row in the 'Current' import_state after swapping, but there are none."
            ),
        ]

        with self.assertRaises(SDNFallbackMetadata.DoesNotExist):
            with LogCapture(self.LOGGER_NAME) as log:
                SDNFallbackMetadata.swap_all_states()
                log.check_present(*expected_logs)

        self.assertEqual(len(SDNFallbackMetadata.objects.all()), 2)
        former_current_metadata = SDNFallbackMetadata.objects.filter(
            file_checksum=original_current.file_checksum)[0]
        self.assertEqual(former_current_metadata.import_state, 'Current')
        former_discard_metadata = SDNFallbackMetadata.objects.filter(
            file_checksum=original_discard.file_checksum)[0]
        self.assertEqual(former_discard_metadata.import_state, 'Discard')


class SDNFallbackDataTests(TestCase):
    """
    Tests for SDNFallbackData model.
    """
    def setUp(self):
        super().setUp()
        self.sdn_metadata = SDNFallbackMetadataFactory.create(import_state="New")

    def test_fields(self):
        """ Verify all fields are correctly populated. """
        new_data = SDNFallbackData(
            sdn_fallback_metadata=self.sdn_metadata,
            source="Specially Designated Nationals (SDN) - Treasury Department",
            sdn_type="Individual",
            names="maria giuseppe",
            addresses="123 main street",
            countries="US",
        )
        new_data.full_clean()
        new_data.save()

        self.assertEqual(len(SDNFallbackData.objects.all()), 1)

        actual_data = SDNFallbackData.objects.all()[0]
        self.assertEqual(actual_data.sdn_fallback_metadata, self.sdn_metadata)
        self.assertEqual(actual_data.source, "Specially Designated Nationals (SDN) - Treasury Department")
        self.assertEqual(actual_data.sdn_type, "Individual")
        self.assertEqual(actual_data.names, "maria giuseppe")
        self.assertEqual(actual_data.addresses, "123 main street")
        self.assertEqual(actual_data.countries, "US")

    def test_data_is_deleted_on_delete_of_metadata(self):
        """ Verify SDNFallbackData object is deleted if SDNFallbackMetadata object is removed. """
        SDNFallbackDataFactory.create(
            sdn_fallback_metadata=self.sdn_metadata,
        )

        self.assertEqual(len(SDNFallbackData.objects.all()), 1)
        self.sdn_metadata.delete()
        self.assertEqual(len(SDNFallbackData.objects.all()), 0)

    def test_get_current_records_and_filter_by_source_and_type(self):
        """ Verify the query is done for current records by source and by optional sdn_type. """
        sdn_metadata_current = SDNFallbackMetadataFactory.create(import_state="Current")
        sdn_metadata_discard = SDNFallbackMetadataFactory.create(import_state="Discard")
        sdn_source = "Specially Designated Nationals (SDN) - Treasury Department"
        isn_source = "Nonproliferation Sanctions (ISN) - State Department"
        sdn_type = "Individual"

        rows = [
            [sdn_source, sdn_type, sdn_metadata_current],
            [sdn_source, "Entity", sdn_metadata_current],
            [isn_source, "", sdn_metadata_current],
            [sdn_source, sdn_type, sdn_metadata_discard],
        ]

        for row in rows:
            source, sdn_type, sdn_fallback_metadata = row
            SDNFallbackDataFactory.create(
                sdn_fallback_metadata=sdn_fallback_metadata,
                source=source,
                sdn_type=sdn_type,
            )

        filtered_records_sdn_individual = SDNFallbackData.get_current_records_and_filter_by_source_and_type(
            sdn_source, sdn_type)
        self.assertEqual(len(filtered_records_sdn_individual), 1)
        self.assertEqual(filtered_records_sdn_individual[0].sdn_fallback_metadata, sdn_metadata_current)
        filtered_records_sdn_entity = SDNFallbackData.get_current_records_and_filter_by_source_and_type(
            sdn_source, "Entity")
        self.assertEqual(len(filtered_records_sdn_entity), 1)
        filtered_records_isn = SDNFallbackData.get_current_records_and_filter_by_source_and_type(
            isn_source, "")
        self.assertEqual(len(filtered_records_isn), 1)

    def test_get_current_records_and_filter_by_source_and_type_empty_data(self):
        """ Verify that we raise the expected Exception if this is called before data is populated"""
        sdn_source = "Specially Designated Nationals (SDN) - Treasury Department"
        sdn_type = "Individual"

        with self.assertRaises(Exception):
            SDNFallbackData.get_current_records_and_filter_by_source_and_type(sdn_source, sdn_type)
