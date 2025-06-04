import uuid
from datetime import datetime


class Compra:
    def __init__(self, proveedor, items_compra=None, id=None, fecha=None):
        self.id = id or str(uuid.uuid4())  # ID único para la compra
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora de la compra
        self.proveedor = proveedor  # Nombre del proveedor asociado a la compra
        self.items_compra = items_compra if items_compra is not None else []  # Lista de objetos CompraDetalle

        # Calcula el total de la compra sumando los totales de cada item_compra
        self.total = round(sum(item.total for item in self.items_compra), 2)

    def to_dict(self):
        """
        Convierte el objeto Compra a un diccionario para serialización JSON.
        """
        return {
            "id": self.id,
            "fecha": self.fecha,
            "proveedor": self.proveedor,
            "items_compra": [item.to_dict() for item in self.items_compra],  # Serializa cada CompraDetalle
            "total": self.total
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Compra a partir de un diccionario (deserialización JSON).
        """
        from models.compra_detalle import CompraDetalle  # Importación local para evitar circular

        # Deserializa cada item de compra a un objeto CompraDetalle
        items_compra = [CompraDetalle.from_dict(item_data) for item_data in data.get("items_compra", [])]

        return Compra(
            id=data.get("id"),
            fecha=data.get("fecha"),
            proveedor=data.get("proveedor"),
            items_compra=items_compra
        )
