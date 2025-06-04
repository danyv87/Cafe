import uuid
from datetime import datetime

class Receta:
    def __init__(self, producto_id, producto_nombre, ingredientes=None, id=None):
        self.id = id or str(uuid.uuid4()) # ID único para la receta
        self.producto_id = producto_id # ID del producto al que pertenece esta receta
        self.producto_nombre = producto_nombre # ¡Nuevo atributo: nombre del producto!
        self.ingredientes = ingredientes if ingredientes is not None else [] # Lista de diccionarios de ingredientes

    def to_dict(self):
        """
        Convierte el objeto Receta a un diccionario para serialización JSON.
        """
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "producto_nombre": self.producto_nombre, # Incluir en la serialización
            "ingredientes": self.ingredientes
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Receta a partir de un diccionario (deserialización JSON).
        """
        return Receta(
            id=data.get("id"),
            producto_id=data.get("producto_id"),
            producto_nombre=data.get("producto_nombre"), # Incluir en la deserialización
            ingredientes=data.get("ingredientes", [])
        )

