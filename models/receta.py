import uuid
from datetime import datetime

class Receta:
    def __init__(self, producto_id, nombre_producto, ingredientes=None, rendimiento=None, id=None):
        self.id = id or str(uuid.uuid4()) # ID único para la receta
        self.producto_id = producto_id # ID del producto terminado al que pertenece esta receta
        self.nombre_producto = nombre_producto # Nombre del producto terminado
        # ingredientes será una lista de diccionarios, ej:
        # [{"materia_prima_id": "uuid1", "nombre_materia_prima": "Granos de Café", "cantidad_necesaria": 20, "unidad_medida": "gramos"}]
        self.ingredientes = ingredientes if ingredientes is not None else []
        self.rendimiento = rendimiento # Nuevo atributo para el rendimiento de la receta (ej. número de unidades)

    def to_dict(self):
        """
        Convierte el objeto Receta a un diccionario para serialización JSON.
        """
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "nombre_producto": self.nombre_producto,
            "ingredientes": self.ingredientes, # Los ingredientes ya son diccionarios
            "rendimiento": self.rendimiento # Incluir el rendimiento en el diccionario
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Receta a partir de un diccionario (deserialización JSON).
        """
        return Receta(
            id=data.get("id"),
            producto_id=data.get("producto_id"),
            nombre_producto=data.get("nombre_producto"),
            ingredientes=data.get("ingredientes", []),
            rendimiento=data.get("rendimiento") # Obtener el rendimiento del diccionario
        )
