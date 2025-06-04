import uuid

class Producto:
    def __init__(self, nombre, precio_unitario, id=None):
        self.id = id or str(uuid.uuid4())
        self.nombre = nombre
        self.precio_unitario = precio_unitario

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio_unitario": self.precio_unitario
        }

    @staticmethod
    def from_dict(data):
        return Producto(
            id=data.get("id"),
            nombre=data.get("nombre"),
            precio_unitario=data.get("precio_unitario")
        )
