"""Data update coordinator for the Tarif EDF integration."""

from __future__ import annotations

from datetime import timedelta
import re
from typing import Any

import logging

import requests
import csv

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import TimestampDataUpdateCoordinator

from .const import (
    DEFAULT_REFRESH_INTERVAL,
    CONTRACT_TYPE_BASE,
    CONTRACT_TYPE_HPHC,
    CONTRACT_TYPE_TEMPO,
    TARIF_BASE_URL,
    TARIF_HPHC_URL,
    TEMPO_COLOR_API_URL,
    TEMPO_COEFF_DETAILS,
)

_LOGGER = logging.getLogger(__name__)


def get_remote_file(url: str):
    response = requests.get(url, stream=True)
    return response


class TarifEdfDataUpdateCoordinator(TimestampDataUpdateCoordinator):
    """Data update coordinator for the Tarif EDF integration."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=entry.title,
            update_interval=timedelta(days=entry.options.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)),
        )
        self.config_entry = entry

    async def _async_update_data(self) -> dict[Platform, dict[str, Any]]:
        """Get the latest data from Tarif EDF and updates the state."""
        data = self.config_entry.data
        self.data = {
            "contract_power": data["contract_power"],
            "contract_type": data["contract_type"],
        }

        if data["contract_type"] == CONTRACT_TYPE_HPHC:
            url = TARIF_HPHC_URL
        else:
            url = TARIF_BASE_URL

        response = await self.hass.async_add_executor_job(get_remote_file, url)
        parsed_content = csv.reader(response.content.decode("utf-8").splitlines(), delimiter=";")
        rows = list(parsed_content)

        base_ttc = 0.0
        for row in rows:
            if row[1] == "" and row[2] == data["contract_power"]:
                if data["contract_type"] == CONTRACT_TYPE_BASE:
                    self.data["base_fixe_ttc"] = float(row[4].replace(",", "."))
                    self.data["base_variable_ttc"] = float(row[6].replace(",", "."))
                elif data["contract_type"] == CONTRACT_TYPE_HPHC:
                    self.data["hphc_fixe_ttc"] = float(row[4].replace(",", "."))
                    self.data["hphc_variable_hc_ttc"] = float(row[6].replace(",", "."))
                    self.data["hphc_variable_hp_ttc"] = float(row[8].replace(",", "."))
                else:
                    base_ttc = float(row[6].replace(",", "."))

                break
        response.close

        if data["contract_type"] == CONTRACT_TYPE_TEMPO:
            response = await self.hass.async_add_executor_job(get_remote_file, TEMPO_COLOR_API_URL)
            tempo_color_data = response.json()
            self.data["tempo_couleur"] = TEMPO_COEFF_DETAILS[tempo_color_data["codeJour"]]["couleur"]
            self.data["tempo_variable_bleu_hc_ttc"] = base_ttc * TEMPO_COEFF_DETAILS["bleu"]["hc"]
            self.data["tempo_variable_bleu_hp_ttc"] = base_ttc * TEMPO_COEFF_DETAILS["bleu"]["hp"]
            self.data["tempo_variable_blanc_hc_ttc"] = base_ttc * TEMPO_COEFF_DETAILS["blanc"]["hc"]
            self.data["tempo_variable_blanc_hp_ttc"] = base_ttc * TEMPO_COEFF_DETAILS["blanc"]["hp"]
            self.data["tempo_variable_rouge_hc_ttc"] = base_ttc * TEMPO_COEFF_DETAILS["rouge"]["hc"]
            self.data["tempo_variable_rouge_hp_ttc"] = base_ttc * TEMPO_COEFF_DETAILS["rouge"]["hp"]

        self.logger.info(self.data)

        return self.data
