import os
import re
import sys
import logging
import asyncio
import datetime
import pytz
from telethon import TelegramClient, events
from quotexapi.stable_api import Quotex

logging.basicConfig(level=logging.WARNING)
logging.getLogger('telethon').setLevel(logging.CRITICAL)


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


async def main():
    await client.start(phone_number)
    print("Sesión iniciada correctamente.")

    signal_pattern = re.compile(r'(\w{3}/\w{3});(\d{2}:\d{2});(CALL|PUT)')

    @client.on(events.NewMessage(chats=(int(os.environ['ID_GRUPO_CHAT']))))
    async def handle_signal(event):
        message = event.message.message
        for line in message.splitlines():
            match = signal_pattern.match(line)
            if match:
                currency_pair = match.group(1)
                time = match.group(2)
                direction = match.group(3)

                print(f"Señal de trading: {currency_pair} {time} {direction}")

                # Obtén la fecha actual en GTM-3
                gmt_3 = pytz.timezone("Etc/GMT+3")
                current_date_gmt_3 = datetime.datetime.now(gmt_3).date()

                # Convierte la hora de la señal a un objeto datetime
                signal_time = datetime.datetime.strptime(time, "%H:%M")

                # Combina la fecha actual con la hora de la señal
                signal_time_gmt_3 = gmt_3.localize(
                    datetime.datetime.combine(
                        current_date_gmt_3, signal_time.time())
                )

                # Convierte la hora de la señal a GTM-5 (hora local)
                gmt_5 = pytz.timezone("Etc/GMT+5")
                signal_time_local = signal_time_gmt_3.astimezone(gmt_5)

                # Calcular el tiempo restante antes de que se ejecute la operación
                now_local = datetime.datetime.now(gmt_5)
                time_remaining = signal_time_local - now_local

                # if check_connect:
                #     monto = 1
                #     WinLose = None
                #     for _ in range(3):  # Realiza la operación un máximo de 3 veces
                #         # Lanzar la operación aquí (tu código existente)
                #         quotex_client.change_account(
                #             "PRACTICE")  # PRACTICE - REAL
                #         asset = currency_pair.replace(
                #             "/", "") + "_otc"  # "EURUSD_otc"
                #         amount = monto
                #         direction = direction.lower()  # call or put miniscula
                #         duration = 10  # in seconds
                #         buy_info = quotex_client.buy(
                #             amount, asset, direction, duration)
                #         idOperation = buy_info[1]["id"]  # id operation
                #         WinLose = quotex_client.check_win(
                #             idOperation)  # win = True, lose = False
                #         print(amount, asset, direction, duration)
                #         if WinLose:  # Si ganó, salir del bucle
                #             print("Saldo actual: ",
                #                   quotex_client.get_balance())
                #             break
                #         else:  # Si perdió, duplicar el monto de la apuesta
                #             WinLose = None
                #             monto *= 2

                # Asegurarse de que el tiempo restante sea positivo
                if time_remaining.total_seconds() > 0:
                    print("Operacion Capturada, lanzando en: ", time_remaining)

                    await asyncio.sleep(time_remaining.total_seconds())
                    print("Operacion lanzada: ", signal_time_local)

                    if check_connect:

                        monto = 1
                        WinLose = None

                        for _ in range(3):  # Realiza la operación un máximo de 3 veces
                            # Lanzar la operación aquí (tu código existente)
                            quotex_client.change_account(
                                "PRACTICE")  # PRACTICE - REAL
                            asset = currency_pair.replace(
                                "/", "") + "_otc"  # "EURUSD_otc"
                            amount = monto
                            direction = direction.lower()  # call or put miniscula
                            duration = 10  # in seconds
                            buy_info = quotex_client.buy(
                                amount, asset, direction, duration)
                            idOperation = buy_info[1]["id"]  # id operation
                            WinLose = quotex_client.check_win(
                                idOperation)  # win = True, lose = False
                            print(amount, asset, direction, duration)

                            if WinLose:  # Si ganó, salir del bucle
                                print("Saldo actual: ",
                                      quotex_client.get_balance())
                                break
                            else:  # Si perdió, duplicar el monto de la apuesta
                                WinLose = None
                                monto *= 2

                    print("Saldo actual: ", quotex_client.get_balance())
                else:
                    print(
                        "La hora de la señal ya ha pasado, no se ejecutará la operación.")

    await client.run_until_disconnected()


async def disconnect():
    await client.disconnect()
    quotex_client.close()


async def disconnect():
    await client.disconnect()
    quotex_client.close()

try:
    client.loop.run_until_complete(main())
finally:
    client.loop.run_until_complete(disconnect())
