import uuid

class MateriaPrima:
    def __init__(self, nombre, unidad_medida, costo_unitario, stock=0, stock_minimo=0, id=None):
        self.id = id or str(uuid.uuid4()) # ID único para la materia prima
        self.nombre = nombre.strip() # Nombre de la materia prima (ej: "Granos de Café", "Leche")
        self.unidad_medida = unidad_medida.strip() # Unidad de medida (ej: "kg", "litros", "unidades")
        self.costo_unitario = costo_unitario # Costo por unidad de compra
        self.stock = stock # Cantidad actual en inventario
        self.stock_minimo = stock_minimo # Cantidad mínima deseada en inventario

    def to_dict(self):
        """
        Convierte el objeto MateriaPrima a un diccionario para serialización JSON.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "unidad_medida": self.unidad_medida,
            "costo_unitario": self.costo_unitario,
            "stock": self.stock,
            "stock_minimo": self.stock_minimo
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto MateriaPrima a partir de un diccionario (deserialización JSON).
        """
        return MateriaPrima(
            id=data.get("id"),
            nombre=data.get("nombre"),
            unidad_medida=data.get("unidad_medida"),
            costo_unitario=data.get("costo_unitario"),
            stock=data.get("stock", 0), # Asegura que el stock tenga un valor por defecto
            stock_minimo=data.get("stock_minimo", 0)
        )
