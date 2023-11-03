"""
Helpers for the sanctions app.
"""
import csv
import hashlib
import io
import logging
import re
import unicodedata
from datetime import datetime, timezone

import pycountry

from sanctions.apps.sanctions.models import SanctionsFallbackData, SanctionsFallbackMetadata

logger = logging.getLogger(__name__)
COUNTRY_CODES = {country.alpha_2 for country in pycountry.countries}


def checkSDNFallback(name, city, country):
    """
    Performs an SDN check against the SanctionsFallbackData.

    First, filter the SanctionsFallbackData records by source, type and country.
    Then, compare the provided name/city against each record and return whether we find a match.
    The check uses the following properties:
    1. Order of words doesn’t matter
    2. Number of times that a given word appears doesn’t matter
    3. Punctuation between words or at the beginning/end of a given word doesn’t matter
    4. If a subset of words match, it still counts as a match
    5. Capitalization doesn’t matter
    """
    hit_count = 0
    records = SanctionsFallbackData.get_current_records_and_filter_by_source_and_type(
        'Specially Designated Nationals (SDN) - Treasury Department', 'Individual'
    )
    records = records.filter(countries__contains=country)
    processed_name, processed_city = process_text(name), process_text(city)
    for record in records:
        record_names, record_addresses = set(record.names.split()), set(record.addresses.split())
        if (processed_name.issubset(record_names) and processed_city.issubset(record_addresses)):
            hit_count = hit_count + 1
    return hit_count


def transliterate_text(text):
    """
    Transliterate unicode characters into ASCII (such as accented characters into non-accented characters).

    This works by decomposing accented characters into the letter and the accent.

    The subsequent ASCII encoding drops any accents and leaves the original letter.

    Returns the original string if no transliteration is available.

    Args:
        text (str): a string to be transliterated

    Returns:
        text (str): the transliterated string
    """
    t11e_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return t11e_text if t11e_text else text


def process_text(text):
    """
    Lowercase, remove non-alphanumeric characters, and ignore order and word frequency.
    Attempts to transliterate unicode characters into ASCII (such as accented characters into non-accented characters).

    Args:
        text (str): names or addresses from the SDN list to be processed

    Returns:
        text (set): processed text
    """
    if len(text) == 0:
        return ''

    # Make lowercase
    text = text.casefold()

    # Transliterate numbers and letters
    text = ''.join(map(transliterate_text, text))

    # Ignore punctuation, order, and word frequency
    text = set(filter(None, set(re.split(r'[\W_]+', text))))

    return text


def extract_country_information(addresses, ids):
    """
    Extract any country codes that are present, if any, in the addresses and ids fields

    Args:
        addresses (str): addresses from the csv addresses field
        ids (str): ids from the csv ids field

    Returns:
        countries (str): Space separated list of alpha_2 country codes present in the addresses and ids fields
    """
    country_matches = []
    if addresses:
        # Addresses are stored in a '; ' separated format with the country at the end of each address
        # We check for two uppercase letters followed by '; ' or at the end of the string
        addresses_regex = r'([A-Z]{2})$|([A-Z]{2});'
        country_matches += re.findall(addresses_regex, addresses)
    if ids:
        # Ids are stored in a '; ' separated format with the country at the beginning of each id
        # Countries within the id are followed by a comma
        # We check for two uppercase letters prefaced by '; ' or at the beginning of a string
        # Notes are also stored in this field in sentence case, so checking for two uppercase letters handles this
        ids_regex = r'^([A-Z]{2}),|; ([A-Z]{2}),'
        country_matches += re.findall(ids_regex, ids)
    # country_matches is returned in the following format [('', 'IQ'), ('', 'JO'), ('', 'IQ'), ('', 'TR')]
    # We filter out regex groups with no match, deduplicate countries, and convert them to a space separated string
    # with the following format 'IQ JO TR'
    country_codes = {' '.join(tuple(filter(None, x))) for x in country_matches}
    valid_country_codes = COUNTRY_CODES.intersection(country_codes)
    formatted_countries = ' '.join(valid_country_codes)
    return formatted_countries


def populate_sdn_fallback_metadata(sdn_csv_string):
    """
    Insert a new SanctionsFallbackMetadata entry if the new csv differs from the current one

    Args:
        sdn_csv_string (bytes): Bytes of the sdn csv

    Returns:
        sdn_fallback_metadata_entry (SanctionsFallbackMetadata): Instance of the current SanctionsFallbackMetadata class
        or None if none exists
    """
    file_checksum = hashlib.sha256(sdn_csv_string.encode('utf-8')).hexdigest()
    metadata_entry = SanctionsFallbackMetadata.insert_new_sdn_fallback_metadata_entry(file_checksum)
    return metadata_entry


def populate_sdn_fallback_data(sdn_csv_string, metadata_entry):
    """
    Process CSV data and create SanctionsFallbackData records

    Args:
        sdn_csv_string (str): String of the sdn csv
        metadata_entry (SanctionsFallbackMetadata): Instance of the current SanctionsFallbackMetadata class
    """
    sdn_csv_reader = csv.DictReader(io.StringIO(sdn_csv_string))
    processed_records = []
    for row in sdn_csv_reader:
        sdn_source, sdn_type, names, addresses, alt_names, ids = (
            row['source'] or '', row['type'] or '', row['name'] or '',
            row['addresses'] or '', row['alt_names'] or '', row['ids'] or ''
        )
        processed_names = ' '.join(process_text(' '.join(filter(None, [names, alt_names]))))
        processed_addresses = ' '.join(process_text(addresses))
        countries = extract_country_information(addresses, ids)
        processed_records.append(SanctionsFallbackData(
            sanctions_fallback_metadata=metadata_entry,
            source=sdn_source,
            sdn_type=sdn_type,
            names=processed_names,
            addresses=processed_addresses,
            countries=countries
        ))
    # Bulk create should be more efficient for a few thousand records without needing to use SQL directly.
    SanctionsFallbackData.objects.bulk_create(processed_records)


def populate_sdn_fallback_data_and_metadata(sdn_csv_string):
    """
    1. Create the SanctionsFallbackMetadata entry
    2. Populate the SanctionsFallbackData from the csv

    Args:
        sdn_csv_string (str): String of the sdn csv
    """
    metadata_entry = populate_sdn_fallback_metadata(sdn_csv_string)
    if metadata_entry:
        populate_sdn_fallback_data(sdn_csv_string, metadata_entry)
        # Once data is successfully imported, update the metadata import timestamp and state
        now = datetime.now(timezone.utc)
        metadata_entry.import_timestamp = now
        metadata_entry.save()
        metadata_entry.swap_all_states()
    return metadata_entry
