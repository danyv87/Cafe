"""Aplicación móvil base con Kivy para el sistema de cafetería.

Esta versión inicial reutiliza la capa de controladores existente y muestra
métricas básicas para validar integración en dispositivos móviles.
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from controllers.productos_controller import listar_productos
from controllers.tickets_controller import listar_tickets


class DashboardCard(BoxLayout):
    """Tarjeta simple para mostrar una métrica en el dashboard."""

    def __init__(self, titulo: str, valor: str, **kwargs):
        super().__init__(orientation="vertical", padding=dp(14), spacing=dp(4), **kwargs)
        self.size_hint_y = None
        self.height = dp(100)

        self.add_widget(
            Label(
                text=titulo,
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                halign="left",
                valign="middle",
            )
        )
        self.add_widget(
            Label(
                text=valor,
                font_size="24sp",
                color=(0.1, 0.4, 0.2, 1),
                halign="left",
                valign="middle",
            )
        )


class CafeMobileApp(App):
    """App móvil inicial de la cafetería."""

    def build(self):
        self.title = "Cafe Mobile"
        Window.clearcolor = (0.96, 0.96, 0.96, 1)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        root.add_widget(
            Label(
                text="Cafetería · Panel móvil (MVP)",
                size_hint_y=None,
                height=dp(42),
                font_size="20sp",
                bold=True,
                color=(0.12, 0.12, 0.12, 1),
            )
        )

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        productos = listar_productos()
        tickets = listar_tickets()
        total_ventas = sum(ticket.total for ticket in tickets)

        cards = [
            DashboardCard("Productos registrados", str(len(productos))),
            DashboardCard("Tickets emitidos", str(len(tickets))),
            DashboardCard("Ventas acumuladas", f"Gs {total_ventas:,.0f}"),
            DashboardCard(
                "Estado",
                "Base móvil Kivy lista.\nSiguiente paso: pantallas de Ventas y Stock.",
            ),
        ]

        for card in cards:
            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)

        return root


if __name__ == "__main__":
    CafeMobileApp().run()
