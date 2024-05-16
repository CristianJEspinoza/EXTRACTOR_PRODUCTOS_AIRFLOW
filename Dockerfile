FROM apache/airflow:2.5.3

ADD requirements.txt .
RUN pip install -r requirements.txt

# Cambiar al usuario root
USER root

# Actualizar e instalar paquetes necesarios
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    unixodbc \
    unixodbc-dev \
    ca-certificates \
    sudo

# Agregar claves y repositorios de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg \
    && sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list'

# Instalar el driver ODBC de SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Comando opcional: instalar las herramientas de SQL Server (sqlcmd y bcp)
# RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
# RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Limpiar el caché de APT
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Establecer variables de entorno para el driver ODBC
ENV ODBCINI=/etc/odbc.ini
ENV ODBCSYSINI=/etc