import json
import os
import sys  # Importar el módulo sys para PyInstaller
from models.materia_prima import MateriaPrima

# Determinar la ruta base de la aplicación para compatibilidad con PyInstaller.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_PATH = sys._MEIPASS
else:
    # En ambiente de desarrollo, queremos el directorio raíz del proyecto
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

DATA_PATH = os.path.join(BASE_PATH, "data", "materias_primas.json")

# Asegurarse de que la carpeta 'data' exista
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def cargar_materias_primas():
    """
    Carga la lista de materias primas desde el archivo JSON.
    Si el archivo no existe, devuelve una lista vacía.
    """
    print(f"DEBUG: Intentando cargar materias primas desde: {DATA_PATH}")  # DEBUG LINE
    if not os.path.exists(DATA_PATH):
        print(f"DEBUG: Archivo de materias primas no encontrado: {DATA_PATH}")  # DEBUG LINE
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"DEBUG: Materias primas cargadas (raw data): {data}")  # DEBUG LINE
            return [MateriaPrima.from_dict(mp) for mp in data]
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo {DATA_PATH} está vacío o malformado. Se devolverá una lista vacía.")
        return []
    except Exception as e:
        print(f"DEBUG: Error inesperado al cargar materias primas: {e}")  # DEBUG LINE
        return []


def guardar_materias_primas(materias_primas):
    """
    Guarda la lista de objetos MateriaPrima en el archivo JSON.
    """
    print(f"DEBUG: Intentando guardar {len(materias_primas)} materias primas en: {DATA_PATH}")  # DEBUG LINE
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump([mp.to_dict() for mp in materias_primas], f, indent=4)
    print("DEBUG: Materias primas guardadas con éxito.")  # DEBUG LINE


def validar_materia_prima(nombre, unidad_medida, costo_unitario, stock):
    """
    Valida los datos de una materia prima.
    Retorna True si es válido, False y un mensaje de error en caso contrario.
    """
    if not nombre or not isinstance(nombre, str) or len(nombre.strip()) == 0:
        return False, "El nombre de la materia prima no puede estar vacío."
    if not unidad_medida or not isinstance(unidad_medida, str) or len(unidad_medida.strip()) == 0:
        return False, "La unidad de medida no puede estar vacía."
    if not isinstance(costo_unitario, (int, float)) or costo_unitario <= 0:
        return False, "El costo unitario debe ser un número positivo."
    if not isinstance(stock, int) or stock < 0:
        return False, "El stock debe ser un número entero no negativo."
    return True, ""


def agregar_materia_prima(nombre, unidad_medida, costo_unitario, stock_inicial):
    """
    Agrega una nueva materia prima a la lista y la guarda.
    """
    es_valido, mensaje_error = validar_materia_prima(nombre, unidad_medida, costo_unitario, stock_inicial)
    if not es_valido:
        raise ValueError(mensaje_error)

    materias_primas = cargar_materias_primas()
    nueva_materia_prima = MateriaPrima(
        nombre.strip(),
        unidad_medida.strip(),
        costo_unitario,
        stock_inicial
    )
    materias_primas.append(nueva_materia_prima)
    guardar_materias_primas(materias_primas)
    return nueva_materia_prima


def listar_materias_primas():
    """
    Retorna la lista completa de materias primas.
    """
    return cargar_materias_primas()


def obtener_materia_prima_por_id(id_materia_prima):
    """
    Busca y retorna una materia prima por su ID.
    Retorna None si la materia prima no es encontrada.
    """
    materias_primas = cargar_materias_primas()
    for mp in materias_primas:
        if mp.id == id_materia_prima:
            return mp
    return None


def editar_materia_prima(id_materia_prima, nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario, nuevo_stock):
    """
    Edita una materia prima existente por su ID.
    """
    es_valido, mensaje_error = validar_materia_prima(nuevo_nombre, nueva_unidad_medida, nuevo_costo_unitario,
                                                     nuevo_stock)
    if not es_valido:
        raise ValueError(mensaje_error)

    materias_primas = cargar_materias_primas()
    for i, mp in enumerate(materias_primas):
        if mp.id == id_materia_prima:
            materias_primas[i].nombre = nuevo_nombre.strip()
            materias_primas[i].unidad_medida = nueva_unidad_medida.strip()
            materias_primas[i].costo_unitario = nuevo_costo_unitario
            materias_primas[i].stock = nuevo_stock
            guardar_materias_primas(materias_primas)
            return materias_primas[i]
    raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para edición.")


def eliminar_materia_prima(id_materia_prima):
    """
    Elimina una materia prima de la lista por su ID.
    """
    materias_primas = cargar_materias_primas()
    materias_primas_original_count = len(materias_primas)
    materias_primas = [mp for mp in materias_primas if mp.id != id_materia_prima]

    if len(materias_primas) == materias_primas_original_count:
        raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para eliminación.")

    guardar_materias_primas(materias_primas)
    return True


def actualizar_stock_materia_prima(id_materia_prima, cantidad_cambio):
    """
    Actualiza el stock de una materia prima.
    Args:
        id_materia_prima (str): ID de la materia prima a actualizar.
        cantidad_cambio (float): Cantidad a sumar (para compras) o restar (para ventas).
    Raises:
        ValueError: Si la materia prima no se encuentra o el stock resultante es negativo.
    """
    materias_primas = cargar_materias_primas()
    materia_prima_encontrada = None
    for i, mp in enumerate(materias_primas):
        if mp.id == id_materia_prima:
            materia_prima_encontrada = mp
            break

    if not materia_prima_encontrada:
        raise ValueError(f"Materia prima con ID '{id_materia_prima}' no encontrada para actualizar stock.")

    nuevo_stock = materia_prima_encontrada.stock + cantidad_cambio
    if nuevo_stock < 0:
        raise ValueError(
            f"Stock insuficiente para '{materia_prima_encontrada.nombre}'. Se intenta reducir el stock a {nuevo_stock}, pero solo hay {materia_prima_encontrada.stock}.")

    materias_primas[i].stock = nuevo_stock
    guardar_materias_primas(materias_primas)
    return materias_primas[i]
