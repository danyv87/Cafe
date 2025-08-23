from utils.invoice_utils import save_invoice
from controllers import compras_controller
from controllers import materia_prima_controller as mp_controller


def test_importar_factura(tmp_path):
    compras_path = tmp_path / "compras.json"
    materias_path = tmp_path / "materias.json"
    compras_path.write_text("[]", encoding="utf-8")
    materias_path.write_text("[]", encoding="utf-8")

    original_compras = compras_controller.DATA_PATH
    original_materias = mp_controller.DATA_PATH
    mp_controller.clear_materias_cache()
    try:
        compras_controller.DATA_PATH = str(compras_path)
        mp_controller.DATA_PATH = str(materias_path)
        mp_controller.clear_materias_cache()

        materia = mp_controller.agregar_materia_prima("Cafe", "kg", 5, 0)

        invoice = {
            "proveedor_id": "prov1",
            "proveedor": "Proveedor X",
            "items": [
                {
                    "producto_id": materia.id,
                    "nombre_producto": "Cafe",
                    "cantidad": 2,
                    "costo_unitario": 5,
                    "descripcion_adicional": "",
                }
            ],
            "pendientes": [],
        }
        invoice_id = save_invoice(invoice, tmp_path)
        invoice_file = tmp_path / f"{invoice_id}.json"

        compras_controller.importar_factura(invoice_file)

        compras = compras_controller.listar_compras()
        assert len(compras) == 1
        compra = compras[0]
        assert compra.proveedor_id == "prov1"
        assert compra.total == 10

        materias = mp_controller.listar_materias_primas()
        assert materias[0].stock == 2
    finally:
        compras_controller.DATA_PATH = original_compras
        mp_controller.DATA_PATH = original_materias
        mp_controller.clear_materias_cache()
