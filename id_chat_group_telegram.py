from telethon import TelegramClient
import os
import sys


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


# Carga las variables de entorno del archivo .env
load_env()

# Accede a las variables de entorno utilizando os.environ
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
phone_number = os.environ['PHONE_NUMBER']
session_name = 'my_session'

client = TelegramClient(session_name, api_id, api_hash)


async def main():
    await client.start(phone_number)
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_group or dialog.is_channel:
            print(f"{dialog.name}: {dialog.id}")

    await client.run_until_disconnected()
client.loop.run_until_complete(main())
