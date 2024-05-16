from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class EnviarCorreosCli:

    tipo_ver = []
    path_file = ""

    def __init__(self, tipo_veri, path_attach, fromCorreo,ToCorreo,CCCorreo, password):
        self.tipo_ver = tipo_veri
        self.path_file = path_attach
        self.fromCorreo =  fromCorreo
        self.ToCorreo = ToCorreo
        self.CCCorreo = CCCorreo
        self.password = password

    def enviarCorreo(self):

        # Creando Instancia de correo
        msg = MIMEMultipart()

        # Configurando parametros de envio
        password = self.password
        msg['From'] = self.fromCorreo
        msg['To'] = self.ToCorreo
        msg['Subject'] = "Reporte de Verificación de Extractos"
        msg['CC'] = self.CCCorreo

        # Agregando contenido de mensaje
        # msg.attach(MIMEText(message, 'plain'))
        msg_contenido = ""
        #####
        msg_contenido = msg_contenido+'''<div style="margin-left: 16px;">
            <h3>ERROR DE INGRESO DE CLIENTES:</h3>
            <h2>EL PROPÓSITO DE ESTE MENSAJE ES COMPARTIR LOS CLIENTES QUE PRESENTAN ERRORES PARA QUE PUEDAN SER CORREGIDOS DE MANERA OPORTUNA.
            </h2>
        </div>'''
        if "CLIENTE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Se encontro errores con la cuenta de cliente.</h3>
            <p>Se encontraron clientes afectados los cuales se muestran en el archivo adjunto.
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
            <h2 style="color:white; font-size: 15px; margin-left: 14px;">Reporte de Verificación de Clientes</h2>
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
