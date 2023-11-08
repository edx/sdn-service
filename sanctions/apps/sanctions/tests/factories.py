"""
Factoryboy factories for Sanctions app.
"""
import logging

import factory
from django.utils import timezone
from faker import Faker

from sanctions.apps.sanctions.models import SDNFallbackData, SDNFallbackMetadata

# Silence faker locale warnings
logging.getLogger("faker").setLevel(logging.ERROR)


class SDNFallbackMetadataFactory(factory.django.DjangoModelFactory):
    """
    Test factory for the `SDNFallbackMetadata` model.
    """
    file_checksum = factory.Sequence(lambda n: Faker().md5())
    import_state = 'New'
    download_timestamp = timezone.now() - timezone.timedelta(days=10)

    class Meta:
        model = SDNFallbackMetadata


class SDNFallbackDataFactory(factory.django.DjangoModelFactory):
    """
    Test factory for the `SDNFallbackData` model.
    """
    sdn_fallback_metadata = factory.SubFactory(SDNFallbackMetadataFactory)
    source = "Specially Designated Nationals (SDN) - Treasury Department"
    sdn_type = "Individual"
    names = factory.Faker('name')
    addresses = factory.Faker('address')
    countries = factory.Faker('country_code')

    class Meta:
        model = SDNFallbackData
