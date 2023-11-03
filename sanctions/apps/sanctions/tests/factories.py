from datetime import datetime, timedelta

import factory
from faker import Faker

from sanctions.apps.sanctions.models import SanctionsFallbackData, SanctionsFallbackMetadata

class SanctionsFallbackMetadataFactory(factory.DjangoModelFactory):
    class Meta:
        model = SanctionsFallbackMetadata

    file_checksum = factory.Sequence(lambda n: Faker().md5())
    import_state = 'New'
    download_timestamp = datetime.now() - timedelta(days=10)


class SanctionsFallbackDataFactory(factory.DjangoModelFactory):
    class Meta:
        model = SanctionsFallbackData

    sdn_fallback_metadata = factory.SubFactory(SanctionsFallbackMetadataFactory)
    source = "Specially Designated Nationals (SDN) - Treasury Department"
    sdn_type = "Individual"
    names = factory.Faker('name')
    addresses = factory.Faker('address')
    countries = factory.Faker('country_code')