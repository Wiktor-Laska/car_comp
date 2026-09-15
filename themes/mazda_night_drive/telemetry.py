# themes/mazda_night_drive/telemetry.py
import math
import flet as ft
import flet.canvas as cv
from core.state import AppState

def render_telemetry(theme, state: AppState, update_speed_func, update_rpm_func) -> ft.Control:

    class MazdaPulseGauge(ft.Container):
        def __init__(self, current_speed: float, current_rpm: float):
            super().__init__()
            self.max_speed = 220.0
            self.max_rpm = 6500.0

            # Główny tekst prędkości (środek)
            self.speed_text = ft.Text(str(int(current_speed)), size=88, weight=ft.FontWeight.BOLD, color=theme.text_main)

            # Łuk prędkości (Gap u góry. Start od -45 stopni (-pi/4), rysuje 270 stopni zgodnie z zegarem)
            self.bg_arc = cv.Arc(x=0, y=0, width=320, height=320, start_angle=-math.pi/4, sweep_angle=1.5 * math.pi,
                                 paint=ft.Paint(color=theme.panel_border, stroke_width=12, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.ROUND))
            self.val_arc = cv.Arc(x=0, y=0, width=320, height=320, start_angle=-math.pi/4, sweep_angle=self._calc_sweep(current_speed),
                                  paint=ft.Paint(color=theme.text_main, stroke_width=12, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.ROUND))

            # Pasek RPM (Engine Pulse)
            self.rpm_bar_bg = ft.Container(width=600, height=8, bgcolor=theme.panel_border, border_radius=4)
            self.rpm_bar_fg = ft.Container(width=self._calc_rpm_width(current_rpm), height=8, bgcolor=self._get_rpm_color(current_rpm), border_radius=4)

            self.rpm_text = ft.Text(f"{int(current_rpm):,} RPM", size=22, color=theme.text_muted, weight=ft.FontWeight.W_600)

            self.content = ft.Column([
                # Górna sekcja - Prędkość
                ft.Container(
                    width=340, height=340,
                    content=ft.Stack([
                        cv.Canvas([self.bg_arc, self.val_arc], width=320, height=320),
                        ft.Container(
                            content=ft.Column([
                                self.speed_text,
                                ft.Text("km/h", size=20, color=theme.text_muted, weight=ft.FontWeight.W_600)
                            ], alignment="center", horizontal_alignment="center", spacing=-10),
                            alignment=ft.Alignment(0, 0)
                        )
                    ])
                ),
                ft.Container(height=40),
                # Dolna sekcja - Engine Pulse (RPM)
                ft.Column([
                    ft.Row([
                        ft.Text("0", size=14, color=theme.text_muted),
                        ft.Container(expand=True),
                        ft.Text("4k", size=14, color=theme.text_muted),
                        ft.Container(expand=True),
                        ft.Text("6500", size=14, color=theme.danger, weight=ft.FontWeight.BOLD),
                    ], width=600),
                    ft.Stack([self.rpm_bar_bg, self.rpm_bar_fg], width=600, height=8),
                    ft.Container(height=10),
                    self.rpm_text
                ], horizontal_alignment="center", spacing=4)
            ], horizontal_alignment="center")

        def _calc_sweep(self, speed):
            clamped = max(0.0, min(speed, self.max_speed))
            return max(0.01, (clamped / self.max_speed) * (1.5 * math.pi))

        def _calc_rpm_width(self, rpm):
            clamped = max(0.0, min(rpm, self.max_rpm))
            return (clamped / self.max_rpm) * 600

        def _get_rpm_color(self, rpm):
            if rpm < 4000: return theme.text_main
            if rpm < 5500: return theme.warning
            return theme.danger

        def update_values(self, speed, rpm):
            self.speed_text.value = str(int(speed))

            # Zmiana koloru prędkości tylko przy max prędkości
            is_speed_danger = speed >= 140
            self.val_arc.paint.color = theme.danger if is_speed_danger else theme.text_main
            self.speed_text.color = theme.danger if is_speed_danger else theme.text_main
            self.val_arc.sweep_angle = self._calc_sweep(speed)

            self.rpm_bar_fg.width = self._calc_rpm_width(rpm)
            self.rpm_bar_fg.bgcolor = self._get_rpm_color(rpm)
            self.rpm_text.value = f"{int(rpm):,} RPM"
            self.update()

    gauge = MazdaPulseGauge(state.speed, state.rpm)

    def on_speed(e):
        update_speed_func(float(e.control.value))
        gauge.update_values(float(e.control.value), state.rpm)
    def on_rpm(e):
        update_rpm_func(float(e.control.value))
        gauge.update_values(state.speed, float(e.control.value))

    # Symulatory suwaków ukryte dla pasażera - na dole do testowania
    sliders = ft.Row([
        ft.Slider(min=0, max=220, value=state.speed, on_change=on_speed, width=200, active_color=theme.panel_border),
        ft.Slider(min=0, max=6500, value=state.rpm, on_change=on_rpm, width=200, active_color=theme.panel_border)
    ], alignment="center")

    return ft.Container(
        expand=True,
        padding=ft.Padding(0, 20, 0, 0),
        content=ft.Column([
            gauge,
            ft.Container(expand=True),
            sliders
        ], horizontal_alignment="center")
    )
