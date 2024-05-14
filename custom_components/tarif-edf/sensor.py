from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)


from .coordinator import TarifEdfDataUpdateCoordinator

from .const import (
    DOMAIN,
    CONTRACT_TYPE_BASE,
    CONTRACT_TYPE_HPHC,
    CONTRACT_TYPE_TEMPO,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TarifEdfDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    sensors = []
    if coordinator.data["contract_type"] == CONTRACT_TYPE_BASE:
        sensors = [
            TarifEdfSensor(
                coordinator, "base_variable_ttc", "Tarif Base TTC", "EUR/kWh"
            ),
        ]
    elif coordinator.data["contract_type"] == CONTRACT_TYPE_HPHC:
        sensors = [
            TarifEdfSensor(
                coordinator,
                "hphc_variable_hc_ttc",
                "Tarif Heures creuses TTC",
                "EUR/kWh",
            ),
            TarifEdfSensor(
                coordinator,
                "hphc_variable_hp_ttc",
                "Tarif Heures pleines TTC",
                "EUR/kWh",
            ),
        ]
    elif coordinator.data["contract_type"] == CONTRACT_TYPE_TEMPO:
        sensors = [
            TarifEdfSensor(coordinator, "tempo_couleur", "Tarif Tempo Couleur"),
            TarifEdfSensor(
                coordinator,
                "tempo_variable_bleu_hc_ttc",
                "Tarif Tempo Bleu Heures creuses TTC",
                "EUR/kWh",
            ),
            TarifEdfSensor(
                coordinator,
                "tempo_variable_bleu_hp_ttc",
                "Tarif Tempo Bleu Heures pleines TTC",
                "EUR/kWh",
            ),
            TarifEdfSensor(
                coordinator,
                "tempo_variable_blanc_hc_ttc",
                "Tarif Tempo Blanc Heures creuses TTC",
                "EUR/kWh",
            ),
            TarifEdfSensor(
                coordinator,
                "tempo_variable_blanc_hp_ttc",
                "Tarif Tempo Blanc Heures pleines TTC",
                "EUR/kWh",
            ),
            TarifEdfSensor(
                coordinator,
                "tempo_variable_rouge_hc_ttc",
                "Tarif Tempo Rouge Heures creuses TTC",
                "EUR/kWh",
            ),
            TarifEdfSensor(
                coordinator,
                "tempo_variable_rouge_hp_ttc",
                "Tarif Tempo Rouge Heures pleines TTC",
                "EUR/kWh",
            ),
        ]

    async_add_entities(sensors, False)


class TarifEdfSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tarif EDF sensor."""

    def __init__(
        self,
        coordinator,
        coordinator_key: str,
        name: str,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize the Tarif EDF sensor."""
        super().__init__(coordinator)
        contract_name = (
            str.upper(self.coordinator.data["contract_type"])
            + " "
            + self.coordinator.data["contract_power"]
            + "kVA"
        )

        self._coordinator_key = coordinator_key
        self._name = name
        self._attr_unique_id = f"tarif_edf_{self._name}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            name=f"Tarif EDF - {contract_name}",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"Tarif EDF - {contract_name}")},
            manufacturer="Tarif EDF",
            model=contract_name,
        )
        if unit_of_measurement is not None:
            self._attr_unit_of_measurement = unit_of_measurement

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data[self._coordinator_key] is None:
            return "unavailable"
        else:
            return self.coordinator.data[self._coordinator_key]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "updated_at": self.coordinator.last_update_success_time,
            "unit_of_measurement": self._attr_unit_of_measurement,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data[self._coordinator_key] is not None
        )
