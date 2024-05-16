from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from functions.DAG018.modules.modulo1 import Modulo1
from functions.DAG018.functions.api_dynamics import ApiDynamics
from functions.DAG018.functions.enviar_correos import EnviarCorreos
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["cristian.espinoza@terranovatrading.com.pe"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

ListaExBarCode = [102449, 102452, 110353, 110354, 110355, 110356, 110357,110358, 110359, 110360, 110361,
                700039, 101803,107163,700023,112205,101293,101598,102453,104859,104860,104874,104875,104876,
                107717,107947,108525,108786,108892,110381,111222,111732,111757,111759,111762,111760,111765,
                111761,111767,101292,112011,112014,112073,112134,112135,112144,112146,112183,112201,112253,
                112268,112280,112298,112314,112318,112322,112323,112332,112476,112478,112479,101799,106265,
                110494,112595,110972,112599,112600,112601,112602,112603,112604,112605,112608,112609]

ListaExandU = [100051,100054,100067,100170,100198,100199,100260,100687,100688,100775,100776,100777,100780,
                100783,100788,100789,100790,100792,100795,100800,100801,100804,101763,101790,101799,101801,101803,
                101804,101805,101806,103912,103914,103915,103916,105094,105095,105096,105097,105515,105518,106970,
                107163,107165,108282,108586,108796,109318,109327,109351,110016,110017,110018,110019,110020,110021,
                110022,110023,110025,110027,110028,110225,110349,110715,107167,111179,111995,112104,112177,112190,
                112205,112497]

ListaExinventUnitSymbol =[100051,100054,100067,100170,100198,100199,100260,100687,100688,100775,100776,100777,100780,100783,100788,
                            100789,100790,100792,100795,100800,100801,100804,101763,101790,101799,101801,101803,101804,101805,101806,
                            103912,103914,103915,103916,105094,105095,105096,105097,105515,105518,106970,107163,107165,108282,108586,
                            108796,109318,109327,109351,110016,110017,110018,110019,110020,110021,110022,110023,110025,110027,110028,
                            110225,110349,110715,107167,111179,111995,112104,112177,112190,112205,112497,112595]

# Obtener los valores de las variables de Airflow
barcodeExtrac = Variable.get("barCode", deserialize_json=True)
unitExtrac = Variable.get("andU", deserialize_json=True)
unitsymbolExtrac = Variable.get("inventUnitSymbol", deserialize_json=True)



listaTotalBarcode = ListaExBarCode + barcodeExtrac
listaTotalU = ListaExandU + unitExtrac
listaTotalunitSymbol = ListaExinventUnitSymbol + unitsymbolExtrac

def execute():
    try:
        api = ApiDynamics(listaTotalBarcode, listaTotalU, listaTotalunitSymbol)
        api.ejecutar_funciones()
        modulo = Modulo1(api)
        tipo_verificacion, ruta_archivo =  modulo.Start()
        ####
        if len(tipo_verificacion) != 0:
            p_attach = ruta_archivo
            correo = EnviarCorreos(tipo_verificacion,p_attach)
            correo.enviarCorreo()
            print("correos enviados")
        else:
            print("no hay errores")
        
    except Exception as e:
        print(f"Error: {e}")

with DAG(
    "DAG_validador_productos",
    default_args=default_args,
    description="VALIDADOR DE PRODUCTOS",
    schedule_interval="0 8,14 * * *",
    start_date=datetime(2024, 5, 13, 8, 0, 0),
    tags=["DAG_validador_productos"],
) as dag:
    scrape_task = PythonOperator(task_id="ejecutar_aplicacion", python_callable=execute)
