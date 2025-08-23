from gui.compras_view import importar_desde_archivo


def test_importar_desde_archivo(monkeypatch):
    monkeypatch.setattr('gui.compras_view.filedialog.askopenfilename', lambda title: 'factura.json')
    monkeypatch.setattr('gui.compras_view.simpledialog.askstring', lambda title, prompt: 'INV1')
    called = {}
    def fake_importar_factura(src, invoice_id):
        called['args'] = (src, invoice_id)
    monkeypatch.setattr('gui.compras_view.importar_factura', fake_importar_factura)
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

    assert called['args'] == ('factura.json', 'INV1')
    assert items == []
    assert updated['called']
    assert label.text == 'Total Compra: Gs 0'
