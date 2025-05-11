from enum import Enum, StrEnum
import os
import serial


SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyS0")


# Raspberry serial port config
class SerialConfig(Enum):
    PORT = SERIAL_PORT
    BAUDRATE = 1200
    PARITY = serial.PARITY_NONE
    STOPBITS = serial.STOPBITS_ONE
    BYTESIZE = serial.SEVENBITS
    TIMEOUT = 1  # seconde


class TeleinfoLabel(StrEnum):
    ADCO = "ADCO"  # Adresse du compteur
    OPTARIF = "OPTARIF"  # Option tarifaire choisie
    ISOUSC = "ISOUSC"  # Intensité souscrite
    BASE = "BASE"  # Index option Base
    HCHC = "HCHC"  # Index Heures Creuses
    HCHP = "HCHP"  # Index Heures Pleines
    EJPHN = "EJPHN"  # Index Heures Normales EJP
    EJPHPM = "EJPHPM"  # Index Heures de Pointe Mobile EJP
    BBRHCJB = "BBRHCJB"  # Heures Creuses Jours Bleus Tempo
    BBRHPJB = "BBRHPJB"  # Heures Pleines Jours Bleus Tempo
    BBRHCJW = "BBRHCJW"  # Heures Creuses Jours Blancs Tempo
    BBRHPJW = "BBRHPJW"  # Heures Pleines Jours Blancs Tempo
    BBRHCJR = "BBRHCJR"  # Heures Creuses Jours Rouges Tempo
    BBRHPJR = "BBRHPJR"  # Heures Pleines Jours Rouges Tempo
    PEJP = "PEJP"  # Préavis Début EJP (30 min)
    PTEC = "PTEC"  # Période Tarifaire en cours
    DEMAIN = "DEMAIN"  # Couleur du lendemain (Tempo)
    IINST = "IINST"  # Intensité Instantanée
    ADPS = "ADPS"  # Avertissement de Dépassement De Puissance Souscrite
    IMAX = "IMAX"  # Intensité maximale appelée
    PAPP = "PAPP"  # Puissance apparente
    HHPHC = "HHPHC"  # Horaire Heures Pleines Heures Creuses
    MOTDETAT = "MOTDETAT"  # Mot d'état du compteur


REQUIRED_TELEINFO_KEYS = [
    TeleinfoLabel.ADCO,
    TeleinfoLabel.MOTDETAT,
    TeleinfoLabel.IINST,
    TeleinfoLabel.ISOUSC,
]

FIRST_TELEINFO_FRAME_KEY = TeleinfoLabel.ADCO

UNUSED_CHARS_IN_TELEINFO = {
    "\r": "",  # Carriage Return
    "\n": "",  # New line
    "\x03": "",  # End of Text (ETX)
    "\x02": "",  # Start of Text (STX)
}

# teleinfo sample:
# b'ADCO 021728123456 @\r\n'
# b'OPTARIF HC.. <\r\n'
# b'ISOUSC 45 ?\r\n'
# b'HCHC 050977332 *\r\n'
# b'HCHP 056567645 ?\r\n'
# b'PTEC HP..  \r\n'
# b'IINST 004 [\r\n'
# b'IMAX 057 K\r\n'
# b'PAPP 00850 .\r\n'
# b'HHPHC E 0\r\n'
# b'MOTDETAT 000000 B\r\x03\x02\n'
