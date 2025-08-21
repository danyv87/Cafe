import uuid

class Proveedor:
    def __init__(self, nombre, contacto="", id=None):
        self.id = id or str(uuid.uuid4())
        self.nombre = nombre.strip()
        self.contacto = contacto.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "contacto": self.contacto,
        }

    @staticmethod
    def from_dict(data):
        return Proveedor(
            id=data.get("id"),
            nombre=data.get("nombre"),
            contacto=data.get("contacto", ""),
        )
