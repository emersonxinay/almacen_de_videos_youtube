
import time
import os

# Reloj que se actualice cada sugundo


def actualiza_hora():

    while True:
        hora = time.strftime("%H:%M:%S")
        os.system("cls")
        print(hora)
        time.sleep(1)


# Convertir cualquier segundo a días
def convertir_segundo(seg):
    dias = seg//86400
    seg %= 86400
    horas = seg//3600
    seg %= 3600
    minutos = seg//60
    seg %= 60
    return f": {dias} dias,  {horas} horas, {minutos} minutos,{seg} segundos"


# Invocando las funciones


calcula = int(input("ingrese los segundos a convertir: "))
print(convertir_segundo(calcula))

actualiza_hora()
