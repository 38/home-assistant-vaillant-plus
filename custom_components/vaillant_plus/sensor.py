"""Vaillant sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.const import (
    UnitOfTemperature
)

from .client import VaillantClient
from .const import CONF_DID, DISPATCHERS, DOMAIN, EVT_DEVICE_CONNECTED, API_CLIENT
from .entity import VaillantEntity

_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS = (

	SensorEntityDescription(
        key="water_pressure",
        name="供暖水压",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement="bar",
    ),
    SensorEntityDescription(
        key="Room_Temperature_Setpoint_Comfort",
        name="舒适模式温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Room_Temperature_Setpoint_ECO",
        name="经济模式温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Room_Temperature",
        name="房间温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="DHW_readSetPoint",
        name="Domestic hot water read setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Current_DHW_Setpoint",
        name="当前热水温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
	SensorEntityDescription(
        key="indoor_temperature",
        name="室内温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Tank_temperature",
        name="水箱温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Outdoor_Temperature",
        name="室外温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="DHW_setpoint",
        name="生活热水设置温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Lower_Limitation_of_CH_Setpoint",
        name="暖气最小设置温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Upper_Limitation_of_CH_Setpoint",
        name="暖气最大设置温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Lower_Limitation_of_DHW_Setpoint",
        name="生活热水最小设置温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Upper_Limitation_of_DHW_Setpoint",
        name="生活热水最大设置温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Flow_Temperature_Setpoint",
        name="暖气设置温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Flow_temperature",
        name="供暖出水温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="return_temperature",
        name="供暖回水温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
      native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="Mode_Setting_CH",
        name="暖气模式设置",
    ),

     SensorEntityDescription(
        key="Heating_System_Setting",
        name="供暖系统设置",
    ),
      SensorEntityDescription(
        key="burn_status",
        name="燃烧器状态",
    ),
    SensorEntityDescription(
        key="gas_ch_consumption_today",
        name="今日燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_ch_consumption_yesterday",
        name="昨日燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_ch_consumption_monthly",
        name="月度燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_ch_consumption_yearly",
        name="年度燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_dhw_consumption_today",
        name="今日热水燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_dhw_consumption_yesterday",
        name="昨日热水燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_dhw_consumption_monthly",
        name="月度热水燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_dhw_consumption_yearly",
        name="年度热水燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="gas_consumption",
        name="总燃气消耗",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="CH_workTime",
        name="壁挂炉工作时间",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="CH_startTimes",
        name="壁挂炉开启次数",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="DHW_workTime",
        name="热水器工作时间",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="DHW_startTimes",
        name="热水器工作次数",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="CH_power",
        name="壁挂炉功率",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="DHW_power",
        name="热水器功率",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Heating_Curve",
        name="加热曲线",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="pump_status",
        name="水泵状态",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="fan_status",
        name="风扇状态",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="fan_speed",
        name="风扇速度",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="ebus_status",
        name="eBUS状态",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="modbus_status",
        name="Modbus状态",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="WiFi_RSSI",
        name="Wi-Fi RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="maintainence_remainTime",
        name="下次保养时间",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Fault_List_1",
        name="Fault list 1",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Fault_List_2",
        name="Fault list 2",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Fault_List_3",
        name="Fault list 3",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Fault_List_4",
        name="Fault list 4",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Fault_List_5",
        name="Fault list 5",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Gateway_Fault_List_1",
        name="Gateway fault list 1",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Gateway_Fault_List_2",
        name="Gateway fault list 2",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Gateway_Fault_List_3",
        name="Gateway fault list 3",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Gateway_Fault_List_4",
        name="Gateway fault list 4",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Gateway_Fault_List_5",
        name="Gateway fault list 5",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> bool:
    """Set up Vaillant sensors."""
    device_id = entry.data.get(CONF_DID)
    client: VaillantClient = hass.data[DOMAIN][API_CLIENT][
        entry.entry_id
    ]

    added_entities = []

    @callback
    def async_new_entities(device_attrs: dict[str, Any]):
        _LOGGER.debug("add vaillant sensor entities. device attrs: %s", device_attrs)
        new_entities = []
        for description in SENSOR_DESCRIPTIONS:
            if (
                description.key in device_attrs
                and description.key not in added_entities
            ):
                new_entities.append(VaillantSensorEntity(client, description))
                added_entities.append(description.key)

        if len(new_entities) > 0:
            async_add_entities(new_entities)

    unsub = async_dispatcher_connect(
        hass, EVT_DEVICE_CONNECTED.format(device_id), async_new_entities
    )

    hass.data[DOMAIN][DISPATCHERS][device_id].append(unsub)

    return True


class VaillantSensorEntity(VaillantEntity, SensorEntity):
    """Define a Vaillant sensor entity."""

    def __init__(
        self,
        client: VaillantClient,
        description: SensorEntityDescription,
    ):
        super().__init__(client)
        self.entity_description = description

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return f"{self.device.id}_{self.entity_description.key}"

    @callback
    def update_from_latest_data(self, data: dict[str, Any]) -> None:
        """Update the entity from the latest data."""
        if self.entity_description.key not in data:
            return

        if(self.entity_description.key in data):
          value = data.get(self.entity_description.key)
          self._attr_native_value = value
          self._attr_available = value is not None
          self.async_schedule_update_ha_state(True)
