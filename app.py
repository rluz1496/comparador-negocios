import os
import json
import http.client
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import openai

# Carregar variáveis
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

def gerar_analise_ia(nome_usuario, nota_usuario, avals_usuario, concorrentes):
    avals_texto = [f"{r.get('rating')} - {r.get('snippet', '')}" for r in avals_usuario if r.get("snippet")]
    concorrentes_texto = []
    for c in concorrentes:
        avals = get_reviews(c["cid"])
        trechos = [f"{r.get('rating')} - {r.get('snippet', '')}" for r in avals if r.get("snippet")]
        concorrentes_texto.append(f"- {c['title']} (nota média: {c.get('rating')}, avaliações: {trechos[:5]})")

    prompt = f"""
Você é um especialista em análise de negócios. Com base nas avaliações e nas notas médias a seguir, forneça uma análise comparativa entre o negócio do usuário e seus concorrentes. 
Diga se o negócio está abaixo da média e, se sim, dê sugestões de melhoria com base nas avaliações. 
Se estiver acima da média, elogie e sugira continuar assim.

Negócio do usuário:
- Nome: {nome_usuario}
- Nota média: {nota_usuario}
- Avaliações: {avals_texto[:5]}

Concorrentes:
""" + "\n".join(concorrentes_texto[:4])

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um consultor de negócios especialista em experiência do cliente."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=700
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

    # Buscar concorrentes
    st.subheader("📰 Concorrentes próximos")
    lat = selecionado["latitude"]
    lng = selecionado["longitude"]
    categoria = selecionado.get("category", "")

    payload_conc = json.dumps({
        "q": categoria,
        "gl": "br",
        "hl": "pt-br",
        "type": "places",
        "location": f"{lat},{lng}",
        "engine": "google",
        "num": 10
    })
    conn = http.client.HTTPSConnection("google.serper.dev")
    conn.request("POST", "/places", payload_conc, HEADERS)
    res = conn.getresponse()
    data = json.loads(res.read())
    concorrentes = data.get("places", [])

    df_concorrentes = pd.DataFrame([{
        "Name": c["title"],
        "Endereço": c.get("address"),
        "Nota Média": c.get("rating"),
        "Avaliações": c.get("ratingCount"),
        "Categoria": c.get("category")
    } for c in concorrentes])
    st.dataframe(df_concorrentes, use_container_width=True)

    st.subheader("📝 Comparativo de Avaliações")
    st.caption("Visualize lado a lado as avaliações recentes do seu negócio e dos concorrentes.")

    colunas = st.columns(len(concorrentes[:4]) + 1)
    with colunas[0]:
        st.markdown(f"#### 🏢 {selecionado['title']}")
        user_reviews = get_reviews(selecionado['cid'])
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

    st.subheader("🤖 Análise da IA")
    with st.spinner("Gerando análise com inteligência artificial..."):
        analise = gerar_analise_ia(
            nome_usuario=selecionado["title"],
            nota_usuario=selecionado.get("rating", "N/A"),
            avals_usuario=user_reviews,
            concorrentes=concorrentes[:4]
        )
        st.markdown(analise)
