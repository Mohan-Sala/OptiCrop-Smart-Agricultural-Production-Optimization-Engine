import abc
from typing import Dict, Any, List
from app.utils.exceptions import ValidationException


class ExternalTelemetryProvider(abc.ABC):
    """Abstract plugin interface for external telemetry providers (Weather, IoT)."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def validate(self, raw_data: Dict[str, Any]) -> None:
        pass

    @abc.abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def metadata(self) -> Dict[str, Any]:
        pass


class WeatherAPIProvider(ExternalTelemetryProvider):
    @property
    def name(self) -> str:
        return "WeatherAPI"

    def validate(self, raw_data: Dict[str, Any]) -> None:
        if "temperature" not in raw_data and "temp" not in raw_data:
            raise ValidationException("Missing temperature field in weather payload.")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        temp = raw_data.get("temperature") or raw_data.get("temp", 0.0)
        humidity = raw_data.get("humidity", 50.0)
        return {
            "temperature": float(temp),
            "humidity": float(humidity),
            "moisture": None,
        }

    def metadata(self) -> Dict[str, Any]:
        return {"precision": "hourly", "source": "openweather"}


class IoTSensorsProvider(ExternalTelemetryProvider):
    @property
    def name(self) -> str:
        return "IoTSensors"

    def validate(self, raw_data: Dict[str, Any]) -> None:
        if "moisture" not in raw_data and "soil_moisture" not in raw_data:
            raise ValidationException("Missing moisture field in IoT payload.")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        moisture = raw_data.get("moisture") or raw_data.get("soil_moisture", 0.0)
        temp = raw_data.get("temperature") or raw_data.get("temp")
        return {
            "temperature": float(temp) if temp is not None else None,
            "humidity": None,
            "moisture": float(moisture),
        }

    def metadata(self) -> Dict[str, Any]:
        return {"precision": "realtime", "sensor_type": "capacitive"}


class SatelliteNDVIProvider(ExternalTelemetryProvider):
    @property
    def name(self) -> str:
        return "SatelliteNDVI"

    def validate(self, raw_data: Dict[str, Any]) -> None:
        if "ndvi" not in raw_data:
            raise ValidationException("Missing ndvi index value.")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ndvi": float(raw_data.get("ndvi", 0.0)),
            "evi": float(raw_data.get("evi")) if raw_data.get("evi") is not None else None,
        }

    def metadata(self) -> Dict[str, Any]:
        return {"sat": "Sentinel-2"}


class TelemetryProviderRegistry:
    """Registry loading external telemetry providers plugins."""

    def __init__(self):
        self._providers: Dict[str, ExternalTelemetryProvider] = {}
        # Auto-register defaults
        self.register(WeatherAPIProvider())
        self.register(IoTSensorsProvider())
        self.register(SatelliteNDVIProvider())

    def register(self, provider: ExternalTelemetryProvider) -> None:
        self._providers[provider.name.lower()] = provider

    def get(self, name: str) -> ExternalTelemetryProvider:
        prov = self._providers.get(name.lower())
        if not prov:
            raise KeyError(f"Unsupported telemetry provider: '{name}'")
        return prov

    def list_registered(self) -> List[str]:
        return list(self._providers.keys())
