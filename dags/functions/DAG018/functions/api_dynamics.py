import requests, json
import datetime
import pandas as pd
import re

class ApiDynamics:
    
    #Definiendo variables
    url = "https://mistr.operations.dynamics.com/"
    extracto=""
    transaccion=""
    msg_error=""
    lista_productos={}
    productos=""
    
    ##
    productsBarcode = None
    categoryProducts = None
    translationProducts = None
    AllProducts = None
    listProviders = None
    listProductsSell = None
    productsInactive = None
    unitConvertionProducts = None
    priceProducts = None
    productCreations = None
    prodcutForAI = None
    wareHouses = None
    

    #Inicializando 
    def __init__(self, except_barCode, exceptu_andU, except_inventUnitSymbol):
        
        self.exect_barCode = except_barCode
        self.exceptu_andU = exceptu_andU
        self.except_inventUnitSymbol = except_inventUnitSymbol
        
        
        ##
    
    def ejecutar_funciones(self):
        ##
        self.get_Token()
        self.productsBarcode = pd.read_json(json.dumps(self.getBarcodeProduct()))
        self.categoryProducts = pd.read_json(json.dumps(self.getCategoryProduct()))
        self.translationProducts = pd.read_json(json.dumps(self.getTraslationProduct()))
        self.AllProducts = pd.read_json(json.dumps(self.getAllProducts()))
        self.listProviders = pd.read_json(json.dumps(self.getListProvidersProducts()))
        self.listProductsSell = pd.read_json(json.dumps(self.getProductsSell()))
        self.productsInactive = pd.read_json(json.dumps(self.getAllProductsInactive()))
        self.unitConvertionProducts = pd.read_json(json.dumps(self.getUnitConversionProducts()))
        self.priceProducts = pd.read_json(json.dumps(self.getPricesProducts()))
        self.productCreations = pd.read_json(json.dumps(self.getProductsCreations()))
        self.wareHouses = pd.read_json(json.dumps(self.getWarehouses()))
        
        self.getProductsSell()
        self.verifyExistsBarCode()
        self.verifyExistsDuplicateBarCode()
        self.verifyEquiUnitSymbol()
        self.verifyAssignProvider()
        self.verifyTranslationProduct1()
        self.verifyTranslationProduct2()
        self.verifyTranslationProduct3()
        self.verifyProductsInStateActive()
        self.verifyPricesExists()
        self.verifyTranslationProductosEmptyFields()
        self.verifyFromToUnitSymbol()
        self.verifyProductType()
        self.verifyProductSubType()
        self.verifyServiceType()
        self.verifyNameFields()
        self.verifyStorageDimensionGroupName()
        self.verifyTrackingDimensionGroupName()
        self.verifyItemModelGroupId()
        self.verifyPurchaseUnitSymbol()
        self.verifySalesUnitSymbol()
        self.verifyPurchaseSalesTaxItemGroupCode()
        self.verifySalesSalesTaxItemGroupCode()
        self.verifyInventoryUnitSymbol()
        self.verifyProductGroupId()
        self.verifyNetProductWeight()
        self.verifyNetProductWeight()
        self.verifyTransferOrderUnderdeliveryPercentage()
        self.verifyProductCoverageGroupId()
        self.verifyProductionType()
        self.verifyCodeProduct()
        self.verifyCodeProductWithEightDigits()
        self.verifyIsPurchasePriceAutomaticallyUpdated()
        self.verifyIsSalesPriceAdjustmentAllowed()
        self.verifyIsUnitCostAutomaticallyUpdated()
        self.verifyIsManualDiscountPOSRegistrationProhibited()
        self.verifyKeyInQuantityRequirementsAtPOSRegister()
        
    
    def get_Token(self):
        env = {
                "client_id":"53f3c906-9bfc-4a5d-89d8-30ce9a672481",
                "client_secret":"zNA3~9-5wuywwiflFbAP52cgJ_5wQ__Y48",
                "resource":f"{self.url}",
                "grant_type":"client_credentials"
            }
        endp = 'https://login.microsoftonline.com/ceb88b8e-4e6a-4561-a112-5cf771712517/oauth2/token'
        
        req = requests.post(endp,env)
        
        if req.status_code == 200:
            token = req.json()['access_token']
            return 'Bearer {0}'.format(token)
        else:
            return None
    
    #region Obtener Todos Productos Vendidos
    def getProductsSell(self): 
        #Definir url
        path = f"{self.url}/data/RetailTransactionSalesLinesV2"
        
        token = self.get_Token()
        
        #Date Now
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        #Queries
        query = f"?$filter=TransactionDate eq '{fecha_actual}'&$select=ItemId,Unit"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion

    #region Verificación de campos
    #Verificar si es que el producto contiene barcode
    def verifyExistsBarCode(self):
        df1 = self.AllProducts
        df2 = self.productsBarcode
        df3 = self.wareHouses
        df4 = self.categoryProducts
        
        names_markets = ['MD01_LUZ', 'MD02_JRC', 'MD03_CRH', 'MD04_SUC', 'MD05_CRZ', 'MD06_BOL']
        
        # Filtrar df3 para incluir solo los registros con InventoryWarehouseId en names_markets
        filtered_df3 = df3[df3['InventoryWarehouseId'].isin(names_markets)]
        
        if not filtered_df3.empty:  # Verificar si hay al menos un almacén en la lista 'names_markets'
            # Obtener los ItemNumber que cumplen con la condición de df3
            valid_item_numbers = filtered_df3['ItemNumber'].unique()
            
            # Filtrar df1 con los productos que no tienen 'ItemNumber' correspondiente en df2 y son válidos según df3
            result = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
            consult = result[~result['ItemNumber'].isin(df2['ItemNumber']) & result['ItemNumber'].isin(valid_item_numbers)]
            
            
            # Contar la cantidad de productos encontrados
            x, _ = consult.shape
            
            if x > 0:
                print("-- Total prod. sin código de barras encontrado:", x)
                
                # Excluir los 'ItemNumber' específicos
                excluded_item_numbers =  self.exect_barCode
                
                # Filtrar filas con 'ItemNumber' excluidos
                data = consult[~consult['ItemNumber'].isin(excluded_item_numbers)][["ItemNumber", "SearchName"]]
                return data
            else:
                return pd.DataFrame({})
        else:
            return pd.DataFrame({})
    
    #Verificar si es que el barcode se repite
    def verifyExistsDuplicateBarCode(self):
        df2 = self.productsBarcode
        
        # Agrupar por 'Barcode' y contar los 'ItemNumber' únicos por cada código de barras
        grouped = df2.groupby('Barcode')['ItemNumber'].nunique().reset_index()
        
        # Filtrar para obtener solo los códigos de barras que tienen más de un 'ItemNumber' único
        duplicated_barcodes = grouped[grouped['ItemNumber'] > 1]['Barcode']
        
        # Filtrar df2 para obtener solo los registros con códigos de barras duplicados
        if not duplicated_barcodes.empty:
            duplicated_data = df2[df2['Barcode'].isin(duplicated_barcodes)]
            print("Se encontraron códigos de barras duplicados:")
            return duplicated_data[['ItemNumber', 'Barcode']]
        else:
            print("No se encontraron códigos de barras duplicados.")
            return pd.DataFrame({})

    #Verificar conversión de unidades
    def verifyEquiUnitSymbol(self):
        df1 = self.unitConvertionProducts
        df2 = self.AllProducts
        df1["from_u"] = df1["FromUnitSymbol"].apply(lambda x: re.findall(r'\d+',x))
        df1["from_u"] = df1["from_u"].apply(lambda x: int(x[0]) if len(x) > 0 else 1)
        df1["to_u"] = df1["ToUnitSymbol"].apply(lambda x: re.findall(r'\d+',x))
        df1["to_u"] = df1["to_u"].apply(lambda x: int(x[0]) if len(x) > 0 else 1)
        #temp_result = df1[~(df1["to_u"].astype(int) * df1["Factor"].astype(int) == df1["from_u"].astype(int))]
        temp_result = df1[~(df1["to_u"].astype(float) * df1["Factor"].astype(float) == df1["from_u"].astype(float))]
        result = pd.merge(df2,temp_result,left_on='ItemNumber',right_on='ProductNumber')
        result["error"] = result["ToUnitSymbol"].astype(str) +' / '+ result["Factor"].astype(str) +' / '+ result["FromUnitSymbol"].astype(str)
        x , y = result.shape
        
        if x>0:
            print("-- Total prod. con problemas en unidades de conversion encontrado:" ,x)
            data = result[["ItemNumber","SearchName","error"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    #Verificar si el producto contiene proveedor
    def verifyAssignProvider(self):
        df1= self.AllProducts
        df2 = self.listProviders
        df4 = self.categoryProducts
        # Exclude specific ItemNumber values
        result1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        result  = result1[~result1['ItemNumber'].isin(df2['ItemNumber'])]
        # exclusiones segun el joven cesar
        excluded_item_numbers = [700039]
        
        # Filter out rows with excluded ItemNumber values
        result = result[~result['ItemNumber'].isin(excluded_item_numbers)]
        #print(result) ##Esperar a verificar
        
        x,y = result.shape
        if x>0:
            print("-- Total prod. sin proveedor encontrados:" ,x)
            data = result[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
        
    #Verificación de idioma es
    def verifyTranslationProduct1(self):
        df1 = self.AllProducts
        df2 = self.translationProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_es = df2[df2["LanguageId"].str.contains("es",na=False)]
        result1 = new_df1[~new_df1["ItemNumber"].isin(df_es["ProductNumber"])]
        x1 ,y1 = result1.shape
        
        if x1>0:
            print("-- Total prod. sin traducciones1 encontrados:" ,x1)
            data = result1[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    #Verificación del idioma es-MX
    def verifyTranslationProduct2(self):
        df1 = self.AllProducts
        df2 = self.translationProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_mx = df2[df2["LanguageId"].str.contains("es-MX",na=False)]
        result2 = new_df1[~new_df1["ItemNumber"].isin(df_mx["ProductNumber"])]
        x2 ,y2 = result2.shape
        if x2>0:
            print("-- Total prod. sin traducciones2 encontrados:" ,x2)
            data = result2[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    #Verificación de los que no tienen idioma registrado
    def verifyTranslationProduct3(self):
        df1 = self.AllProducts
        df2 = self.translationProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        result3= new_df1[~new_df1["ItemNumber"].isin(df2["ProductNumber"])] # No esta registrado ni MX ni ES para el product
        x3 ,y3 = result3.shape
        if x3>0:
            print("-- Total prod. sin traducciones3 encontrados:" ,x3)
            data = result3[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    #Verificación de productos inactivos 
    def verifyProductsInStateActive(self):
        try:
            df1 = self.AllProducts
            df2 = self.listProductsSell
            df3 = self.productsInactive
            df4 = self.categoryProducts
            if 'ItemId' in df2.columns:
                new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
                result = df2[~df2["ItemId"].isin(new_df1["ItemNumber"])]
                result_1 = df3[df3["ItemNumber"].isin(result["ItemId"])]
                x , y = result.shape
                if x>0:
                    print("-- Total prod. vendidos con estado inactivo encontrados:" ,x)
                    data = result_1[["ItemNumber","SearchName"]] 
                    return data
            else: 
                return pd.DataFrame({})
        except Exception as e:
            # Manejar la excepción
            print(f"Se produjo un error: {e}")    
    
    #Verificación de productos con precio vacio o cero
    def verifyPricesExists(self):
        df1 = self.priceProducts
        df2 = self.AllProducts
        df4 = self.categoryProducts
        new_df2 = df2[df2["ItemNumber"].isin(df4["ProductNumber"])]
        result = df1[(df1['Price'] == 0) | (df1['Price'] == '')]
        # print(result)
        result_1 = pd.merge(new_df2,result,left_on='ItemNumber',right_on='ItemNumber')
        # result_1["error"] = result_1["PriceWarehouseId"] + " | "+ result_1["QuantityUnitySymbol"]
        x , y = result_1.shape
        if x>0:
            print("-- Total prod. con precio vacio o cero encontrados:" ,x)
            data = result_1[["ItemNumber","SearchName"]]
            return data
        else: 
            return pd.DataFrame({})
    
    #Verificación de contenido de los campos descripción y nombre del producto
    def verifyTranslationProductosEmptyFields(self):
        df1 = self.translationProducts
        df2 = self.AllProducts
        df4 = self.categoryProducts
        new_df2 = df2[df2["ItemNumber"].isin(df4["ProductNumber"])]
        # Crear una máscara booleana para identificar filas con campos vacíos
        result = df1[(df1['ProductName'].str.strip() == '') | (df1['Description'].str.strip() == '')]
        
        # Realizar la unión entre df2 y empty_fields_df en base a 'ItemNumber' y 'ProductNumber'
        result_1 = pd.merge(new_df2, result, left_on='ItemNumber', right_on='ProductNumber')
        
        if not result_1.empty:
            print("Hay productos con campos de descripción o nombre del producto vacíos en traducciones de texto.")
            # Seleccionar las columnas necesarias del DataFrame resultante
            data = result_1[['ItemNumber', 'SearchName']]  # Aquí selecciona las columnas correctas
            return data
        else: 
            print("No se encontraron productos con campos de descripción o nombre del producto vacíos en traducciones de texto.")
            return pd.DataFrame({})
    
    #Verificación que todos los productos desde unidad contengan U y hasta unidad contenga U.
    def verifyFromToUnitSymbol(self):
        df1 = self.AllProducts
        df2 = self.unitConvertionProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        
        # Filtrar df2 para encontrar filas donde "FromUnitSymbol" contiene 'U' y "ToUnitSymbol" contiene 'U.'
        df_unit = df2[(df2["FromUnitSymbol"].str.contains("U", na=False)) & (df2["ToUnitSymbol"].str.contains("U.", na=False))]

        # Filtrar df1 para encontrar productos que no tienen conversiones con las unidades deseadas
        result = new_df1[~new_df1["ItemNumber"].isin(df_unit["ProductNumber"])]
        
        excluded_item_numbers = self.exceptu_andU
        
        result = result[~result["ItemNumber"].isin(excluded_item_numbers)]

        if not result.empty:
            print(f"-- Total productos sin 'U' y 'U.' encontrados en desde y hasta: {result.shape[0]}")
            data = result[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos sin 'U' y 'U.' en las conversiones de unidades.")
            return pd.DataFrame({})
    
    #Verificar que tipo de producto sea artículo
    def verifyProductType(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        #Verificar que todos los productos creados tengan como tipo de producto artículo:
        df_tyProd = new_df1[~(new_df1["ProductType"].str.contains("Item", na=False))]
        if not df_tyProd.empty:
            print(f"-- Total productos que el tipo de producto no es Artículo: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos sin el tipo de producto Artículo")
            return pd.DataFrame({})
    
    #verificar que subtipo de producto sea Producto
    def verifyProductSubType(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        #Verificar que todos los productos creados tengan como tipo de producto artículo:
        df_tyProd = new_df1[~(new_df1["ProductSubType"].str.contains("Product", na=False))]
        if not df_tyProd.empty:
            print(f"-- Total productos que el subtipo de producto no es Producto: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos sin el subtipo de producto Producto")
            return pd.DataFrame({})
    
    #Verificar que el tipo de servicio de producto sea "No especificado"
    def verifyServiceType(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        #Verificar que todos los productos creados tengan como tipo de producto artículo:
        df_tyProd = new_df1[~(new_df1["ServiceType"].str.contains("NotSpecified", na=False))]
        if not df_tyProd.empty:
            print(f"-- Total productos que el tipo de servicio no es No especificado: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos que el tipo de servicio no es No especificado.")
            return pd.DataFrame({})
    
    #Verificar que los campos de nombre del producto, nombre de busqueca y descripción no esten vacios
    def verifyNameFields(self):
        df1 = self.productCreations
        df2 = self.AllProducts
        df4 = self.categoryProducts
        new_df2 = df2[df2["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = df1[(df1['ProductName'].str.strip() == '') | (df1['ProductSearchName'].str.strip() == '') | (df1['ProductDescription'].str.strip() == '')]
        
        result_1 = pd.merge(new_df2, df_tyProd, left_on='ItemNumber', right_on='ProductNumber')
        
        if not result_1.empty:
            print(f"-- Total productos con algún campo de identificación adicional vacio: {result_1.shape[0]}")
            data = result_1[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con algún campo de identificación adicional vacio.")
            return pd.DataFrame({})
    
    #Verificar que los campos de grupo de dimensiones de almacenamiento sea SiteWHL
    def verifyStorageDimensionGroupName(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1["StorageDimensionGroupName"].str.contains("SiteWHL", na=False))]
        if not df_tyProd.empty:
            print(f"-- Total productos con el grupo de dimensiones de almacenamiento distinto a SiteWHL: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el grupo de dimensiones de almacenamiento distinto a SiteWHL.")
            return pd.DataFrame({})
    
    #Verificar que los campos de grupo de dimensiones de seguimiento sea Ninguno
    def verifyTrackingDimensionGroupName(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1["TrackingDimensionGroupName"].str.contains("Ninguno", na=False))]
        if not df_tyProd.empty:
            print(f"-- Total productos con el grupo de dimensiones de seguimiento distinto a Ninguno: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el grupo de dimensiones de seguimiento distinto a Ninguno.")
            return pd.DataFrame({})
    
    #Verificar que los campos de grupo de modelos de artículo sea PROD
    def verifyItemModelGroupId(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1["ItemModelGroupId"].str.contains("PROD", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con el grupo de modelos de artículo distinto a PROD: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron  productos con el grupo de modelos de artículo distinto a PROD.")
            return pd.DataFrame({})
    
    #Verificar que la unidad del pedido de compra no sea igual a U.
    def verifyPurchaseUnitSymbol(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[(new_df1["PurchaseUnitSymbol"].str.contains("U.", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con la unidad del pedido de compra iguales a U.: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con la unidad del pedido de compra iguales a U..")
            return pd.DataFrame({})
    
    #Verificar que la unidad del pedido de ventas no sea igual a U.
    def verifySalesUnitSymbol(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[(new_df1["SalesUnitSymbol"].str.contains("U.", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con la unidad del pedido de venta iguales a U.: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con la unidad del pedido de venta iguales a U..")
            return pd.DataFrame({})
    
    #Verificar que el grupo de impuestos de artículos en compras no este vacio
    def verifyPurchaseSalesTaxItemGroupCode(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        result = new_df1[(new_df1['PurchaseSalesTaxItemGroupCode'] == '')]
        if not result.empty:
            print(f"-- Total productos con el campo de grupo de impuestos de artículos vacios en compras: {result.shape[0]}")
            data = result[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el campo de grupo de impuestos de artículos vacios en compras.")
            return pd.DataFrame({})
    
    #Verificar que el grupo de impuestos de artículos en ventas no este vacio
    def verifySalesSalesTaxItemGroupCode(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        result = new_df1[(new_df1['SalesSalesTaxItemGroupCode'] == '')]
        if not result.empty:
            print(f"-- Total productos con el campo de grupo de impuestos de artículos vacios en ventas: {result.shape[0]}")
            data = result[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el campo de grupo de impuestos de artículos vacios en ventas.")
            return pd.DataFrame({})
    
    #Verificar que le unidad de inventario en administrar inventario sea U.
    def verifyInventoryUnitSymbol(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1["InventoryUnitSymbol"].str.contains("U.", na=False))]
        
        excluded_item_numbers = self.except_inventUnitSymbol
        
        df_tyProd = df_tyProd[~df_tyProd["ItemNumber"].isin(excluded_item_numbers)]
        if not df_tyProd.empty:
            print(f"-- Total productos con la unidad de inventario distintos a U.: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            
            return data
        else:
            print("No se encontraron productos con la unidad de inventario distintos a U..")
            return pd.DataFrame({})
    
    #Verificar que el grupo de artículos sea GA001
    def verifyProductGroupId(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1["ProductGroupId"].str.contains("GA001", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con el grupo de artículos distinto a GA001: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el grupo de artículos distinto a GA001.")
            return pd.DataFrame({})
    
    #Verificar que todos los productos tengan peso neto
    def verifyNetProductWeight(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        result = new_df1[(new_df1['NetProductWeight'] == '') | (new_df1['NetProductWeight'] == 0)]
        if not result.empty:
            print(f"-- Total productos con peso neto vacio o igual a 0: {result.shape[0]}")
            data = result[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con peso neto vacio o igual a 0.")
            return pd.DataFrame({})
    
    #Verificar campo de entrega incompleta en transfererencia de pedidos de medidas de peso sea igual a 100 
    def verifyTransferOrderUnderdeliveryPercentage(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1['TransferOrderUnderdeliveryPercentage'] == 100) ]
        if not df_tyProd.empty:
            print(f"-- Total productos con el campo de entrega incompleta en transferencia de pedidos distinto a 100: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el campo de entrega incompleta en transferencia de pedidos distinto a 100.")
            return pd.DataFrame({})
    
    #Verificar que el grupo de cobertura de Plan sea Grupo:
    def verifyProductCoverageGroupId(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1['ProductCoverageGroupId'] == 'Grupo')]
        if not df_tyProd.empty:
            print(f"-- Total productos con el grupo de cobertura de Plan distinto a Grupo: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el grupo de cobertura de Plan distinto a Grupo.")
            return pd.DataFrame({})
    
    #Verificar que tipo de producción en planificación de formula en aplicar ingeniería tiene que ser ninguno:
    def verifyProductionType(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1['ProductionType'] == 'None') ]
        if not df_tyProd.empty:
            print(f"-- Total productos con el tipo de producción en planificación de formula ditinto a ninguno: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el tipo de producción en planificación de formula ditinto a ninguno.")
            return pd.DataFrame({})
    
    #Verificar que el código iternacional sea igual al código SUNAT en datos Perú
    def verifyCodeProduct(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1['DPCodProductSUNAT_PE'] == new_df1['DPCodeCUBSO_PE'])]
        if not df_tyProd.empty:
            print(f"-- Total productos con el código iternacional distinto al código sunat: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el código iternacional distinto al código sunat.")
            return pd.DataFrame({})
    
    #Verificar que el código internacional y el código SUNAT tengan 8 dígitos:
    def verifyCodeProductWithEightDigits(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        # Filtrar filas donde la longitud de 'DPCodProductSUNAT_PE' no sea 8
        df_tyProd = new_df1[((new_df1['DPCodProductSUNAT_PE'].astype(str).str.len() != 8) | (new_df1['DPCodeCUBSO_PE'].astype(str).str.len() != 8))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con el código internacional o el código SUNAT distinto a 8 dígitos: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con el código internacional o el código SUNAT distinto a 8 dígitos.")
            return pd.DataFrame({})
    
    #Verificar que el el último precio de compra en actualización del precio en Compra sea Sí 
    def verifyIsPurchasePriceAutomaticallyUpdated(self):
        df1 = self.AllProducts
        
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        
        df_tyProd = new_df1[~(new_df1["IsPurchasePriceAutomaticallyUpdated"].str.contains("Yes", na=False))]
        if not df_tyProd.empty:
            print(f"-- Total productos con último precio de compra en actualización del precio en Compra distintos a Sí: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con último precio de compra en actualización del precio en Compra distintos a Sí.")
            return pd.DataFrame({})
    
    #Verificar que permitir ajuste de precios en Vender sea No
    def verifyIsSalesPriceAdjustmentAllowed(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        
        df_tyProd = new_df1[~(new_df1["IsSalesPriceAdjustmentAllowed"].str.contains("No", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con permitir ajustes de precios en Vender distinto a No: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con permitir ajustes de precios en Vender distinto a No.")
            return pd.DataFrame({})
    
    #Verificar que ultimo precio de coste en gestionar costes este marcado como Sí
    def verifyIsUnitCostAutomaticallyUpdated(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        
        df_tyProd = new_df1[~(new_df1["IsUnitCostAutomaticallyUpdated"].str.contains("Yes", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con ultimo precio de coste en gestionar costes distinto a Sí: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con ultimo precio de coste en gestionar costes distinto a Sí.")
            return pd.DataFrame({})
    
    #Verificar que evitar los descuentos manuales en comercio sea igual a Sí
    def verifyIsManualDiscountPOSRegistrationProhibited(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        
        df_tyProd = new_df1[~(new_df1["IsManualDiscountPOSRegistrationProhibited"].str.contains("Yes", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con evitar los descuentos manuales en comercio distinto a Sí: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con evitar los descuentos manuales en comercio distinto a Sí.")
            return pd.DataFrame({})
    
    #Verificar que especificar precio en comercio tiene que ser iguar a "No se debe especificar el precio"
    def verifyKeyInQuantityRequirementsAtPOSRegister(self):
        df1 = self.AllProducts
        df4 = self.categoryProducts
        new_df1 = df1[df1["ItemNumber"].isin(df4["ProductNumber"])]
        df_tyProd = new_df1[~(new_df1["KeyInPriceRequirementsAtPOSRegister"].str.contains("NoPrice", na=False))]
        
        if not df_tyProd.empty:
            print(f"-- Total productos con especificar precio en comercio distintos a No se debe especificar el precio: {df_tyProd.shape[0]}")
            data = df_tyProd[["ItemNumber", "SearchName"]]
            return data
        else:
            print("No se encontraron productos con especificar precio en comercio distintos a No se debe especificar el precio.")
            return pd.DataFrame({})
    
    ######
    
    #region PricesProducts
    def getPricesProducts(self):
        #Definir url
        path = f"{self.url}/data/PurchasePriceAgreements"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$select=ItemNumber,Price"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion

    #region AllProducts
    def getAllProducts(self):
        #Definir url
        path = f"{self.url}/data/ReleasedProductsV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$filter=ProductLifecycleStateId eq 'ACTIVO' &$select=ItemNumber,ItemModelGroupId,ProductSubType,InventoryUnitSymbol,ProductLifecycleStateId,PurchaseUnitSymbol,ProductGroupId,DPCodProductSUNAT_PE,SearchName,NetProductWeight,PurchaseUnderdeliveryPercentage,TransferOrderUnderdeliveryPercentage,ProductionType,ProductCoverageGroupId,DPCodeCUBSO_PE,ProductType,ServiceType,StorageDimensionGroupName,TrackingDimensionGroupName,ItemModelGroupId,SalesUnitSymbol,PurchaseSalesTaxItemGroupCode,SalesSalesTaxItemGroupCode,IsPurchasePriceAutomaticallyUpdated,IsSalesPriceAdjustmentAllowed,IsUnitCostAutomaticallyUpdated,IsManualDiscountPOSRegistrationProhibited,KeyInPriceRequirementsAtPOSRegister"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                        
                # Lista de ItemNumbers a excluir
                excluded_item_numbers = [102449, 102452, 110353, 110354, 110355, 110356, 110357,
                                        110358, 110359, 110360, 110361, 700039, 700039, 700039]

                # Filtrar elementos con ItemNumbers en la lista de exclusión
                result = [item for item in result if item["ItemNumber"] not in excluded_item_numbers]
                
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region AllProductsInactive
    def getAllProductsInactive(self):
        #Definir url
        path = f"{self.url}/data/ReleasedProductsV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$filter=ProductLifecycleStateId eq 'INACTIVO' &$select=ItemNumber,SearchName"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetBarcode
    def getBarcodeProduct(self):
        #Definir url
        path = f"{self.url}/data/ProductBarcodesV3"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$select=ItemNumber,ProductQuantityUnitSymbol,BarcodeSetupId,Barcode,ProductDescription"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetCategoriesProduct
    def getCategoryProduct(self):
        #Definir url
        path = f"{self.url}/data/ProductCategoryAssignments"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$filter=ProductCategoryHierarchyName eq 'Catalogo Ventas' &$select=ProductNumber"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetCategoriesProduct
    def getTraslationProduct(self):
        #Definir url
        path = f"{self.url}/data/ProductTranslations"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                        
                        # Lista de ItemNumbers a excluir
                excluded_item_numbers = [102449, 102452, 110353, 110354, 110355, 110356, 110357,
                                        110358, 110359, 110360, 110361, 700039, 700039, 700039]

                # Filtrar elementos con ItemNumbers en la lista de exclusión
                result = [item for item in result if item.get("ItemNumber") not in excluded_item_numbers]
                
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetCategoriesProduct
    def getListProvidersProducts(self):
        #Definir url
        path = f"{self.url}/data/ProductApprovedVendors"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetUnitConvertionProducts
    def getUnitConversionProducts(self):
        #Definir url
        path = f"{self.url}/data/ProductSpecificUnitOfMeasureConversions"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion

    #region GetProductCreations
    def getProductsCreations(self):
        #Definir url
        path = f"{self.url}/data/ReleasedProductCreationsV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true &$select=ProductNumber,ProductName,ProductSearchName,ProductDescription"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion

    #region getWarehouses
    def getWarehouses(self):
        #Definir url
        path = f"{self.url}/data/WarehousesOnHandV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true &$select=ItemNumber,InventoryWarehouseId"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion