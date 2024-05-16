from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class EnviarCorreos:

    tipo_ver = []
    path_file = ""

    def __init__(self, tipo_veri, path_attach):
        self.tipo_ver = tipo_veri
        self.path_file = path_attach

    def enviarCorreo(self):

        # Creando Instancia de correo
        msg = MIMEMultipart()

        # Configurando parametros de envio
        password = "huaraz2024.."
        msg['From'] = "cristian.espinoza@terranovatrading.com.pe"
        msg['To'] = "estefano.espinoza@terranovatrading.com.pe"
        msg['Subject'] = "Reporte de Verificación de Productos"
        msg['CC'] = "katherine.rodriguez@terranovatrading.com.pe;logistica@terranovatrading.com.pe"

        # Agregando contenido de mensaje
        # msg.attach(MIMEText(message, 'plain'))
        msg_contenido = ""
        #####
        msg_contenido = msg_contenido+'''<div style="margin-left: 16px;">
            <h1>PRINCIPALES
            </h1>
            <p>Estos errores deben ser solucionados inmediatamente.</p>
            <p>De no mostrarse ningun error en este modulo considerar los errores secundarios.
            </p>
            <p><i>Los principales se mostrarán antes de la línea amarilla.</i></p>
        </div>'''
        if "BARCODE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin código de barra</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "DUPLICATEBARCODE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con códigos de barra duplicados</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "UNIT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con error asignación de unidades de medida</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "STATUS_ACTIVE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos vendidos con estado INACTIVO</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "UNITSYMBOL" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin 'U' Y 'U.' en la conversión de unidades.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "SALESUNITSYMBOL" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con la Unidad en Pedido de ventas igual a 'U.'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "SALESPRICEADJUSTMENT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con 'permitir ajustes de precios' marcado como 'Sí'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "INVENTORYUNITSYMBOL" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con la unidad en administrar inventario distinto a 'U.'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "KEYINQUANTITY" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de Especificar precio de Comercio distinto a 'No se debe especificar el precio'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "ISMANUALDISCOUNT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con Evitar los descuentos manuales de Comercio marcados como 'No'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        
        
        msg_contenido = msg_contenido+'''<div style="margin-left: 16px;">
            <h1>SECUNDARIOS
            </h1>
            <p>Estos errores deben ser solucionados pero no son de vital importancia. 
            </p>
        </div>'''
        
        
        if "PROVIDER" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin proveedores asignados</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "TRANSLATION" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con campo de traducciones incompletas</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PRICE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin asignación de precios</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "TRANSLATIONNAMEPRODUCT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con la descripción o el nombre del producto en traducciones vacio.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        
        if "PRODUCTTYPE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que no tienen 'Artículo' en el campo de Tipo de producto en general.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PRODUCTSUBTYPE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que no tienen 'Producto' en el campo de Subtipo de producto en general.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "SERVICETYPE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que no tienen 'No especificado' en el campo de Tipo de servicio de producto en General.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "NAMEFIELDS" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que tienen alguno de los campos de Nombre del producto, nombre de búsqueda o descripción vacios.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "STORAGEDIMENSION" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que tienen el campo de Grupo de dimensiones de almacenamiento distinto a 'SiteWHL'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "DIMENSIONGROUPNAME" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que tienen el campo de Grupo de dimensiones de seguimiento distinto a 'Ninguno'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "ITEMMODEL" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos que tienen el campo de Grupo de modelos de artículo distinto a 'PROD'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PURCHASEUNITSYMBOL" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con la Unidad en Pedido de compra igual a 'U.'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PURCHASESALESTAXITEM" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de grupo de impuestos de artículos en 'compra' vacios.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "SALESSALESTAXITEM" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de grupo de impuestos de artículos en 'vender' vacios.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PURCHASEPRICEAUTOMATICALL" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con 'ultimo precio de compra' marcado como 'No'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        
        if "NETPRODUCT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin peso neto.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "ORDERUNDERDE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de 'entrega icompleta' en 'administrar inventario' distinto a '100.00'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PRODUCTIONTYPE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de Tipo de producción en Aplicar ingeniería distinto a 'Ninguno'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PRODUCTCOVERAGE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de Grupo de cobertura de Plan distinto a 'Grupo'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PRODUCTGROUPID" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con el campo de Grupo de artículos de Gestionar costes es distinto a 'GA001'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "UNITCOSTAUTOMATICALLY" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con Ultimo precio de coste de Gestionar costes marcado como 'No'.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "CODEPRODUCTVERIFY" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con código iternacional y código productos Sunat distintos.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "CODEPRODUCTEIGHT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con código productos sin 8 dígitos.</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        
        #####
        msg.attach(MIMEText('''
                                <!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;font-size: 14px;">
    <div style="padding:20px 0px;width: 100%; height: 100%;">
        <img src="https://trujillodatalake.blob.core.windows.net/public/img/logo.png" style="height: 100px;">
        <div style="background-color:#F44336;padding-top: 1px;padding-bottom: 1px;margin-top: 10px; margin-bottom: 20px;">
            <h2 style="color:white; font-size: 15px; margin-left: 14px;">Reporte de Verificación de Productos</h2>
        </div>
        '''+msg_contenido+'''
    </div>
    <div style="margin-left: 14px; margin-top: 5px; font-size: 14px;">
            <span>El presente correo electrónico fue generado por un proceso automático, para más información o inconveniente por favor comuniquese con el área de Tecnología.
                <br><br>Saludos.
            </span>
        </div>
</body>
</html>''', 'html'))
        #####
        self.attach_file_to_email(msg, self.path_file)
        #####
        try:
            # Creando servidor
            server = smtplib.SMTP('smtp.outlook.com: 587')
            server.starttls()

            # Direccion de envio "DE"
            server.login(msg['From'], password)
            # Agregando CC
            emails = f"{msg['To']}, {msg['CC']}".split(",")
            # emails = f"{msg['To']}".split(",")

            # Direccion de envio "PARA"
            server.sendmail(msg['From'], emails, msg.as_string())
            server.quit()
        except Exception as e:
            print(e)
        else:
            print("Correo enviado correctamente a", (msg['To']))

    def attach_file_to_email(self, email_message, filename):
        # Abriendo archivo
        with open(filename, "rb") as f:
            file_attachment = MIMEApplication(f.read())
        # Agregamos archivo en cabecera
        file_name = filename.split("/")[-1]
        file_attachment.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}",
        )
        # Agregamos el archivo en el mensaje
        email_message.attach(file_attachment)
