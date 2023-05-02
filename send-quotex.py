import os
import sys
from quotexapi.stable_api import Quotex


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

client = Quotex(email=os.environ['CORREO'], password=os.environ['PASSWORD'])
client.debug_ws_enable = False
check_connect, message = client.connect()
print(check_connect, message)
if check_connect:
    # client.change_account("PRACTICE")
    # amount = 1
    # asset = "AUDCAD_otc"  # "EURUSD_otc"
    # direction = "call"  # call or put minuscula
    # duration = 10  # in seconds
    # status, buy_info = client.buy(amount, asset, direction, duration)
    # print(status, buy_info)
    # print("Saldo corrente: ", client.get_balance())
    # print("Saindo...")
    monto = 1
    for _ in range(3):
        client.change_account(
            "PRACTICE")  # PRACTICE - REAL
        asset = "AUDCAD_otc"  # "EURUSD_otc"
        amount = monto
        direction = "call"  # call or put miniscula
        duration = 10  # in seconds
        buy_info = client.buy(
            amount, asset, direction, duration)
        idOperation = buy_info[1]["id"]
        stado_compra = client.check_win(idOperation)

        if stado_compra:  # Si ganó, salir del bucle
            print("Saldo actual: ", client.get_balance())
            client.close()
            break
        else:  # Si perdió, duplicar el monto de la apuesta
            stado_compra = None
            monto *= 2
