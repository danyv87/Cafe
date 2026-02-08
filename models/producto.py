import uuid

class Producto:
    def __init__(self, nombre, precio_unitario, id=None, disponible_venta=True):
        self.id = id or str(uuid.uuid4())
        self.nombre = nombre
        self.precio_unitario = precio_unitario
        self.disponible_venta = disponible_venta
        # El atributo 'stock' ha sido removido de aquí.
        # La disponibilidad de productos terminados se gestionará a través de materias primas y recetas.

    def to_dict(self):
        """
        Convierte el objeto Producto a un diccionario para serialización JSON.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio_unitario": self.precio_unitario,
            "disponible_venta": self.disponible_venta,
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Producto a partir de un diccionario (deserialización JSON).
        """
        return Producto(
            id=data.get("id"),
            nombre=data.get("nombre"),
            precio_unitario=data.get("precio_unitario"),
            disponible_venta=data.get("disponible_venta", True),
        )
