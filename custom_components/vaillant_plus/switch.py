from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import VaillantClient
from .const import DOMAIN, API_CLIENT, CONF_DID
from .discovery import async_register_discovery

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device_id = entry.data[CONF_DID]
    client: VaillantClient = hass.data[DOMAIN][API_CLIENT][entry.entry_id]

    @callback
    def discover_switch(device_attrs):
        if "Circulation_Enable" in device_attrs:
            async_add_entities([VaillantCirculationSwitch(client)])

    async_register_discovery(hass, device_id, client, discover_switch)

class VaillantCirculationSwitch(SwitchEntity):
    def __init__(self, client: VaillantClient):
        self._client = client
        self._attr_name = "Circulation Pump"
        self._attr_unique_id = f"{client.device.id}_circulation_enable"
        self._attr_is_on = None

    @property
    def is_on(self):
        val = self._client.device_attrs.get("Circulation_Enable")
        if val is None:
            return None
        return bool(val)

    async def async_turn_on(self, **kwargs):
        await self._client.control_device({"Circulation_Enable": True})
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._client.control_device({"Circulation_Enable": False})
        self._attr_is_on = False
        self.async_write_ha_state()
