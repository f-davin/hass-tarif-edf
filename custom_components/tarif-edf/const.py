"""Constants for the Tarif EDF integration."""

from homeassistant.const import Platform

DOMAIN = "tarif_edf"

CONTRACT_TYPE_BASE = "base"
CONTRACT_TYPE_HPHC = "hphc"
CONTRACT_TYPE_TEMPO = "tempo"

TARIF_BASE_URL = "https://www.data.gouv.fr/fr/datasets/r/c13d05e5-9e55-4d03-bf7e-042a2ade7e49"
TARIF_HPHC_URL = "https://www.data.gouv.fr/fr/datasets/r/f7303b3a-93c7-4242-813d-84919034c416"

TEMPO_COLOR_API_URL = "https://www.api-couleur-tempo.fr/api/jourTempo/today"

TEMPO_COEFF_DETAILS = {
    1: {"couleur": "bleu", "hc": 0.51510333863275, "hp": 0.639507154213037},
    2: {"couleur": "blanc", "hc": 0.590620031796502, "hp": 0.752782193958665},
    3: {"couleur": "rouge", "hc": 0.623211446740858, "hp": 3.00556438791733},
}

DEFAULT_REFRESH_INTERVAL = 1

PLATFORMS = [Platform.SENSOR]
