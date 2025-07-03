import os
import json
import http.client
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import openai

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}
openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="Comparador de Negócios Locais", layout="wide")
st.title("📍 Comparador de Negócios Locais")
st.caption("Busque seu negócio e compare com concorrentes similares por categoria e localização.")

query = st.text_input("🔎 Nome do seu negócio", placeholder="Ex: Selva Hamburgueria")

def get_reviews(cid):
    payload = json.dumps({
        "cid": cid,
        "gl": "br",
        "hl": "pt-br",
        "sortBy": "newest"
    })
    conn = http.client.HTTPSConnection("google.serper.dev")
    conn.request("POST", "/reviews", payload, HEADERS)
    res = conn.getresponse()
    data = json.loads(res.read())
    return data.get("reviews", [])

def openai_call(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um consultor de negócios especialista em experiência do cliente."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

if query:
    with st.spinner("🔎 Buscando informações..."):
        payload = json.dumps({
            "q": query,
            "gl": "br",
            "hl": "pt-br",
            "type": "places",
            "num": 10
        })
        conn = http.client.HTTPSConnection("google.serper.dev")
        conn.request("POST", "/places", payload, HEADERS)
        res = conn.getresponse()
        data = json.loads(res.read())
        places = data.get("places", [])

    opcoes = [f"{p['title']} | {p['address']} | {p.get('category', 'Categoria não informada')}" for p in places]
    escolha = st.selectbox("Selecione a empresa", opcoes)
    selecionado = places[opcoes.index(escolha)]

    st.success(f"✅ Encontrado: {selecionado['title']}")
    st.markdown(f"📍 **Endereço:** {selecionado['address']}")
    st.markdown(f"🏷️ **Categoria:** {selecionado.get('category', 'N/A')}")
    st.markdown(f"⭐ **Nota Média:** {selecionado.get('rating', 'N/A')} ({selecionado.get('ratingCount', 0)} avaliações)")
    st.markdown(f"[Abrir no Google Maps](https://www.google.com/maps/search/?api=1&query={selecionado['latitude']},{selecionado['longitude']})")

    # Buscar concorrentes com type=maps e parâmetro ll com zoom
    lat = selecionado["latitude"]
    lng = selecionado["longitude"]
    categoria = selecionado.get("category", "")
    payload_conc = json.dumps({
        "q": categoria,
        "gl": "br",
        "hl": "pt-br",
        "type": "maps",
        "ll": f"@{lat},{lng},14z",
        "num": 10
    })
    conn = http.client.HTTPSConnection("google.serper.dev")
    conn.request("POST", "/search", payload_conc, HEADERS)
    res = conn.getresponse()
    data = json.loads(res.read())
    concorrentes = data.get("places", [])

    df_concorrentes = pd.DataFrame([{
        "Nome": c["title"],
        "Endereço": c.get("address"),
        "Nota Média": c.get("rating"),
        "Avaliações": c.get("ratingCount"),
        "Categoria": c.get("category")
    } for c in concorrentes])
    st.subheader("📊 Concorrentes próximos")
    st.dataframe(df_concorrentes, use_container_width=True)

    st.subheader("📝 Comparativo de Avaliações")
    st.caption("Visualize lado a lado as avaliações recentes do seu negócio e dos concorrentes.")

    colunas = st.columns(len(concorrentes[:4]) + 1)
    user_reviews = get_reviews(selecionado['cid'])
    with colunas[0]:
        st.markdown(f"#### 🏢 {selecionado['title']}")
        for r in user_reviews[:10]:
            nome = r.get("user", {}).get("name", "?")
            nota = r.get("rating", "?")
            data = r.get("date", "")
            texto = r.get("snippet", "")
            st.markdown(f"**⭐ {nota} | 🧍 {nome} | 🕒 {data}**\n> {texto}")

    for idx, concorrente in enumerate(concorrentes[:4], start=1):
        with colunas[idx]:
            st.markdown(f"#### 🏛️ {concorrente['title']}")
            reviews = get_reviews(concorrente['cid'])
            for r in reviews[:10]:
                nome = r.get("user", {}).get("name", "?")
                nota = r.get("rating", "?")
                data = r.get("date", "")
                texto = r.get("snippet", "")
                st.markdown(f"**⭐ {nota} | 🧍 {nome} | 🕒 {data}**\n> {texto}")

    if st.button("🤖 Gerar análise com IA"):
        with st.spinner("Gerando análise com inteligência artificial..."):
            user_avals = [f"{r.get('rating')} - {r.get('snippet', '')}" for r in user_reviews if r.get("snippet")]
            concorrentes_data = []
            for c in concorrentes[:4]:
                avals = get_reviews(c["cid"])
                trechos = [f"{r.get('rating')} - {r.get('snippet', '')}" for r in avals if r.get("snippet")]
                concorrentes_data.append({"nome": c["title"], "nota": c.get("rating"), "reviews": trechos[:5]})

            partes = []
            partes.append(openai_call(f"Compare a nota média do negócio '{selecionado['title']}' ({selecionado.get('rating')}) com os concorrentes: {[(c['nome'], c['nota']) for c in concorrentes_data]}"))
            partes.append(openai_call(f"Analise as avaliações dos clientes do negócio '{selecionado['title']}' e identifique pontos fortes e fracos: {user_avals[:5]}"))
            partes.append(openai_call(f"Com base nas avaliações dos concorrentes ({[(c['nome'], c['nota']) for c in concorrentes_data]}), diga o que os clientes elogiam mais e o que pode ser aprendido."))
            partes.append(openai_call(f"Sugira melhorias para o negócio '{selecionado['title']}' com base nas comparações anteriores."))
            partes.append(openai_call(f"Escreva uma conclusão executiva com base em todas as análises anteriores sobre o negócio '{selecionado['title']}'."))

            st.subheader("🧠 Análise da IA")
            for i, parte in enumerate(partes):
                st.info(parte)
