import os
import re
import sys
import logging
import asyncio
import datetime
from telethon import TelegramClient, events
from quotexapi.stable_api import Quotex

# logging.basicConfig(level=logging.WARNING)
# logging.getLogger('telethon').setLevel(logging.CRITICAL)


def load_env(file_path='.env'):
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if '#' in line:
                    line = line.split('#')[0].strip()
                if '=' in line:
                    name, value = line.split('=', 1)
                    os.environ[name] = value
    except FileNotFoundError:
        print(f"Archivo .env no encontrado en la ruta {file_path}.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al cargar el archivo .env: {e}")
        sys.exit(1)


load_env()

api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
phone_number = os.environ['PHONE_NUMBER']
session_name = 'my_session'

client = TelegramClient(
    session_name,
    api_id,
    api_hash,
    connection_retries=None,
    auto_reconnect=True
)

# Inicia sesión en Quotex y crea el objeto
quotex_email = os.environ['CORREO']
quotex_password = os.environ['PASSWORD']
quotex_client = Quotex(email=quotex_email, password=quotex_password)
quotex_client.debug_ws_enable = False
check_connect, message = quotex_client.connect()
print(check_connect, message)

def convertir_a_segundos_telegram(hora):
    h, m = map(int, hora.split(':'))
    return h * 3600 + m * 60

def convertir_a_segundos_PC():
    #recibo de telegram en GTM -3 y mi PC esta a GTM -5, entonces el de telegram esta 2 horas adelantado, asi que aumentare 2 horas
    aumentar_segundos = 7200 # 7200 segundos = 2 horas
    hora_actual = datetime.datetime.now().time()
    h, m, s = map(int, hora_actual.strftime("%H:%M:%S").split(':'))
    return h * 3600 + (m * 60) + s + aumentar_segundos

async def main():
    await client.start(phone_number)
    print("Sesión iniciada correctamente.")

    signal_pattern = re.compile(r'(\w{3}/\w{3});(\d{2}:\d{2});(CALL|PUT)')

    @client.on(events.NewMessage(chats=(int(os.environ['ID_GRUPO_CHAT']))))
    async def handle_signal(event):
        messages = event.message.message
        for line in messages.splitlines():
            match = signal_pattern.match(line)
            if match:
                currency_pair = match.group(1)
                time = match.group(2)
                type_operation = match.group(3)

                print(
                    f"Señal de trading: {currency_pair} {time} {type_operation}")

                #time a segundos recibidos de telegram GTM -3
                segundos_recibidos = convertir_a_segundos_telegram(time)
                segundos_local = convertir_a_segundos_PC()
                tiempo_faltante = segundos_recibidos - segundos_local

                async def execute_trade():
                    #print(check_connect, message)
                    monto = 1
                    WinLose = None
                    for _ in range(3):  # Realiza la operación un máximo de 3 veces
                        # Lanzar la operación aquí (tu código existente)
                        quotex_client.change_account("PRACTICE")  # PRACTICE - REAL
                        asset = currency_pair.replace("/", "") + "_otc"  # "EURUSD_otc"
                        amount = monto
                        direction = type_operation.lower()  # call or put miniscula
                        duration = 10  # in seconds
                        print(amount, asset, direction, duration)
                        buy_info = quotex_client.buy(amount, asset, direction, duration)
                        idOperation = buy_info[1]["id"]  # id operation
                        WinLose = quotex_client.check_win(idOperation)  # win = True, lose = False

                        if WinLose:  # Si ganó, salir del bucle
                            print("Saldo actual: ",
                                    quotex_client.get_balance())
                            break
                        else:  # Si perdió, duplicar el monto de la apuesta
                            WinLose = None
                            monto *= 2
                
                if tiempo_faltante > 0:
                    print("Operacion Capturada, lanzando en: ", tiempo_faltante)
                    await asyncio.sleep(tiempo_faltante)
                    await execute_trade()
                else:
                    print(
                        "La hora de la señal ya ha pasado, no se ejecutará la operación.")

    await client.run_until_disconnected()


async def disconnect():
    await client.disconnect()
    quotex_client.close()

try:
    client.loop.run_until_complete(main())
finally:
    client.loop.run_until_complete(disconnect())