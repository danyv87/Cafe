import uuid
from datetime import datetime


class Ticket:
    def __init__(self, cliente, items_venta=None, id=None, fecha=None):
        self.id = id or str(uuid.uuid4())  # ID único para el ticket
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora del ticket
        self.cliente = cliente  # Nombre del cliente asociado al ticket
        self.items_venta = items_venta if items_venta is not None else []  # Lista de objetos VentaDetalle

        # Calcula el total del ticket sumando los totales de cada item_venta
        self.total = round(sum(item.total for item in self.items_venta), 2)

    def to_dict(self):
        """
        Convierte el objeto Ticket a un diccionario para serialización JSON.
        """
        return {
            "id": self.id,
            "fecha": self.fecha,
            "cliente": self.cliente,
            "items_venta": [item.to_dict() for item in self.items_venta],  # Serializa cada VentaDetalle
            "total": self.total
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Ticket a partir de un diccionario (deserialización JSON).
        """
        from models.venta_detalle import VentaDetalle  # Importación local para evitar circular

        # Deserializa cada item de venta a un objeto VentaDetalle
        items_venta = [VentaDetalle.from_dict(item_data) for item_data in data.get("items_venta", [])]

        return Ticket(
            id=data.get("id"),
            fecha=data.get("fecha"),
            cliente=data.get("cliente"),
            items_venta=items_venta
        )
