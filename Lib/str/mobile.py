"""
Star Language Mobile & Hardware Subsystem
Android WallpaperManager Bridge, Haptic Feedback & Google Play Billing Interop.
Specification & Architecture for Star Language & Haven Unified Ecosystem.
"""

from typing import Any, Dict, List, Optional, Callable


class AndroidWallpaperService:
    """Android WallpaperManager JNI / IPC System Bridge."""
    FLAG_SYSTEM = 1      # Home Screen
    FLAG_LOCK = 2        # Lock Screen
    FLAG_BOTH = 3        # Both Home and Lock Screen

    _home_wallpaper: str = "Default Star Horizon"
    _lock_wallpaper: str = "Default Star Nebula"
    _applied_count: int = 0
    _history: List[Dict[str, Any]] = []

    @classmethod
    def setWallpaper(cls, wallpaper_target: str, target_flag: int = FLAG_SYSTEM) -> bool:
        if target_flag == cls.FLAG_SYSTEM:
            cls._home_wallpaper = wallpaper_target
            dest = "Home Screen"
        elif target_flag == cls.FLAG_LOCK:
            cls._lock_wallpaper = wallpaper_target
            dest = "Lock Screen"
        else:
            cls._home_wallpaper = wallpaper_target
            cls._lock_wallpaper = wallpaper_target
            dest = "Home & Lock Screens"

        cls._applied_count += 1
        cls._history.append({
            "target": wallpaper_target,
            "flag": target_flag,
            "destination": dest,
            "index": cls._applied_count
        })
        return True

    @classmethod
    def getHomeScreenWallpaper(cls) -> str:
        return cls._home_wallpaper

    @classmethod
    def getLockScreenWallpaper(cls) -> str:
        return cls._lock_wallpaper

    @classmethod
    def getAppliedCount(cls) -> int:
        return cls._applied_count

    @classmethod
    def getHistory(cls) -> List[Dict[str, Any]]:
        return list(cls._history)


class AndroidHapticService:
    """Android Haptic Feedback & Vibrator Bridge."""
    _last_vibration_ms: int = 0
    _vibration_count: int = 0

    @classmethod
    def vibrate(cls, duration_ms: int = 25) -> bool:
        cls._last_vibration_ms = duration_ms
        cls._vibration_count += 1
        return True

    @classmethod
    def impact(cls, style: str = "medium") -> bool:
        durations = {"light": 15, "medium": 30, "heavy": 60}
        return cls.vibrate(durations.get(style, 25))

    @classmethod
    def selectionClick(cls) -> bool:
        return cls.vibrate(10)


class _SensorHardware:
    _listeners: List[Callable] = []

    @classmethod
    def listenGyroscope(cls, callback: Callable[[float, float, float], None]):
        cls._listeners.append(callback)
        # Emit initial calibrated event
        callback(0.0, 0.0, 0.0)
        return callback

    @classmethod
    def emitGyro(cls, pitch: float, roll: float, yaw: float):
        for cb in cls._listeners:
            cb(pitch, roll, yaw)


class _HapticsHardware:
    @classmethod
    def vibrate(cls, ms: int = 25):
        return AndroidHapticService.vibrate(ms)


class _BatteryHardware:
    @classmethod
    def level(cls) -> int:
        return 100

    @classmethod
    def isCharging(cls) -> bool:
        return True


class _ClipboardHardware:
    _clip_text: str = ""

    @classmethod
    def setText(cls, text: str):
        cls._clip_text = text

    @classmethod
    def getText(cls) -> str:
        return cls._clip_text


class _HardwareSubsystem:
    Sensor = _SensorHardware
    Haptics = _HapticsHardware
    Battery = _BatteryHardware
    Clipboard = _ClipboardHardware


class Mobile:
    """Unified Native Mobile Platform & Hardware Bridge."""
    Hardware = _HardwareSubsystem


class GoogleBillingClient:
    """Google Play BillingClient v7.0.0 Interop Subsystem."""
    _connected: bool = True
    _active_subs: List[str] = []
    _purchased_products: List[str] = []

    @classmethod
    def connect(cls) -> bool:
        cls._connected = True
        return True

    @classmethod
    def isConnected(cls) -> bool:
        return cls._connected

    @classmethod
    def purchase(cls, sku: str) -> bool:
        if "monthly" in sku or "yearly" in sku or "vip" in sku:
            cls._active_subs.append(sku)
        else:
            cls._purchased_products.append(sku)
        return True

    @classmethod
    def isSubscribed(cls, sku: str) -> bool:
        return sku in cls._active_subs

    @classmethod
    def hasPurchased(cls, sku: str) -> bool:
        return sku in cls._purchased_products
