from datetime import datetime

class VentaDetalle: # Renombrada de Venta a VentaDetalle
    def __init__(self, producto_id, nombre_producto, cantidad, precio_unitario, fecha_item=None):
        # La fecha aquí es para el item individual, aunque el ticket tendrá su propia fecha
        self.fecha_item = fecha_item or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.producto_id = producto_id
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.total = round(cantidad * precio_unitario, 2) # Total por este item de venta

    def to_dict(self):
        """
        Convierte el objeto VentaDetalle a un diccionario para serialización JSON.
        """
        return {
            "fecha_item": self.fecha_item, # Renombrado de 'fecha' a 'fecha_item' para claridad
            "producto_id": self.producto_id,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "total": self.total
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto VentaDetalle a partir de un diccionario (deserialización JSON).
        """
        return VentaDetalle(
            fecha_item=data.get("fecha_item"), # Usar 'fecha_item'
            producto_id=data.get("producto_id"),
            nombre_producto=data.get("nombre_producto"),
            cantidad=data.get("cantidad"),
            precio_unitario=data.get("precio_unitario")
        )
