import logging
from unittest.mock import patch

from controllers import compras_controller
from models.proveedor import Proveedor


@patch("controllers.compras_controller.registrar_compra_desde_imagen")
def test_importacion_masiva_registra_errores(mock_registrar, tmp_path):
    def side_effect(proveedor, archivo, como_compra=True, selector=None, **kwargs):
        if "bad" in archivo:
            raise ValueError("fail")
        return ("compra", [], {})

    mock_registrar.side_effect = side_effect

    # registrar handler temporal para verificar logs
    log_file = tmp_path / "audit.log"
    handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter("%(proveedor)s - %(archivo)s - %(message)s")
    )
    compras_controller.logger.logger.addHandler(handler)

    archivos = ["ok.jpg", "bad.jpg"]
    proveedor = Proveedor("Prov")
    resultados = compras_controller.importar_comprobantes_masivos(proveedor, archivos)

    # Verificar resultados
    assert resultados[0]["ok"] is True
    assert resultados[0]["archivo"] == "ok.jpg"
    assert resultados[1]["ok"] is False
    assert resultados[1]["archivo"] == "bad.jpg"
    assert "error" in resultados[1]

    handler.flush()
    contenido = log_file.read_text()
    assert "bad.jpg" in contenido
    assert "Prov" in contenido

    compras_controller.logger.logger.removeHandler(handler)
