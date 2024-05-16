import pandas as pd
from datetime import datetime, timedelta

def getFechaFiltrado():
    fecha_actual = datetime.now()
    fecha_hace_una_semana = fecha_actual - timedelta(weeks=1)
    fecha_formateada = fecha_hace_una_semana.strftime("%Y-%m-%d")
    return fecha_formateada


def getFilterTransaccionesTienda(data):
    # df = pd.DataFrame([{key: value for key, value in d.items() if key != '@odata.etag'} for d in data])
    df = get_df_excluyed_colum(data, "@odata.etag")

    column_names = [
        "numero_transaccion",
        "fecha_transaccion",
        "tienda",
    ]
    df = rename_columns(df, column_names)

    return df

def getFilterClient(data):
    # df = pd.DataFrame([{key: value for key, value in d.items() if key != '@odata.etag'} for d in data])
    df = get_df_excluyed_colum(data, "@odata.etag")

    column_names = [
        "cuanta_cliente",
        "nombre",
        "apellido"
    ]
    df = rename_columns(df, column_names)

    return df

def getFilterErrorMessageExtract(data):
    try:
        df = get_df_excluyed_colum(data, "@odata.etag")

        column_names = ["error_mensaje"]
        df = rename_columns(df, column_names)

        return df
    except Exception as e:
        print(f"Error en la función 'getFilterErrorMessageExtract': {e}")
        return None  # Devolver None en caso de error

def getFilterTransaccionesDeLaVenta(data):
    df = eliminar_columna(data, "@odata.etag")
    column_names = [
        "numero_transaccion",
        "codigo_producto",
        "unidad_vendida",
        'almacen',
        'num_extracto',
        "nombre_producto",
    ]
    df = renombrar_columnas(df, column_names)
    return df


def getFilterNumeroTransaccionesExtractos(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    df = eliminar_columna(df, "@odata.etag")
    column_names = ["numero_extracto", "numero_transaccion"]
    df = renombrar_columnas(df, column_names)
    return df


def getFilterExtractos(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    rename_columns = ["numero_extracto", "numero_tienda", "mensaje_error"]
    df = renombrar_columnas(df, rename_columns)
    return df


def getFilterConversionUnidades(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    df = eliminar_columna(df, "@odata.etag")
    column_names = ["Desde_unidad"]
    # column_names = ["unidad_origen", "unidad_destino"]
    df = renombrar_columnas(df, column_names)
    return df

def getFilterAlmacenUnidad(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    df = eliminar_columna(df, "@odata.etag")
    column_names = ["unidad_de_conversion"]

def getFilterAlmacenes(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    df = eliminar_columna(df, "@odata.etag")
    column_names = ["InventLocationId"]
    df = renombrar_columnas(df, column_names)
    return df

def getFilterSiteLocation(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    df = eliminar_columna(df, "@odata.etag")
    column_names = ["InventLocationId","InventSiteId"]
    df = renombrar_columnas(df, column_names)
    return df

def getFilterProUnit(data):
    df = pd.DataFrame([{key: value for key, value in d.items()} for d in data])
    df = eliminar_columna(df, "@odata.etag")
    column_names = ["InventoryUnitSymbol"]
    df = renombrar_columnas(df, column_names)
    return df


def get_df_excluyed_colum(data, columns):
    df = pd.DataFrame(
        [{key: value for key, value in d.items() if key != columns} for d in data]
    )
    return df


def rename_columns(df, column_names):
    df.columns = column_names
    return df


def eliminar_columna(dataframe, nombre_columna):
    if nombre_columna in dataframe.columns:
        dataframe.drop(columns=nombre_columna, inplace=True)
    else:
        print(f"La columna '{nombre_columna}' no existe en el DataFrame.")
    return dataframe


def renombrar_columnas(dataframe, nombres_nuevos):
    if len(dataframe.columns) != len(nombres_nuevos):
        print(
            "La longitud de la lista de nombres no coincide con el número de columnas en el DataFrame."
        )
        return dataframe

    dataframe.columns = nombres_nuevos
    return dataframe


## --- 
def verificar_unidades(df_producto, unidad_vendida):
    try:
        encontrado = []

        for index, producto in df_producto.iterrows():
            
            try:
                if producto["Desde_unidad"] == unidad_vendida:
                    encontrado.append(unidad_vendida)
            except KeyError as e:
                print(f"Error al acceder a las columnas 'unidad_origen' o 'unidad_destino': {e}")
                contador_errores += 1
        if encontrado:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error en la función verificar_unidades: {e}")
        return False

    
def verificar_almacen(almacen_vendida, data):
    try:
        print(f"Filtrando almacenes para almacen_vendida: {almacen_vendida}")
        filtro = data.loc[
            (data['InventLocationId'] == almacen_vendida)
        ]
        
        if not filtro.empty:
            return True
        else:
            return False
    
    except Exception as e:
        print(f"Error al verificar almacén: {e}")
        return False



def verifyInventLocation(almacen_vendida, data):
    try:
        print(f"Filtrando almacenes para almacen_vendida: {almacen_vendida}")

        # Filtrar el DataFrame 'data' por 'InventLocationId'
        filtro = data[data['InventLocationId'] == almacen_vendida]
        
        if not filtro.empty:
            # Obtener el primer registro del filtro (si hay múltiples coincidencias)
            first_row = filtro.iloc[0]
            
            # Comparar 'InventLocationId' específico con 'InventSiteId'
            if first_row['InventLocationId'] == 'MD01_LUZ' and first_row['InventSiteId'] == 'SR0001':
                return True
            elif first_row['InventLocationId'] == 'MD02_JRC' and first_row['InventSiteId'] == 'SR0002':
                return True
            elif first_row['InventLocationId'] == 'MD03_CRH' and first_row['InventSiteId'] == 'SR0003':
                return True
            elif first_row['InventLocationId'] == 'MD04_SUC' and first_row['InventSiteId'] == 'SR0004':
                return True
            elif first_row['InventLocationId'] == 'MD05_CRZ' and first_row['InventSiteId'] == 'SR0005':
                return True
            elif first_row['InventLocationId'] == 'MD06_BOL' and first_row['InventSiteId'] == 'SR0006':
                return True
            elif first_row['InventLocationId'] == 'MD07_CEN' and first_row['InventSiteId'] == 'SR0007':
                return True
            else:
                return False
        else:
            return 'nulo'

    except Exception as e:
        print(f"Error al verificar TYPELOCATION: {e}")
        return False

def verificar_error_trasaction(data):
    try:
        filtro = data.loc[
            (data['ErrorMessage'])
        ]
        
        if not filtro.empty:
            return data['ErrorMessage']
        else:
            return False
    
    except Exception as e:
        print(f"Error al verificar almacén: {e}")
        return False
    
def productUnit(data):
    try:
        filtro = data.loc[
            (data['InventoryUnitSymbol'] == "U.")
        ]
        
        if not filtro.empty:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error al verificar productounit: {e}")
        return False