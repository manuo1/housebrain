from teleinfo.constants import (
    FIRST_TELEINFO_FRAME_KEY,
    REQUIRED_TELEINFO_KEYS,
    UNUSED_CHARS_IN_TELEINFO,
)
from core.utils.bytes_utils import decode_byte


def clean_data(data: str) -> str | None:
    """Clean unwanted characters from teleinfo data."""
    try:
        return data.translate(str.maketrans(UNUSED_CHARS_IN_TELEINFO))
    except (TypeError, AttributeError):
        return None


def split_data(cleaned_data: str) -> list[str | None, str | None, str | None]:
    """Splits the cleaned data into key, value, and checksum."""

    error_return = [None, None, None]
    if (
        not isinstance(cleaned_data, str)
        or len(cleaned_data) < 5
        or " " not in cleaned_data
    ):
        return error_return

    last_char = cleaned_data[-1]
    splitted = cleaned_data.split()
    len_splitted = len(splitted)

    # On attend len = 3 (key,value,checksum) mais parfois le checksum
    # est un espace donc split le supprime on peux donc avoir len = 2
    if len_splitted not in (2, 3):
        return error_return

    # Mais si len = 2 mais que le checksum n'est pas un espace
    if len_splitted == 2 and last_char != " ":
        return error_return

    # Si splitted a une longueur de 2 ou 3
    # key = splitted[1]
    # value = splitted[2]
    # checksum = dernier caractère de cleaned_data
    return [*splitted[:2], last_char]


def calculate_checksum(key: str, value: str) -> str | None:
    """
    La "checksum" est calculée sur l'ensemble des caractères allant du début
    du champ étiquette à la fin du champ donnée, caractère SP inclus.
    On fait tout d'abord la somme des codes ASCII de tous ces caractères.
    Pour éviter d'introduire des fonctions ASCII (00 à 1F en hexadécimal),
    on ne conserve que les six bits de poids faible du résultat obtenu
    (cette opération se traduit par un ET logique entre la somme précédemment
    calculée et 03Fh). Enfin, on ajoute 20 en hexadécimal.
    Le résultat sera donc toujours un caractère ASCII imprimable
    (signe, chiffre, lettre majuscule) allant de 20 à 5F en Hexadécimal.

    !!! 20 est le caractère espace !!!
    """
    if not all(isinstance(var, str) for var in (key, value)) or not all([key, value]):
        return None

    data = key + " " + value
    # Calculer la somme des codes ASCII des caractères de key et value
    ascii_sum = sum(ord(c) for c in data)
    # Conserver les 6 bits de poids faible
    low_6_bits = ascii_sum & 0x3F
    # Ajouter 20 en hexadécimal
    checksum = low_6_bits + 0x20
    return chr(checksum)


def data_is_valid(key: str, value: str, checksum: str) -> bool:
    """compare calculated checksum with extracted checksum"""
    if not all(isinstance(var, str) for var in (key, value, checksum)):
        return False
    return calculate_checksum(key, value) == checksum


def get_data_in_line(byte_data: bytes) -> tuple[str | None, str | None]:
    """extract data from raw data line"""
    str_data = decode_byte(byte_data)
    cleaned_data = clean_data(str_data)
    key, value, checksum = split_data(cleaned_data)
    if data_is_valid(key, value, checksum):
        return (key, value)
    return (None, None)


def buffer_can_accept_new_data(key: str, buffer: dict[str, str]) -> bool:
    """Check if data can be added in buffer"""
    if not isinstance(buffer, dict) or not isinstance(key, str):
        return False

    return (
        # on ne peut commencer à écrire dans le buffer qu'en début de trame donc si
        # le buffer est vide et que la clé est la première attendue dans la trame
        (not buffer and key == FIRST_TELEINFO_FRAME_KEY)
        # ou la première clé attendue dans la trame est déjà présente dans le buffer
        or FIRST_TELEINFO_FRAME_KEY in buffer.keys()
    )


def buffer_is_complete(buffer: dict[str, str]) -> bool:
    """Check if all required key are in the buffer"""
    if not isinstance(buffer, dict):
        return False
    return all(key in buffer for key in REQUIRED_TELEINFO_KEYS)
