import requests
import asyncio
from telegram import Bot

TOKEN = "8714475799:AAERaQlM-KuGQD9h68NBCZfuQ7_2gXQnPg8"
CHAT_ID = "1659054142"
API_KEY = "2b0cac11657acd0a8bd2e0584da76143"

bot = Bot(token=TOKEN)

jogos_alertados = set()


def buscar_jogos():

    url = "https://v3.football.api-sports.io/fixtures?live=all"

    headers = {
        "x-apisports-key": API_KEY
    }

    resposta = requests.get(url, headers=headers)

    dados = resposta.json()

    return dados["response"]


def calcular_probabilidade(minuto, escanteios):

    if minuto is None or minuto == 0:
        return None

    ritmo = escanteios / minuto

    previsao = ritmo * 90

    p35 = min(100, int((previsao / 4) * 100))
    p55 = min(100, int((previsao / 6) * 100))
    p75 = min(100, int((previsao / 8) * 100))

    return p35, p55, p75


def analisar(jogos):

    alertas = []

    for jogo in jogos:

        fixture_id = jogo["fixture"]["id"]

        if fixture_id in jogos_alertados:
            continue

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        minuto = jogo["fixture"]["status"]["elapsed"]

        gols_casa = jogo["goals"]["home"]
        gols_fora = jogo["goals"]["away"]

        escanteios_casa = 0
        escanteios_fora = 0

        try:

            for estat in jogo["statistics"]:

                time = estat["team"]["name"]

                for item in estat["statistics"]:

                    if item["type"] == "Corner Kicks":

                        if time == casa:
                            escanteios_casa = item["value"]

                        if time == fora:
                            escanteios_fora = item["value"]

        except:
            pass

        if escanteios_casa is None:
            escanteios_casa = 0

        if escanteios_fora is None:
            escanteios_fora = 0

        total = escanteios_casa + escanteios_fora

        if minuto is None:
            continue

        if total >= 2 and minuto <= 45:

            prob = calcular_probabilidade(minuto, total)

            if prob is None:
                continue

            p35, p55, p75 = prob

            mensagem = f"""
🚩 ALERTA DE ESCANTEIOS

⚽ {casa} x {fora}

⏱ Minuto: {minuto}

🚩 Escanteios: {total}

📊 Probabilidade estimada:

+3.5 → {p35}%
+5.5 → {p55}%
+7.5 → {p75}%

🔥 Jogo com bom ritmo
"""

            alertas.append(mensagem)

            jogos_alertados.add(fixture_id)

    return alertas


async def enviar(alertas):

    for alerta in alertas:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=alerta
        )


async def main():

    print("BOT ESCANTEIOS PRO ONLINE ⚽")

    while True:

        try:

            jogos = buscar_jogos()

            alertas = analisar(jogos)

            if alertas:
                await enviar(alertas)

        except Exception as erro:

            print("Erro:", erro)

        await asyncio.sleep(60)


asyncio.run(main())