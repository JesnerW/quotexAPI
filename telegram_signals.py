import os
import re
import sys
import logging
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

                # Realiza la operación en Quotex
                amount = 1
                # asset = currency_pair.replace("/", "") + "_otc"
                asset = currency_pair.replace()
                duration = 300

                # Asegúrate de que el cliente de Quotex esté conectado antes de realizar la operación
                if not quotex_client.is_connect():
                    check_connect, message = quotex_client.connect()
                    if not check_connect:
                        print(f"No se pudo conectar a Quotex: {message}")
                        continue
                    quotex_client.change_account("PRACTICE")

                status, buy_info = quotex_client.buy(
                    amount, asset, direction, duration)
                print(status, buy_info)

    await client.run_until_disconnected()


async def disconnect():
    await client.disconnect()
    quotex_client.close()

client.loop.run_until_complete(main())
client.loop.run_until_complete(disconnect())
