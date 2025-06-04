import uuid
from datetime import datetime

class GastoAdicional:
    """
    Representa un gasto adicional o indirecto (ej. fósforos, gas, electricidad).
    """
    def __init__(self, nombre: str, monto: float, fecha: str = None, descripcion: str = None, id: str = None):
        self.id = id if id else str(uuid.uuid4())
        self.nombre = nombre
        self.monto = monto
        # Si no se proporciona una fecha, usar la fecha y hora actual
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.descripcion = descripcion if descripcion else ""

    def to_dict(self):
        """Convierte el objeto GastoAdicional a un diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "monto": self.monto,
            "fecha": self.fecha,
            "descripcion": self.descripcion
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto GastoAdicional desde un diccionario."""
        return cls(
            id=data.get("id"),
            nombre=data["nombre"],
            monto=data["monto"],
            fecha=data.get("fecha"),
            descripcion=data.get("descripcion")
        )

    def __repr__(self):
        return f"GastoAdicional(ID: {self.id[:8]}..., Nombre: {self.nombre}, Monto: {self.monto}, Fecha: {self.fecha})"

