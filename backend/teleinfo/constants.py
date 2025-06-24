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


class ReadableLabel(StrEnum):
    TH = "Toutes les Heures"
    HC = "Heures Creuses"
    HP = "Heures Pleines"
    HN = "Heures Normales"
    PM = "Heures de Pointe Mobile"
    HCJB = "Heures Creuses Jours Bleus"
    HCJW = "Heures Creuses Jours Blancs"
    HCJR = "Heures Creuses Jours Rouges"
    HPJB = "Heures Pleines Jours Bleus"
    HPJW = "Heures Pleines Jours Blancs"
    HPJR = "Heures Pleines Jours Rouges"


TELEINFO_LABEL_TRANSLATIONS = {
    TeleinfoLabel.ADCO: "Adresse du compteur",
    TeleinfoLabel.OPTARIF: "Option tarifaire choisie",
    TeleinfoLabel.ISOUSC: "Intensité souscrite",
    TeleinfoLabel.BASE: "Index option Base",
    TeleinfoLabel.HCHC: "Index Heures Creuses",
    TeleinfoLabel.HCHP: "Index Heures Pleines",
    TeleinfoLabel.EJPHN: "Index Heures Normales EJP",
    TeleinfoLabel.EJPHPM: "Index Heures de Pointe Mobile EJP",
    TeleinfoLabel.BBRHCJB: "Heures Creuses Jours Bleus Tempo",
    TeleinfoLabel.BBRHPJB: "Heures Pleines Jours Bleus Tempo",
    TeleinfoLabel.BBRHCJW: "Heures Creuses Jours Blancs Tempo",
    TeleinfoLabel.BBRHPJW: "Heures Pleines Jours Blancs Tempo",
    TeleinfoLabel.BBRHCJR: "Heures Creuses Jours Rouges Tempo",
    TeleinfoLabel.BBRHPJR: "Heures Pleines Jours Rouges Tempo",
    TeleinfoLabel.PEJP: "Préavis Début EJP (30 min)",
    TeleinfoLabel.PTEC: "Période Tarifaire en cours",
    TeleinfoLabel.DEMAIN: "Couleur du lendemain (Tempo)",
    TeleinfoLabel.IINST: "Intensité Instantanée",
    TeleinfoLabel.ADPS: "Avertissement Dépassement Puissance Souscrite",
    TeleinfoLabel.IMAX: "Intensité maximale appelée",
    TeleinfoLabel.PAPP: "Puissance apparente",
    TeleinfoLabel.HHPHC: "Horaire Heures Pleines Heures Creuses",
    TeleinfoLabel.MOTDETAT: "Mot d'état du compteur",
}

TELEINFO_INDEX_LABELS = [
    TeleinfoLabel.BASE,
    TeleinfoLabel.HCHC,
    TeleinfoLabel.HCHP,
    TeleinfoLabel.EJPHN,
    TeleinfoLabel.EJPHPM,
    TeleinfoLabel.BBRHCJB,
    TeleinfoLabel.BBRHPJB,
    TeleinfoLabel.BBRHCJW,
    TeleinfoLabel.BBRHPJW,
    TeleinfoLabel.BBRHCJR,
    TeleinfoLabel.BBRHPJR,
]


REQUIRED_TELEINFO_KEYS = [
    TeleinfoLabel.ADCO,
    TeleinfoLabel.MOTDETAT,
    TeleinfoLabel.IINST,
    TeleinfoLabel.ISOUSC,
    TeleinfoLabel.PAPP,
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

# Connaître la puissance souscrite du contrat grace au champ ISOUC de la teleinfo
ISOUC_TO_SUBSCRIBED_POWER = {
    # A : kva
    "15": 3,
    "30": 6,
    "45": 9,
    "60": 12,
    "90": 15,
}


class TarifPeriods(StrEnum):
    TH = "TH.."  # Toutes les Heures (option Base)
    HC = "HC.."  # Heures Creuses
    HP = "HP.."  # Heures Pleines
    HN = "HN.."  # Heures Normales (option EJP)
    PM = "PM.."  # Heures de Pointe Mobile (option EJP)
    HCJB = "HCJB"  # Heures Creuses Jours Bleus (option Tempo)
    HCJW = "HCJW"  # Heures Creuses Jours Blancs (option Tempo)
    HCJR = "HCJR"  # Heures Creuses Jours Rouges (option Tempo)
    HPJB = "HPJB"  # Heures Pleines Jours Bleus (option Tempo)
    HPJW = "HPJW"  # Heures Pleines Jours Blancs (option Tempo)
    HPJR = "HPJR"  # Heures Pleines Jours Rouges (option Tempo)


TARIF_PERIODS_TRANSLATIONS = {
    TarifPeriods.TH: ReadableLabel.TH,
    TarifPeriods.HC: ReadableLabel.HC,
    TarifPeriods.HP: ReadableLabel.HP,
    TarifPeriods.HN: ReadableLabel.HN,
    TarifPeriods.PM: ReadableLabel.PM,
    TarifPeriods.HCJB: ReadableLabel.HCJB,
    TarifPeriods.HCJW: ReadableLabel.HCJW,
    TarifPeriods.HCJR: ReadableLabel.HCJR,
    TarifPeriods.HPJB: ReadableLabel.HPJB,
    TarifPeriods.HPJW: ReadableLabel.HPJW,
    TarifPeriods.HPJR: ReadableLabel.HPJR,
}

INDEX_LABEL_TRANSLATIONS = {
    TeleinfoLabel.BASE: ReadableLabel.TH,
    TeleinfoLabel.HCHC: ReadableLabel.HC,
    TeleinfoLabel.HCHP: ReadableLabel.HP,
    TeleinfoLabel.EJPHN: ReadableLabel.HN,
    TeleinfoLabel.EJPHPM: ReadableLabel.PM,
    TeleinfoLabel.BBRHCJB: ReadableLabel.HCJB,
    TeleinfoLabel.BBRHCJW: ReadableLabel.HCJW,
    TeleinfoLabel.BBRHCJR: ReadableLabel.HCJR,
    TeleinfoLabel.BBRHPJB: ReadableLabel.HPJB,
    TeleinfoLabel.BBRHPJW: ReadableLabel.HPJW,
    TeleinfoLabel.BBRHPJR: ReadableLabel.HPJR,
}


TARIF_PERIOD_LABEL_TO_INDEX_LABEL = {
    TarifPeriods.TH: TeleinfoLabel.BASE,
    TarifPeriods.HC: TeleinfoLabel.HCHC,
    TarifPeriods.HP: TeleinfoLabel.HCHP,
    TarifPeriods.HN: TeleinfoLabel.EJPHN,
    TarifPeriods.PM: TeleinfoLabel.EJPHPM,
    TarifPeriods.HCJB: TeleinfoLabel.BBRHCJB,
    TarifPeriods.HCJW: TeleinfoLabel.BBRHCJW,
    TarifPeriods.HCJR: TeleinfoLabel.BBRHCJR,
    TarifPeriods.HPJB: TeleinfoLabel.BBRHPJB,
    TarifPeriods.HPJW: TeleinfoLabel.BBRHPJW,
    TarifPeriods.HPJR: TeleinfoLabel.BBRHPJR,
}

INDEX_LABEL_TO_TARIF_PERIOD_LABEL = {
    TeleinfoLabel.BASE: TarifPeriods.TH,
    TeleinfoLabel.HCHC: TarifPeriods.HC,
    TeleinfoLabel.HCHP: TarifPeriods.HP,
    TeleinfoLabel.EJPHN: TarifPeriods.HN,
    TeleinfoLabel.EJPHPM: TarifPeriods.PM,
    TeleinfoLabel.BBRHCJB: TarifPeriods.HCJB,
    TeleinfoLabel.BBRHCJW: TarifPeriods.HCJW,
    TeleinfoLabel.BBRHCJR: TarifPeriods.HCJR,
    TeleinfoLabel.BBRHPJB: TarifPeriods.HPJB,
    TeleinfoLabel.BBRHPJW: TarifPeriods.HPJW,
    TeleinfoLabel.BBRHPJR: TarifPeriods.HPJR,
}
