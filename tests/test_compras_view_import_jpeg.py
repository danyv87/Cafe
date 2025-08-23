import json
import sys
import types
from gui.compras_view import importar_desde_archivo
from models.proveedor import Proveedor
from models.compra_detalle import CompraDetalle


def test_importar_desde_archivo_jpeg(monkeypatch):
    monkeypatch.setattr('gui.compras_view.filedialog.askopenfilename', lambda title: 'factura.jpg')
    monkeypatch.setattr('gui.compras_view.mostrar_imagen', lambda path: None)

    invoice_data = {
        "proveedor_id": "prov-1",
        "proveedor": "Proveedor Uno",
        "fecha": "2024-05-01 12:00:00",
        "items": [
            {
                "producto_id": "mp-1",
                "nombre_producto": "Azucar",
                "cantidad": 3,
                "costo_unitario": 10,
                "descripcion_adicional": "blanca",
            }
        ],
    }

    class DummyResponse:
        def __init__(self, text):
            self.text = text

    def fake_generate_content(model=None, contents=None, config=None):
        return DummyResponse(json.dumps(invoice_data))

    fake_genai = types.ModuleType("google.genai")
    class DummyClient:
        def __init__(self, *a, **k):
            self.models = types.SimpleNamespace(generate_content=fake_generate_content)
    fake_genai.Client = DummyClient
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, 'google', fake_google)
    monkeypatch.setitem(sys.modules, 'google.genai', fake_genai)

    captured = {}
    def fake_registrar(proveedor, detalles, fecha=None):
        captured['proveedor'] = proveedor
        captured['detalles'] = detalles
        captured['fecha'] = fecha
        return object()

    monkeypatch.setattr('gui.compras_view.registrar_compra', fake_registrar)
    monkeypatch.setattr('gui.compras_view.messagebox.showinfo', lambda *a, **k: None)
    monkeypatch.setattr('gui.compras_view.messagebox.showerror', lambda *a, **k: None)

    items = [object()]
    updated = {'called': False}
    def actualizar():
        updated['called'] = True
    class DummyLabel:
        def __init__(self):
            self.text = ''
        def config(self, text):
            self.text = text
    label = DummyLabel()

    importar_desde_archivo(items, actualizar, label)

    assert isinstance(captured['proveedor'], Proveedor)
    assert captured['proveedor'].nombre == invoice_data['proveedor']
    assert captured['fecha'] == invoice_data['fecha']
    assert isinstance(captured['detalles'], list) and len(captured['detalles']) == 1
    detalle = captured['detalles'][0]
    item = invoice_data['items'][0]
    assert isinstance(detalle, CompraDetalle)
    assert detalle.producto_id == item['producto_id']
    assert detalle.nombre_producto == item['nombre_producto']
    assert detalle.cantidad == item['cantidad']
    assert detalle.costo_unitario == item['costo_unitario']
    assert detalle.descripcion_adicional == item['descripcion_adicional']

    assert items == []
    assert updated['called']
    assert label.text == 'Total Compra: Gs 0'
