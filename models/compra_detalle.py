from datetime import datetime

class CompraDetalle:
    def __init__(self, producto_id, nombre_producto, cantidad, costo_unitario, descripcion_adicional="", fecha_item=None):
        self.fecha_item = fecha_item or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.producto_id = producto_id
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad
        self.costo_unitario = costo_unitario
        self.descripcion_adicional = descripcion_adicional # ¡Nuevo atributo!
        self.total = round(cantidad * costo_unitario, 2)

    def to_dict(self):
        """
        Convierte el objeto CompraDetalle a un diccionario para serialización JSON.
        """
        return {
            "fecha_item": self.fecha_item,
            "producto_id": self.producto_id,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "costo_unitario": self.costo_unitario,
            "descripcion_adicional": self.descripcion_adicional, # Incluir en la serialización
            "total": self.total
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto CompraDetalle a partir de un diccionario (deserialización JSON).
        """
        return CompraDetalle(
            fecha_item=data.get("fecha_item"),
            producto_id=data.get("producto_id"),
            nombre_producto=data.get("nombre_producto"),
            cantidad=data.get("cantidad"),
            costo_unitario=data.get("costo_unitario"),
            descripcion_adicional=data.get("descripcion_adicional", "") # Incluir en la deserialización, con valor por defecto
        )
