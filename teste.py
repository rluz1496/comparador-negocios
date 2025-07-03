import http.client
import json
from datetime import datetime
from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import os

load_dotenv()
api_key = os.getenv("APIKEY")

pesquisa = prompt("🔍 Digite o nome da empresa: ")

conn_place = http.client.HTTPSConnection("google.serper.dev")

payloadPlace = json.dumps({
  "q": pesquisa,
  "gl": "br",
  "hl": "pt-br",
  "type": "places",
  "num": 10,
  "page": 1,
  "engine": "google"
})

headers = {
  'X-API-KEY': api_key,
  'Content-Type': 'application/json'
}

conn_place.request("POST", "/places", payloadPlace, headers)
res = conn_place.getresponse()
data = json.loads(res.read())

# Acessa a lista de lugares
places = data.get("places", [])

# Prepara para exibir em tabela
tabela = data.get("places", [])
cid_list = []

for i, place in enumerate(places, start=1):
    titulo = place.get("title")
    endereco = place.get("address", "Sem endereço")
    codigo = place.get("cid")
    categoria = place.get("category")

    print(f"{i}. {titulo} | {endereco} | {categoria} | {codigo}")
    cid_list.append(codigo)

escolha = prompt("🔍 Digite o número da empresa: ")

try:
    indice = int(escolha)
    if 1 <= indice <= len(cid_list):
        cid_selecionado = cid_list[indice -1]
        print(f"\nVocê escolheu o CID: {cid_selecionado}")

        conn_review = http.client.HTTPSConnection("google.serper.dev")

        payloadReview = json.dumps({
            "cid": cid_selecionado,
            "gl": "br",
            "hl": "pt-br",
            "sortBy": "newest"
        })

        conn_review.request("POST", "/reviews", payloadReview, headers)
        res = conn_review.getresponse()
        data = json.loads(res.read())

    else:
        print("Número fora do intervalo")
except ValueError:
    print("Por favor digite um número válido")

reviews = data.get("reviews", [])

print("\nAvaliações recentes:")

for i, review in enumerate(reviews, start=1):
    rating = review.get("rating")
    date = review.get("date")

    iso_raw = review.get("isoDate")
    if iso_raw:
        dt = datetime.fromisoformat(iso_raw.replace("Z", "+00:00"))
        iso_date = dt.strftime("%d/%m/%Y %H:%M")
    else:
        iso_date = "Sem data"

    snippet = review.get("snippet", "Nenhuma avaliação")
    user = review.get("user",{})
    user_name = user.get("name")

    print(f"{i}. ⭐ {rating} | 📅 {date} | {iso_date}")
    print(f"   👤 {user_name}")
    print(f"   💬 {snippet}\n")
