# themes/mazda_night_drive/home.py
import flet as ft

def render_home(theme, navigate_func) -> ft.Control:
    # Górny pasek statusu
    top_bar = ft.Container(
        height=55,
        padding=ft.Padding(32, 16, 32, 0),
        content=ft.Row([
            ft.Text("19:42", size=18, weight=ft.FontWeight.W_600, color=theme.text_main),
            ft.Container(expand=True),
            ft.Text("18°C", size=18, weight=ft.FontWeight.W_600, color=theme.text_main),
            ft.Container(width=16),
            ft.Icon(ft.Icons.BLUETOOTH_CONNECTED, size=20, color=theme.text_muted),
            ft.Container(width=8),
            ft.Icon(ft.Icons.WIFI, size=20, color=theme.text_muted)
        ], alignment="spaceBetween")
    )

    # Wielki panel Telemetrii na Home
    telemetry_preview = ft.Container(
        expand=True,
        bgcolor=theme.panel,
        border_radius=18,
        border=ft.Border(*[ft.BorderSide(1, theme.panel_border)]*4),
        padding=32,
        ink=True,
        on_click=lambda _: navigate_func("telemetry"),
        content=ft.Column([
            ft.Text("DRIVE", size=16, color=theme.text_muted, weight=ft.FontWeight.W_600),
            ft.Container(expand=True),
            ft.Row([
                ft.Text("72", size=92, weight=ft.FontWeight.BOLD, color=theme.text_main),
                ft.Text("km/h", size=24, color=theme.text_muted, weight=ft.FontWeight.W_500)
            ], alignment="center", vertical_alignment="baseline"),
            ft.Container(expand=True),
        ])
    )

    now_playing_preview = ft.Container(
        width=400,
        bgcolor=theme.panel,
        border_radius=18,
        border=ft.Border(*[ft.BorderSide(1, theme.panel_border)]*4),
        padding=32,
        ink=True,
        on_click=lambda _: navigate_func("bluetooth"),
        content=ft.Column([
            ft.Text("NOW PLAYING", size=14, color=theme.accent, weight=ft.FontWeight.W_600),
            ft.Container(height=16),
            ft.Text("Get Lucky", size=26, color=theme.text_main, weight=ft.FontWeight.BOLD),
            ft.Text("Daft Punk", size=18, color=theme.text_muted),
            ft.Container(expand=True),
            ft.ProgressBar(value=0.4, color=theme.accent, bgcolor=theme.bg_sec, height=4)
        ])
    )

    # Przyciski dolne
    def shortcut_btn(label, icon, app_id):
        return ft.Container(
            expand=True, height=80, bgcolor=theme.panel, border_radius=14, ink=True,
            border=ft.Border(*[ft.BorderSide(1, theme.panel_border)]*4),
            on_click=lambda _: navigate_func(app_id),
            content=ft.Row([
                ft.Icon(icon, color=theme.accent, size=28),
                ft.Container(width=12),
                ft.Text(label, size=18, color=theme.text_main, weight=ft.FontWeight.W_600)
            ], alignment="center")
        )

    shortcuts = ft.Row([
        shortcut_btn("TELEMETRY", ft.Icons.SPEED_ROUNDED, "telemetry"),
        shortcut_btn("RADIO", ft.Icons.RADIO_ROUNDED, "radio"),
        shortcut_btn("CAMERA", ft.Icons.CAMERA_ALT_ROUNDED, "manual_camera")
    ], spacing=24)

    return ft.Column([
        top_bar,
        ft.Container(
            expand=True,
            padding=ft.Padding(32, 16, 32, 24),
            content=ft.Column([
                ft.Text("Good evening", size=26, color=theme.text_main, weight=ft.FontWeight.W_600),
                ft.Container(height=16),
                ft.Row([telemetry_preview, now_playing_preview], expand=True, spacing=24),
                ft.Container(height=24),
                shortcuts
            ])
        )
    ])
