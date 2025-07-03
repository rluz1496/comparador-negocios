# 📍 Comparador de Negócios Locais

Este projeto é uma ferramenta interativa construída com Streamlit e OpenAI, que permite comparar o seu negócio com concorrentes locais similares, com base em avaliações, localização e categoria. Ideal para donos de pequenos negócios que desejam entender sua posição no mercado local.

---

## 🚀 Funcionalidades

* Busca de empresa no Google Maps (via Serper API)
* Exibição de endereço, categoria e nota média
* Identificação de concorrentes próximos
* Comparação de avaliações recentes via layout estilo "kanban"
* Análise de IA com sugestões baseadas nas avaliações usando o modelo GPT-4o-mini da OpenAI

---

## 🧠 Requisitos

* Python 3.10+
* Conta gratuita na [Serper API](https://serper.dev/) para realizar buscas no Google Maps
* Chave de API da OpenAI com acesso ao modelo `gpt-4o-mini`

---

## ⚙️ Instalação

1. Clone o repositório:

```bash
git clone https://github.com/rluz1496/comparador-negocios.git
cd comparador-negocios
```

2. Crie o arquivo `.env` com suas credenciais:

```env
API_KEY=CHAVE_DA_SERPER_API
OPENAI_API_KEY=CHAVE_DA_OPENAI
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
streamlit run app.py
```

---

## 💡 Exemplo de uso

Você digita o nome da sua empresa, seleciona a correta, e o sistema:

* Mostra os dados da sua empresa
* Busca empresas semelhantes próximas com base na categoria e localização
* Mostra as avaliações recentes de todos lado a lado
* Exibe uma análise de IA recomendando melhorias se necessário

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, modificar e compartilhar.

---

Desenvolvido por [Rodrigo Luz](https://github.com/rluz1496) ✨
