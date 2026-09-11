from datetime import datetime
import os
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# Token gratuito padrão ou chave de API (pode ser configurado na Render depois)
# O football-data.org permite criar uma conta gratuita rápida em football-data.org
API_KEY = os.environ.get("FOOTBALL_DATA_API", "YOUR_API_KEY_HERE")

LEAGUES = {
    "2021": "Premier League (Inglaterra)",
    "2014": "La Liga (Espanha)",
    "2019": "Serie A (Itália)",
    "2003": "Eredivisie (Holanda)",
    "2015": "Ligue 1 (França)",
    "2002": "Bundesliga (Alemanha)",
    "2013": "Campeonato Brasileiro Série A",
    "2001": "UEFA Champions League",
}


def fetch_real_matches(league_code, date_str):
  # Busca automática de confrontos reais via API de futebol
  url = f"https://api.football-data.org/v4/competitions/{league_code}/matches?dateFrom={date_str}&dateTo={date_str}"
  headers = {"X-Auth-Token": API_KEY}

  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      data = response.json()
      matches = []
      for m in data.get("matches", []):
        # Extrai o horário formatado (UTC para local aproximado ou original)
        utc_time = m.get("utcDate", "16:00:00Z")
        time_only = utc_time.split("T")[1][:5] if "T" in utc_time else "16:00"

        matches.append({
            "id": m.get("id"),
            "homeTeam": {"name": m.get("homeTeam", {}).get("name", "Casa")},
            "awayTeam": {"name": m.get("awayTeam", {}).get("name", "Fora")},
            "time": time_only,
            "status": m.get("status", "SCHEDULED"),
        })
      return matches
  except Exception as e:
    print("Erro ao buscar API:", e)

  return []


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scout & Odds Pro - Agenda Automática</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased">
    <div class="max-w-md mx-auto p-4 pb-12">
        <!-- Header -->
        <header class="flex items-center justify-between mb-6 pt-2 border-b border-slate-800 pb-4">
            <div>
                <h1 class="text-xl font-bold tracking-tight text-emerald-400">⚽ Scout & Odds Pro</h1>
                <p class="text-xs text-slate-400">Busca automática de confrontos por data</p>
            </div>
            <a href="/" class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300 hover:bg-slate-800">Início</a>
        </header>

        {% if view == 'home' %}
        <!-- Filtros de Data e Liga -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h2 class="text-base font-semibold mb-4 text-slate-200">Selecionar Competição e Data</h2>
            <form method="GET" action="/" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-slate-400 mb-1.5">Campeonato</label>
                    <select name="league" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500">
                        {% for code, name in leagues.items() %}
                        <option value="{{ code }}" {% if code == selected_league %}selected{% endif %}>{{ name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-400 mb-1.5">Data dos Jogos</label>
                    <input type="date" name="date" value="{{ selected_date }}" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
                <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3 rounded-xl text-sm transition-all shadow-lg shadow-emerald-500/10 cursor-pointer">
                    Buscar Confrontos Automáticos 🚀
                </button>
            </form>
        </div>

        <!-- Lista de Confrontos Encontrados -->
        <div class="mt-6">
            <h3 class="text-sm font-medium text-slate-400 mb-3">Partidas para {{ selected_date }}</h3>
            {% if matches %}
            <div class="space-y-3">
                {% for match in matches %}
                <div class="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 hover:border-slate-700 transition-all flex items-center justify-between">
                    <div class="space-y-1">
                        <div class="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            {{ match.time }} - Oficial
                        </div>
                        <div class="text-sm font-bold text-slate-200">
                            {{ match.homeTeam.name }} <span class="text-slate-500 font-normal">vs</span> {{ match.awayTeam.name }}
                        </div>
                    </div>
                    <a href="/analyze?home={{ match.homeTeam.name }}&away={{ match.awayTeam.name }}&date={{ selected_date }}" class="bg-slate-800 hover:bg-emerald-500 hover:text-slate-950 text-emerald-400 text-xs font-semibold px-3.5 py-2 rounded-lg transition-all border border-slate-700">
                        Analisar ➔
                    </a>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-sm">
                Nenhum confronto oficial encontrado para esta data exata nesta liga. Tente selecionar outra data ou campeonato.
            </div>
            {% endif %}
        </div>

        {% elif view == 'analyze' %}
        <!-- Tela de Análise e Notas para o Confronto -->
        <div class="space-y-4">
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
                <span class="text-xs uppercase tracking-wider text-emerald-400 font-semibold bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">Área de Análise Pessoal</span>
                <h2 class="text-lg font-bold text-slate-100 mt-3">{{ home }} vs {{ away }}</h2>
                <p class="text-xs text-slate-400 mt-1">Data selecionada: {{ date }}</p>
            </div>

            <!-- Bloco de Anotações / Scout do Usuário -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
                <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Caderno de Scout e Estratégia</h3>
                <textarea rows="5" placeholder="Escreva aqui suas anotações de mercado, linhas de escanteios, cartões ou análise pré-live..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-emerald-500 resize-none"></textarea>
                <button onclick="alert('Anotações salvas com sucesso!')" class="w-full bg-slate-800 hover:bg-slate-700 text-emerald-400 font-semibold py-2.5 rounded-xl text-sm transition-all border border-slate-700">
                    Salvar Análise 💾
                </button>
            </div>

            <a href="/" class="block text-center w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-3 rounded-xl text-sm transition-all border border-slate-700">
                ← Voltar para a Agenda
            </a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/")
def index():
  league = request.args.get("league", "2013")  # Padrão Brasileirão
  today_str = datetime.now().strftime("%Y-%m-%d")
  date_str = request.args.get("date", today_str)

  matches = fetch_real_matches(league, date_str)

  return render_template_string(
      HTML_TEMPLATE,
      view="home",
      leagues=LEAGUES,
      selected_league=league,
      selected_date=date_str,
      matches=matches,
  )


@app.route("/analyze")
def analyze():
  home = request.args.get("home", "Time Casa")
  away = request.args.get("away", "Time Fora")
  date = request.args.get("date", "")
  return render_template_string(
      HTML_TEMPLATE, view="analyze", home=home, away=away, date=date
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
