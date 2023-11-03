"""
Helpers for the sanctions app.
"""
import re
import unicodedata

from sanctions.apps.sanctions.models import SanctionsFallbackData


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
