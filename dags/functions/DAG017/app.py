def execute_application(ApiDynamics,EnviarCorreos,EnviarCorreosCli):
    import os
    import pandas as pd
    import openpyxl
    from openpyxl.utils.dataframe import dataframe_to_rows
    from datetime import datetime
    from airflow.models import Variable
    
    # inicmomos nuestra lista de transacciones con errores
    transacciones_con_errores = []
    lista_numeros_extractos = None
    transacciones_con_errores_extractos = None
    
    ###Extraccion de datos del Airflow
    usuarioFrom = str(Variable.get("fromCorreo"))
    contra = str(Variable.get("passwordC"))
    #Valores para correo de Extractos
    toEx = str(Variable.get("ToCorreoExtractos"))
    CCCEx = str(Variable.get("CCCorreoExtractos"))
    #Valores para correo de Clientes
    toCli = str(Variable.get("ToCorreoCliente"))
    CCCCli = str(Variable.get("CCCorreoClientes"))

    print(" --- Iniciando la ejecucion del aplicativo --")
    ap = ApiDynamics()
    
    print("\n1- VALIDACION - MODULO TRANSACCIONES DE LA TIENDA")
    transacciones_tienda = ap.getTransaccionesDeLaTienda()
    if transacciones_tienda is not False:
        print("Si se encontraron errores en las transacciones de la tienda.")
        lista_numero_transaccion = transacciones_tienda["numero_transaccion"].tolist()
        transacciones_con_errores.extend(lista_numero_transaccion)
    else:
        print("No se encontraron errores en las transacciones de la tienda.")



    print("\n\n2- VALIDACION - MODULO EXTRACTOS")
    extractos_errores = ap.getExtractosErrores()
    if extractos_errores is not False:
        print("Si se encontraron errores en los extractos.")
        lista_numeros_extractos = extractos_errores["numero_extracto"].tolist()
    else:
        print("No se encontraron errores en los extractos.")
        

    print("2.1- Obtencion de transacciones con errores")
    if lista_numeros_extractos is not None:
        print("obteniendo transacciones con errores")
        transacciones_con_errores_extractos = ap.consultarTransaccionesExtractos(lista_numeros_extractos)
    else:
        print("no se consultan las transacciones de los errores de extractos.")

    if transacciones_con_errores_extractos is not None:
        print("se añaden las transacciones de la tienda a la lista actual")
        lista_numero_transaccion_extractos = transacciones_con_errores_extractos["numero_transaccion"].tolist()
        transacciones_con_errores.extend(lista_numero_transaccion_extractos)
    else:
        print("no se añaden las transacciones de la tienda a la lista actual.")
        

    # punto crucial 
    # - si no hay errores finaliza 
    # - si hay errores continua con la verificacion
    if not transacciones_con_errores:
        print("No hay transacciones con errores")
    else:
        transacciones_con_errores = list(set(transacciones_con_errores))
        print(transacciones_con_errores)
        print("La lista no está vacía.")
        print("\n\n3- VALIDACION - MODULO TRANSACCIONES DE LA VENTA")
        df_transacciones_venta = ap.consultarTransaccionesDeVentas(transacciones_con_errores) #Numero de la transacción, codigo del producto, unidad vendida, almacen y nombre producto
        if df_transacciones_venta is not False:
            print("Si se encontraron transacciones de venta con errores.")
            print(df_transacciones_venta)
        else:
            print("No se encontraron transacciones de venta con errores.")

        productos_validacion_unidades = ap.consultarUnidades(df_transacciones_venta)
        print("\n\n4- VALIDACION - MODULO CONVERSION DE UNIDADES")
        if productos_validacion_unidades is not False:
            print("Si se realizo la validacion de conversion de unidades.")
            print(productos_validacion_unidades)
        else:
            print("No se encontraron transacciones de venta con errores.")
            

        print("\n\n5- VALIDACION - MODULO ALMACENES")
        productos_validacion_almacenes = ap.consultarAlmacenes(df_transacciones_venta)
        if productos_validacion_almacenes is not False:
            print("Si se realizo la validacion de almacenes.")
            print(productos_validacion_almacenes)
        else:
            print("No se realizo la validacion de almacenes.")
        

        print("\n\n6- VALIDACION - MODULO SITIO ALMACEN")
        productos_sitio_almacen = ap.SendVerifySiteLocation(df_transacciones_venta)
        if productos_sitio_almacen is not False:
            print("Si se realizo la validacion de sitio y almacén.")
            print(productos_sitio_almacen)
        else:
            print("No se realizo la validacion de sitio y almacén.")

        print("\n\n7- VALIDACION - ERROR EN LA UNIDAD DE INVENTARIO")
        error_unidad_inventario = ap.verifyInventoryUnitSymbol(df_transacciones_venta)
        if error_unidad_inventario is not False:
            print("Si se realizo la validacion de errores en la unidad de inventario.")
            print(error_unidad_inventario)
        else:
            print("No se realizo la validacion de errores en la unidad de inventario.")
        
        print("\n\n8- VALIDACION - ERROR EN TRANSACCIONES DE LA TIENDA")
        productos_error_transacciones = ap.SendVerifyExtractError(df_transacciones_venta)
        if productos_error_transacciones is not False:
            print("Si se realizo la validacion de errores de transacciones de la tienda.")
            print(productos_error_transacciones)
        else:
            print("No se realizo la validacion de errores de transacciones de la tienda.")
        
        

        verificacion = pd.DataFrame({})
        
        tipo_verificacion = []
        seed_cell_excel = 10
        # Obtener la ruta al directorio 'assets' desde 'modulo1.py'
        ruta_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
        
        # Construir la ruta al archivo Excel dentro de la carpeta 'assets'
        ruta_archivo = os.path.join(ruta_assets, 'model_reporte.xlsx')
        
        data_sheet = openpyxl.load_workbook(ruta_archivo)
        sheet = data_sheet.active
        sheet['C5']= datetime.now()
        ####
        colum_l=['D','E','F','G','H','I']
        count_f = 0
        ##Seleccion de columnas
        df_transacciones = pd.DataFrame(df_transacciones_venta)
        columnas_seleccionadas = ['numero_transaccion','num_extracto','codigo_producto','nombre_producto','unidad_vendida','almacen']
        selected_columns = df_transacciones[columnas_seleccionadas]
        
        ##Asignación de valores
        
        UNIDADES = df_transacciones[df_transacciones['verificacion_unidad'] == False]
        ALMACENES = df_transacciones[df_transacciones['validacion_almacen'] == False]
        SITIO_ALAMACEN = df_transacciones[df_transacciones['validacion_sitio_almacen'] == False]
        INVENTORY_UNIT = df_transacciones[df_transacciones['validar_unidad'] == False]
        ERROR_TRANSACCION = df_transacciones[(df_transacciones['validacion_error_transaccion'] != 'None')]
        UNIQUE_ERROR_TRANSACCION = ERROR_TRANSACCION.drop_duplicates(subset='numero_transaccion')
        ##Reportando errores con la unidad
        if not UNIDADES.empty:
            result_unidades = UNIDADES[selected_columns]
            ##
            tipo_verificacion.append("UNIDAD")
            ##
            rows = dataframe_to_rows(result_unidades,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "La unidad del producto no existe en el campo de conversión de unidades."
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1
        ##Reportando errores con el almacen
        if not ALMACENES.empty:
            # # Lista de columnas a seleccionar
            result_almacen = ALMACENES[columnas_seleccionadas]
            ##
            tipo_verificacion.append("ALMACENES")
            # Seleccionar las columnas del DataFrame ALMACENES
            ##
            rows = dataframe_to_rows(result_almacen,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "El almacén no existe para la unidad del producto."
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1
        ##Reportando errores con el sitio y almacen 
        if not SITIO_ALAMACEN.empty:
            result_sitio = SITIO_ALAMACEN[selected_columns]
            ##
            tipo_verificacion.append("SITIO_ALAMACEN")
            ##
            rows = dataframe_to_rows(result_sitio,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "El 'Almacén' no coincide con el 'Sitio' que debería de tener asignado."
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1
        ##Reportando errores con la unidad de inventario
        if not INVENTORY_UNIT.empty:
            result_inventory = INVENTORY_UNIT[selected_columns]
            ##
            tipo_verificacion.append("INVENTORY_UNIT")
            ##
            rows = dataframe_to_rows(result_inventory,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "LA 'UNIDAD' EN 'ADMINISTRAR INVENTARIO' ES DISTINTO A 'U.'"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1
        
        if not UNIQUE_ERROR_TRANSACCION.empty:
            tipo_verificacion.append("ERROR_TRANSACCION")
            for index, row in UNIQUE_ERROR_TRANSACCION.iterrows():
                num_row = seed_cell_excel + count_f
                sheet[f'B{num_row}'] = count_f + 1

                # Obtener el texto del error con el separador '|'
                error_text = row['validacion_error_transaccion']

                # Dividir el texto en líneas usando '|' como separador
                lines = error_text.split('|')

                # Escribir cada línea en la misma celda, utilizando saltos de línea
                if lines:
                    # Escribir la primera línea en la celda C[num_row]
                    sheet[f'C{num_row}'].alignment = openpyxl.styles.Alignment(wrap_text=True)
                    sheet[f'C{num_row}'].value = lines[0]

                    # Si hay más líneas, escribir cada línea adicional en la misma celda en filas siguientes
                    if len(lines) > 1:
                        for line_index in range(1, len(lines)):
                            next_row = num_row + line_index
                            sheet[f'C{next_row}'].alignment = openpyxl.styles.Alignment(wrap_text=True)
                            sheet[f'C{next_row}'].value = lines[line_index]

                # Escribir las otras columnas seleccionadas en las celdas D[num_row], E[num_row], ...
                count_c = 0
                columun = ['numero_transaccion']
                for col in columun:
                    sheet[f'{chr(ord("D") + count_c)}{num_row}'] = row[col]
                    count_c += 1
                
                # Incrementar count_f según el número de líneas escritas o 1 si no hay líneas adicionales
                count_f += len(lines) if lines else 1
        
        # Obtener la ruta al directorio 'assets' desde 'modulo1.py'
        ruta_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

        ruta_archivo = os.path.join(ruta_assets, 'RerporteVerificacion.xlsx')

        data_sheet.save(ruta_archivo)
        ####
        if len(tipo_verificacion) != 0:
            p_attach = ruta_archivo
            correo = EnviarCorreos(tipo_verificacion,p_attach, usuarioFrom, toEx, CCCEx, contra)
            correo.enviarCorreo()
            print("correos enviados")
        else:
            print("no hay errores")
    
    ruta_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
    print("\n\n9- VALIDACION - CUENTA DE CLIENTES")
    client_error = ap.verifyClient()
    if client_error.empty != True:
        print(client_error)
        print("Si se encontraron errores en los clientes.")
    else:
        print("No se encontraron errores en los clientes.")

    # Construir la ruta al archivo Excel dentro de la carpeta 'assets'
    ruta_archivo_clien = os.path.join(ruta_assets, 'model_reporte_cliente.xlsx')
    
    data_sheet = openpyxl.load_workbook(ruta_archivo_clien)
    sheet = data_sheet.active
    sheet['C5']= datetime.now()
    ####
    colum_l=['C','D','E']
    count_f = 0
    seed_cell_excel = 10
    tipo_verificacion_cliente = []
    if client_error.empty != True:
        ##
        tipo_verificacion_cliente.append("CLIENTE")
        ##
        rows = dataframe_to_rows(client_error,index=False)
        for r_i, row in enumerate(rows,1):
            if r_i != 1:
                num_row = seed_cell_excel + count_f
                sheet[f'B{num_row}'] = count_f+1
                count_c = 0
                for c_i, value in enumerate(row,1):
                    sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                    count_c = count_c+1
                count_f = count_f+1

    # Construir la ruta al archivo Excel dentro de la carpeta 'assets'
    ruta_archivo = os.path.join(ruta_assets, 'RerporteVerificacionCliente.xlsx')    
    data_sheet.save(ruta_archivo)
    ####
    if len(tipo_verificacion_cliente) != 0:
        p_attach = ruta_archivo
        correo = EnviarCorreosCli(tipo_verificacion_cliente,p_attach, usuarioFrom, toCli, CCCCli, contra)
        correo.enviarCorreo()
        print("correos enviados")
    else:
        print("no hay errores")
