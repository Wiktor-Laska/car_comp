from dataclasses import dataclass

@dataclass
class AppTheme:
    """Kontrakt wymuszający na każdym motywie te same zmienne kolorystyczne."""
    name: str
    bg_base: str
    bg_panel: str
    bg_panel_active: str
    text_main: str
    text_muted: str
    accent: str
    danger: str
    success: str
    assets_path: str
