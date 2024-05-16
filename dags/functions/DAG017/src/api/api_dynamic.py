import requests
from urllib.parse import urljoin
from ..functions.function_api_dynamic import *

class ApiDynamics:
    
    def __init__(self):
        self.url = self.get_entorno_trabajo(1)
        self.token = self.get_token()

    def get_entorno_trabajo(self, entorno):
        if entorno == 1:
            print("--- Entorno de producción --")
            return "https://mistr.operations.dynamics.com"
        # Si el entorno no es 1 (suponiendo que sea 2 para pruebas), devuelve la URL del entorno de pruebas
        else:
            print("--- Entorno de pruebas --")
            return "https://mistr-master.sandbox.operations.dynamics.com"
        # return "https://mistr.operations.dynamics.com/"

    def get_token(self):
        env = {
            "client_id": "53f3c906-9bfc-4a5d-89d8-30ce9a672481",
            "client_secret": "zNA3~9-5wuywwiflFbAP52cgJ_5wQ__Y48",
            "resource": self.url,
            "grant_type": "client_credentials",
        }

        endp = "https://login.microsoftonline.com/ceb88b8e-4e6a-4561-a112-5cf771712517/oauth2/token"

        try:
            req = requests.post(endp, env)
            req.raise_for_status()
            return "Bearer {0}".format(req.json().get("access_token"))
        except requests.exceptions.RequestException as e:
            print("Error al obtener el token:", e)
            return None

    def build_url(self, endpoint, query=""):
        return urljoin(self.url, endpoint) + query

    def get_data(self, path):
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        try:
            response = requests.get(path, headers=headers)
            response.raise_for_status()
            return response.json().get("value", [])
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud:", e)
            return []


    #Obtener error en la cuenta de cliente
    def getClientError(self):
        try:
            path = self.build_url("/data/CustomersV3")

            query = f"?$count=true &$select=CustomerAccount,NameAlias,PersonLastName"
            data = self.get_data(path + query)
            if not data:
                return pd.DataFrame({})
            return getFilterClient(data)
        except Exception as e:
            print(f"Error al realizar la solicitud CustomersV3: {e}")
            return pd.DataFrame({})
    
    def verifyClient(self):
        try:
            df = self.getClientError()
            contains_trv = df[~df['cuanta_cliente'].str.contains('TRV')]
            return contains_trv
        except Exception as e:
            print(f"Error al realizar la verifiación del cliente: {e}")
            return False
    
    
    # Obtener errores transacciones de la tienda
    def getTransaccionesDeLaTienda(self):
        try:
            path = self.build_url("/data/RetailTransactionsAuditable")

            # fecha = "2024-03-23"
            # status = 'Failed'
            # query = f"?$filter=TransactionDate ge {fecha}T00:00:00Z and ValidationStatus eq 'Error'&$select=TransactionId,TransactionDate,Warehouse"
            query = f"?$count=true&$filter=ValidationStatus eq Microsoft.Dynamics.DataEntities.RetailTransactionValidationStatus'Failed'&$select=TransactionId,TransactionDate,OperatingUnitNumber"
            data = self.get_data(path + query)
            if not data:
                return False
            return getFilterTransaccionesTienda(data)
        except Exception as e:
            print(f"Error al realizar la solicitud RetailTransactionsAuditable: {e}")
            return False

    def getNombreProducto(self, codigo_producto):
        try:
            path = self.build_url("/data/ReleasedProductCreationsV2")
            query = f"?$filter=ItemNumber eq '{codigo_producto}'&$select=ItemNumber,ProductDescription"
            data = self.get_data(path + query)
            if not data:
                return False
            return data[0]["ProductDescription"]
        except Exception as e:
            print(f"Error al obtener el nombre del producto: {e}")
            return False
    
    def getNumExtracto(self, TransactionId):
        try:
            path = self.build_url("/data/TRURetailEodTransactions")
            query = f"?$filter=TransactionId eq '{TransactionId}'&$select=StatementId"
            data = self.get_data(path + query)
            if not data:
                return False
            return data[0]["StatementId"]
        except Exception as e:
            print(f"Error al obtener el número del extracto: {e}")
            return False
    
    # Obtener errores transacciones de la venta
    def getTransaccionesDeLaVenta(self, numeroTransaccion):
        try:
            path = self.build_url("/data/RetailTransactionSalesLinesV2")
            query = f"?$filter=TransactionNumber eq '{numeroTransaccion}' &$select=TransactionNumber,ItemId,Unit,Warehouse"
            data = self.get_data(path + query)
            if not data:
                return False
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error al realizar la solicitud RetailTransactionSalesLinesV2: {e}")
            return False

    def consultarTransaccionesDeVentas(self, lista_numeros_transaccion):
        try:
            if not lista_numeros_transaccion:
                print("La lista de números de transacción está vacía.")
                return False
        
            dfs = []
            for numero_transaccion in lista_numeros_transaccion:
                df = self.getTransaccionesDeLaVenta(numero_transaccion)
                if df is not False:
                    dfs.append(df)
            if not dfs:
                return False

            df = pd.concat(dfs, ignore_index=True)

            # Obtener los números de los extractos
            number_extract = []
            for num_transaccion in df["TransactionNumber"]:
                num_extract = self.getNumExtracto(num_transaccion)
                number_extract.append(num_extract if num_extract else "")

            # Agregar la columna de nombres de productos al DataFrame
            df["num_extracto"] = number_extract

            # Obtener los nombres de los productos
            nombres_productos = []
            for codigo_producto in df["ItemId"]:
                nombre_producto = self.getNombreProducto(codigo_producto)
                nombres_productos.append(nombre_producto if nombre_producto else "")

            # Agregar la columna de nombres de productos al DataFrame
            df["nombre_producto"] = nombres_productos
            # print(df)

            return getFilterTransaccionesDeLaVenta(df)

        except Exception as e:
            print(f"Error al consultar transacciones de ventas: {e}")
            return False

    def getExtractosErrores(self):
        try:
            path = self.build_url("/data/RetailEodStatementAggregations")

            StatementStatus = "Aggregated"
            AggregationStatus = "SOCreateFailed"

            query = f"?$filter=(StatementStatus eq Microsoft.Dynamics.DataEntities.RetailEodTransactionPostingStatus'{StatementStatus}' and AggregationStatus eq Microsoft.Dynamics.DataEntities.RetailEodTransactionAggregationHeaderPostingStatus'{AggregationStatus}')&$select=StatementId,StoreNumber,ErrorMessage"

            data = self.get_data(path + query)
            if not data:
                return False

            return getFilterExtractos(data)
        except Exception as e:
            print(f"Error al realizar la solicitud RetailEodStatementAggregations: {e}")
            return False

    def getNumeroTransaccionExtractos(self, numero_extracto):
        try:
            path = self.build_url("/data/TRURetailEodTransactions")

            PostingErrorCode = "Error"

            query = f"?$filter=StatementId eq '{numero_extracto}' and PostingErrorCode eq Microsoft.Dynamics.DataEntities.RetailEodTransactionPostingErrorCode'{PostingErrorCode}' &$select=StatementId,TransactionId"

            data = self.get_data(path + query)
            if not data:
                return False

            return getFilterNumeroTransaccionesExtractos(data)
        except Exception as e:
            print(f"Error al realizar la solicitud TRURetailEodTransactions: {e}")
            return False

    def consultarTransaccionesExtractos(self, lista_extractos):
        dfs = []
        for numero_extracto in lista_extractos:
            try:
                df = self.getNumeroTransaccionExtractos(numero_extracto)
                if df is not False:
                    dfs.append(df)
            except Exception as e:
                print(
                    f"Error al consultar transacciones para el extracto {numero_extracto}: {e}"
                )
        if not dfs:
            return False

        try:
            df = pd.concat(dfs, ignore_index=True)
            return df
        except Exception as e:
            print(f"Error al concatenar los dataframes: {e}")
            return False





    # CONVERSION DE UNIDADES
    def getUnidades(self, producto, unidad_vendida):
        try:
            
            print("Conversiones de unidades")

            path = self.build_url("data/ProductUnitOfMeasureConversions")
            # query = f"?$filter=ProductNumber eq '{producto}' &$select=FromUnitSymbol,ToUnitSymbol"
            query = f"?$filter=ProductNumber eq '{producto}' and ToUnitSymbol eq 'U.' &$select=FromUnitSymbol"
            data = self.get_data(path + query)

            if not data:
                return False

            data = getFilterConversionUnidades(data)
            # print(data)
            estado_verificacion_unidades = verificar_unidades(data, unidad_vendida)
            return estado_verificacion_unidades
        except Exception as e:
            print(f"Error al obtener conversion de unidades: {e}")
            return False

    def consultarUnidades(self, df_productos):
        try:
            if df_productos.empty:
                print("El DataFrame de productos está vacío.")
                return False
        
            for index, producto in df_productos.iterrows():
                codigo_producto = str(producto["codigo_producto"])
                unidad_vendida = str(producto["unidad_vendida"])

                estado_conv_unidades = self.getUnidades(
                    codigo_producto, unidad_vendida
                )

                # Agregar una columna al DataFrame con el resultado de la función
                df_productos.at[index, "verificacion_unidad"] = estado_conv_unidades

            return df_productos
        except Exception as e:
            print(f"Error al consultar conversion de unidades: {e}")
            return False

    #Consultar almacen con unidad
    def getAlmacenUnidad(self, codigo_producto, unidad_vendida):
        try:
            path = self.build_url("data/ProductUnitOfMeasureConversions")
            query = f"?$filter=ProductNumber eq '{codigo_producto}' and ToUnitSymbol eq 'U.' and FromUnitSymbol eq '{unidad_vendida}' &$select=UnitOfMeasureConversion"
            data = self.get_data(path + query)
            if not data:
                return False
            return data
        except:
            pass


    # ALMACENES
    def getAlmacenes(self, unitMeasure, almacen_vendida):
        try:
            path = self.build_url("data/ConversionProductUnitsWarehouses")
            query = f"?$filter=UnitOfMeasureConversion eq {unitMeasure} &$select=InventLocationId"

            data = self.get_data(path + query)

            if not data:
                return False

            data = getFilterAlmacenes(data)

            estado_almacen = verificar_almacen(
                almacen_vendida, data
            )  # Salida: True

            return estado_almacen

        except Exception as e:
            print(f"Error al obtener conversion de unidades: {e}")
            return False

        # return data

    def consultarAlmacenes(self, df_productos):
        try:
            if df_productos.empty:
                print("El DataFrame de productos está vacío.")
                return False
            # df de productos que
            for index, producto in df_productos.iterrows():
                codigo_producto = str(producto["codigo_producto"])
                almacen_vendida = str(producto["almacen"])
                unidad_vendidad = str(producto["unidad_vendida"])
                obtener_almacen = self.getAlmacenUnidad(
                    codigo_producto, unidad_vendidad
                )
                primer_elemento = obtener_almacen[0]
                estado_almacen = self.getAlmacenes(
                    primer_elemento["UnitOfMeasureConversion"], almacen_vendida
                )

                df_productos.at[index, "validacion_almacen"] = estado_almacen

            return df_productos
        except Exception as e:
            print(f"Error al consultar almacenes: {e}")
            return False

        
    def consultSiteLocation(self, unitMeasure, almacen_vendida):
        try:
            path = self.build_url("data/ConversionProductUnitsWarehouses")
            query = f"?$filter=UnitOfMeasureConversion eq {unitMeasure} &$select=InventLocationId,InventSiteId"

            data = self.get_data(path + query)

            if not data:
                return False
            
            data = getFilterSiteLocation(data)
            
            estado_almacen = verifyInventLocation(
                almacen_vendida, data
            )  # Salida: True

            return estado_almacen

        except Exception as e:
            print(f"Error al obtener conversion de unidades: {e}")
            return False

    def SendVerifySiteLocation(self, df_productos):
        try:
            if df_productos.empty:
                print("El DataFrame de productos está vacío.")
                return False
            # df de productos que
            for index, producto in df_productos.iterrows():
                codigo_producto = str(producto["codigo_producto"])
                almacen_vendida = str(producto["almacen"])
                unidad_vendidad = str(producto["unidad_vendida"])
                obtener_almacen = self.getAlmacenUnidad(
                    codigo_producto, unidad_vendidad
                )
                primer_elemento = obtener_almacen[0]
                estado_sitio_alamcen = self.consultSiteLocation(
                    primer_elemento["UnitOfMeasureConversion"], almacen_vendida
                )

                df_productos.at[index, "validacion_sitio_almacen"] = estado_sitio_alamcen

            return df_productos
        except Exception as e:
            print(f"Error al consultar validacion_sitio_almacen: {e}")
            return False
    
    ##Verify error of extract
    def Verify_extract_error(self, transactionID):
        try:
            path = self.build_url("/data/RetailTransactionValidationErrorBIEntities")
            query = f"?$filter=TransactionId eq '{transactionID}'&$select=ErrorMessage"
            data = self.get_data(path + query)
            
            if not data:
                return None  # Devolver None si no hay datos
            
            error_df = getFilterErrorMessageExtract(data)
            return error_df
        
        except Exception as e:
            print(f"Error al realizar la solicitud RetailTransactionValidationErrorBIEntities: {e}")
            return None

    def SendVerifyExtractError(self, df_productos):
        try:
            if df_productos.empty:
                print("El DataFrame de productos está vacío.")
                return False
            for index, producto in df_productos.iterrows():
                codigo_producto = str(producto["numero_transaccion"])
                obtener_error = self.Verify_extract_error(codigo_producto)
                
                if obtener_error is not None and not obtener_error.empty:
                    # Concatenar todos los mensajes de error asociados con el código de producto
                    mensajes_error = obtener_error["error_mensaje"].tolist()
                    mostrar_error = " | ".join(mensajes_error)
                    df_productos.at[index, "validacion_error_transaccion"] = mostrar_error
                else:
                    df_productos.at[index, "validacion_error_transaccion"] = 'None'
            return df_productos
        
        except Exception as e:
            print(f"Error al consultar validacion_error_transaccion: {e}")
            return False
    
    def getUnidadProduct(self, codigoprod):
        try:
            path = self.build_url("data/ReleasedProductsV2")
            query = f"?$filter=ItemNumber eq '{codigoprod}' &$select=InventoryUnitSymbol"

            data = self.get_data(path + query)

            if not data:
                return False

            data = getFilterProUnit(data)

            etado_unidad = productUnit(data)

            return etado_unidad

        except Exception as e:
            print(f"Error al obtener conversion de unidades: {e}")
            return False
    
    def verifyInventoryUnitSymbol(self, df_productos):
        try:
            if df_productos.empty:
                print("El DataFrame de productos está vacío.")
                return False
            # df de productos que
            for index, producto in df_productos.iterrows():
                codigo_producto = str(producto["codigo_producto"])
                obtener_almacen = self.getUnidadProduct(
                    codigo_producto
                )

                df_productos.at[index, "validar_unidad"] = obtener_almacen

            return df_productos
        except Exception as e:
            print(f"Error al consultar almacenes: {e}")
            return False


