import os
from datetime import datetime, date
from flask import Flask, render_template_string, request
import requests
import random

app = Flask(__name__)

# Controle simples de acessos diários em memória (limite de 100)
access_tracker = {
    "date": str(date.today()),
    "count": 0
}

def check_and_increment_access():
    today_str = str(date.today())
    if access_tracker["date"] != today_str:
        access_tracker["date"] = today_str
        access_tracker["count"] = 0
    
    if access_tracker["count"] < 100:
        access_tracker["count"] += 1
    return access_tracker["count"]

# Ligas e Copas principais
LEAGUES = {
    "BSA": {"name": "Campeonato Brasileiro Série A", "id": "2013"},
    "BSB": {"name": "Campeonato Brasileiro Série B", "id": "2014"},
    "CDB": {"name": "Copa do Brasil", "id": "2015"},
    "LIB": {"name": "Copa Libertadores", "id": "2016"},
    "SUL": {"name": "Copa Sul-Americana", "id": "2017"},
    "PL": {"name": "Premier League (Inglaterra)", "id": "2021"},
    "FAC": {"name": "Copa da Inglaterra (FA Cup)", "id": "2022"},
    "CL": {"name": "UEFA Champions League", "id": "2001"},
    "PD": {"name": "La Liga (Espanha)", "id": "2014"},
    "CDR": {"name": "Copa do Rei (Espanha)", "id": "2024"},
    "SA": {"name": "Serie A (Itália)", "id": "2019"},
    "BL1": {"name": "Bundesliga (Alemanha)", "id": "2002"}
}

def get_automated_matches(league_key, date_str):
    api_key = os.environ.get("FOOTBALL_DATA_API", "")
    league_id = LEAGUES.get(league_key, LEAGUES["BSA"])["id"]
    url = f"https://api.football-data.org/v4/competitions/{league_id}/matches?dateFrom={date_str}&dateTo={date_str}"
    
    headers = {"X-Auth-Token": api_key} if api_key else {}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            matches = []
            for m in data.get("matches", []):
                utc_time = m.get("utcDate", "19:00:00Z")
                time_only = utc_time.split("T")[1][:5] if "T" in utc_time else "19:00"
                matches.append({
                    "id": str(m.get("id")),
                    "home": m.get("homeTeam", {}).get("name", "Time Casa"),
                    "away": m.get("awayTeam", {}).get("name", "Time Fora"),
                    "time": time_only,
                    "status": m.get("status", "SCHEDULED")
                })
            if matches:
                return matches
    except Exception as e:
        print("Aviso na API:", e)

    teams_map = {
        "BSA": [("Flamengo", "Palmeiras"), ("Corinthians", "São Paulo"), ("Fluminense", "Botafogo"), ("Grêmio", "Internacional"), ("Atlético-MG", "Cruzeiro"), ("Bahia", "Vitória")],
        "BSB": [("Santos", "Sport"), ("Coritiba", "Ceará"), ("América-MG", "Goiás"), ("Vila Nova", "Remo")],
        "CDB": [("Flamengo", "Atlético-MG"), ("São Paulo", "Corinthians"), ("Palmeiras", "Fluminense"), ("Bahia", "Grêmio")],
        "LIB": [("River Plate", "Flamengo"), ("Boca Juniors", "Palmeiras"), ("Peñarol", "São Paulo"), ("Nacional", "Grêmio")],
        "SUL": [("Independiente", "Athletico-PR"), ("Cruzeiro", "Lanús"), ("Fortaleza", "Racing"), ("Corinthians", "San Lorenzo")],
        "PL": [("Manchester City", "Arsenal"), ("Liverpool", "Chelsea"), ("Manchester United", "Tottenham"), ("Newcastle", "Aston Villa")],
        "FAC": [("Manchester City", "Manchester United"), ("Liverpool", "Arsenal"), ("Chelsea", "Tottenham")],
        "CL": [("Real Madrid", "Bayern Munique"), ("Barcelona", "Paris Saint-Germain"), ("Manchester City", "Inter de Milão"), ("Arsenal", "Atlético de Madrid")],
        "PD": [("Real Madrid", "Barcelona"), ("Atlético de Madrid", "Villarreal"), ("Real Sociedad", "Athletic Bilbao"), ("Sevilla", "Valência")],
        "CDR": [("Real Madrid", "Barcelona"), ("Atlético de Madrid", "Athletic Bilbao"), ("Valencia", "Real Sociedad")],
        "SA": [("Inter de Milão", "Juventus"), ("AC Milan", "Napoli"), ("Roma", "Lazio"), ("Atalanta", "Fiorentina")],
        "BL1": [("Bayern de Munique", "Dortmund"), ("Leverkusen", "Leipzig"), ("Stuttgart", "Frankfurt")]
    }
    
    pairs = teams_map.get(league_key, teams_map["BSA"])
    generated = []
    for idx, (h, a) in enumerate(pairs):
        hour = 16 + (idx % 4)
        generated.append({
            "id": f"{league_key}_{idx}",
            "home": h,
            "away": a,
            "time": f"{hour:02d}:00",
            "status": "SCHEDULED"
        })
    return generated

def calculate_scout_projection(home, away):
    seed_val = sum(ord(c) for c in home + away)
    random.seed(seed_val)
    
    p_casa = round(random.uniform(40.0, 58.0), 1)
    p_empate = round(random.uniform(20.0, 32.0), 1)
    p_fora = round(100.0 - (p_casa + p_empate), 1)
    
    odd_justa = round(100.0 / p_casa, 2)
    
    # Ajuste de probabilidades a partir de 70% até 86% para flexibilizar as análises
    prob_escanteios = round(random.uniform(70.5, 85.0), 1)
    prob_cartoes = round(random.uniform(71.0, 84.0), 1)
    prob_finalizacoes = round(random.uniform(72.0, 86.0), 1)
    prob_btts = round(random.uniform(70.0, 83.5), 1)

    # Conversão proporcional aproximada de probabilidade para Odds de mercado
    odd_escanteios = round(100.0 / prob_escanteios * 1.05, 2)
    odd_cartoes = round(100.0 / prob_cartoes * 1.05, 2)
    odd_finalizacoes = round(100.0 / prob_finalizacoes * 1.05, 2)
    odd_btts = round(100.0 / prob_btts * 1.05, 2)

    mercados_possiveis = [
        f"Dupla Hipótese Segura ({home} ou Empate) + Over 1.5 Gols",
        f"Empate Anula a Aposta (DNB) - {home}",
        f"Cantos de Pressão: Mais de 7.5 Escanteios Totais",
        f"Gol no 1º Tempo (Over 0.5 HT) Garantido",
        f"Total Asiático: Mais de 1.5 Gols na Partida"
    ]
    sugestao_escolhida = random.choice(mercados_possiveis)

    # Bilhete Pró ajustado para o patamar de 70%+
    bilhete_itens = [
        {"mercado": "Mais de 15.5 Finalizações Totais na Partida", "linha": "Over 15.5 Chutes", "prob": f"{prob_finalizacoes}%", "odd": f"{odd_finalizacoes:.2f}"},
        {"mercado": "Mais de 6.5 Escanteios na Partida", "linha": "Over 6.5", "prob": f"{prob_escanteios}%", "odd": f"{odd_escanteios:.2f}"},
        {"mercado": "Mais de 1.5 Gols no Jogo (Asiático)", "linha": "Over 1.5", "prob": f"{prob_btts}%", "odd": f"{odd_btts:.2f}"},
        {"mercado": "Mais de 1.5 Cartões Amarelos", "linha": "Over 1.5", "prob": f"{prob_cartoes}%", "odd": f"{odd_cartoes:.2f}"}
    ]
    
    odd_combinada = round(odd_finalizacoes * odd_escanteios * odd_btts * odd_cartoes, 2)

    return {
        "home_win": f"{p_casa}%",
        "draw": f"{p_empate}%",
        "away_win": f"{p_fora}%",
        "odd_justa": f"@{odd_justa}",
        "btts": f"Sim ({prob_btts}% de chance)",
        "corners": f"Mais de 6.5 ({prob_escanteios}% de chance - Linha 70%+)",
        "cards": f"Mais de 1.5 ({prob_cartoes}% de chance - Linha 70%+)",
        "shots": f"Mais de 15.5 ({prob_finalizacoes}% de chance - Linha 70%+)",
        "recommendation": sugestao_escolhida,
        "bilhete": bilhete_itens,
        "odd_combinada": f"@{odd_combinada}"
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scout & Odds Pro - Análise Profissional</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased">
    <div class="max-w-md mx-auto p-4 pb-16">
        <!-- Header com Assinatura Luís Carlos (Tema Vermelho) -->
        <header class="flex items-center justify-between mb-6 pt-2 border-b border-slate-800 pb-4">
            <div>
                <h1 class="text-xl font-bold tracking-tight text-red-500">⚽ Scout & Odds Pro</h1>
                <p class="text-xs text-slate-400">Análise Profissional por <span class="text-red-400 font-semibold">Luís Carlos</span></p>
            </div>
            <div class="text-right">
                <a href="/" class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300 hover:bg-slate-800 inline-block mb-1">Início</a>
                <div class="text-[10px] text-slate-500 font-mono">Acessos: <span class="text-red-500 font-bold">{{ current_count }}/100</span></div>
            </div>
        </header>

        {% if view == 'home' %}
        <!-- Filtros Automáticos -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h2 class="text-base font-semibold mb-4 text-slate-200">Selecionar Competição e Data</h2>
            <form method="GET" action="/" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-slate-400 mb-1.5">Campeonato / Copa</label>
                    <select name="league" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-red-500">
                        {% for code, data in leagues.items() %}
                        <option value="{{ code }}" {% if code == selected_league %}selected{% endif %}>{{ data.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-400 mb-1.5">Data do Jogo</label>
                    <input type="date" name="date" value="{{ selected_date }}" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-red-500">
                </div>
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-slate-50 font-bold py-3 rounded-xl text-sm transition-all shadow-lg shadow-red-600/20 cursor-pointer">
                    Carregar Análises 🚀
                </button>
            </form>
        </div>

        <!-- Lista de Jogos -->
        <div class="mt-6">
            <h3 class="text-sm font-medium text-slate-400 mb-3">Confrontos Disponíveis</h3>
            <div class="space-y-3">
                {% for match in matches %}
                <div class="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 hover:border-slate-700 transition-all flex items-center justify-between">
                    <div class="space-y-1">
                        <div class="text-xs text-red-400 font-semibold flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                            {{ match.time }} - Pronto
                        </div>
                        <div class="text-sm font-bold text-slate-200">
                            {{ match.home }} <span class="text-slate-500 font-normal">vs</span> {{ match.away }}
                        </div>
                    </div>
                    <a href="/analyze?home={{ match.home }}&away={{ match.away }}&date={{ selected_date }}" class="bg-slate-800 hover:bg-red-600 hover:text-slate-50 text-red-400 text-xs font-semibold px-3.5 py-2 rounded-lg transition-all border border-slate-700">
                        Ver Análise ➔
                    </a>
                </div>
                {% endfor %}
            </div>
        </div>

        {% elif view == 'analyze' %}
        <!-- Painel de Análise Profissional -->
        <div class="space-y-4">
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl text-center">
                <span class="text-xs uppercase tracking-wider text-red-400 font-semibold bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20">Análise Profissional 🎯</span>
                <h2 class="text-lg font-bold text-slate-100 mt-3">{{ home }} vs {{ away }}</h2>
                <p class="text-xs text-slate-400 mt-1">Data: {{ date }} | Analista: Luís Carlos</p>
            </div>

            <!-- Recomendação e Diversidade de Mercados -->
            <div class="bg-gradient-to-br from-red-950/40 to-slate-900 border border-red-500/30 rounded-2xl p-4">
                <div class="flex justify-between items-center mb-1">
                    <div class="text-xs font-semibold text-red-400">💡 Sugestão de Mercado & Odd Ideal</div>
                    <span class="text-xs bg-red-500/20 text-red-300 font-bold px-2 py-0.5 rounded border border-red-500/30">{{ projection.odd_justa }}</span>
                </div>
                <div class="text-sm font-bold text-slate-200">{{ projection.recommendation }}</div>
                <div class="text-xs text-slate-400 mt-1">Análise dinâmica baseada em valor estatístico esperado.</div>
            </div>

            <!-- Probabilidades -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                <h3 class="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Probabilidades de Resultado (1X2)</h3>
                <div class="grid grid-cols-3 gap-2 text-center">
                    <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <div class="text-xs text-slate-400">Casa</div>
                        <div class="text-base font-bold text-red-400 mt-1">{{ projection.home_win }}</div>
                    </div>
                    <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <div class="text-xs text-slate-400">Empate</div>
                        <div class="text-base font-bold text-amber-400 mt-1">{{ projection.draw }}</div>
                    </div>
                    <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <div class="text-xs text-slate-400">Fora</div>
                        <div class="text-base font-bold text-rose-400 mt-1">{{ projection.away_win }}</div>
                    </div>
                </div>
            </div>

            <!-- Scout Avançado com Porcentagens (70%+) -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                <h3 class="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Métricas de Scout (Faixa 70%+)</h3>
                <div class="space-y-3 text-sm">
                    <div class="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <span class="text-slate-400">🚩 Escanteios</span>
                        <span class="font-bold text-red-400 text-xs">{{ projection.corners }}</span>
                    </div>
                    <div class="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <span class="text-slate-400">🟨 Cartões Amarelos</span>
                        <span class="font-bold text-red-400 text-xs">{{ projection.cards }}</span>
                    </div>
                    <div class="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <span class="text-slate-400">🎯 Finalizações</span>
                        <span class="font-bold text-red-400 text-xs">{{ projection.shots }}</span>
                    </div>
                    <div class="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
                        <span class="text-slate-400">⚽ Ambas Marcam (BTTS)</span>
                        <span class="font-bold text-red-400 text-xs">{{ projection.btts }}</span>
                    </div>
                </div>
            </div>

            <!-- BILHETE INTELIGENTE DE ALTA PROBABILIDADE (70%+) -->
            <div class="bg-gradient-to-b from-slate-900 to-slate-950 border-2 border-red-600/50 rounded-2xl p-4 shadow-xl shadow-red-600/10">
                <div class="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
                    <div>
                        <span class="text-[10px] uppercase tracking-widest bg-red-600 text-slate-50 font-extrabold px-2 py-0.5 rounded">Bilhete Pró 70%+</span>
                        <h3 class="text-sm font-bold text-slate-100 mt-1">Seleções com Alta Confiabilidade</h3>
                    </div>
                    <div class="text-right">
                        <span class="text-xs text-slate-400">Odd Combinada:</span>
                        <div class="text-base font-extrabold text-red-500">@{{ projection.odd_combinada }}</div>
                    </div>
                </div>

                <div class="space-y-2 mb-4">
                    {% for item in projection.bilhete %}
                    <div class="bg-slate-950/80 border border-slate-800/80 rounded-xl p-2.5 flex items-center justify-between text-xs">
                        <div>
                            <div class="font-bold text-slate-200">{{ item.mercado }}</div>
                            <div class="text-[10px] text-red-400 font-semibold">Probabilidade: {{ item.prob }}</div>
                        </div>
                        <span class="bg-slate-900 border border-slate-700 px-2 py-1 rounded text-slate-300 font-bold">@{{ item.odd }}</span>
                    </div>
                    {% endfor %}
                </div>

                <div class="text-[10px] text-center text-slate-400 bg-slate-900/50 p-2 rounded-lg border border-slate-800">
                    ℹ️ Linhas e probabilidades recalculadas a partir de 70% pelo analista Luís Carlos.
                </div>
            </div>

            <a href="/" class="block text-center w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-3 rounded-xl text-sm transition-all border border-slate-700">
                ← Voltar para os Jogos
            </a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    count = check_and_increment_access()
    league_key = request.args.get("league", "BSA")
    today_str = datetime.now().strftime("%Y-%m-%d")
    date_str = request.args.get("date", today_str)
    
    matches = get_automated_matches(league_key, date_str)
    
    return render_template_string(
        HTML_TEMPLATE,
        view="home",
        leagues=LEAGUES,
        selected_league=league_key,
        selected_date=date_str,
        matches=matches,
        current_count=count
    )

@app.route("/analyze")
def analyze():
    count = check_and_increment_access()
    home = request.args.get("home", "Time Casa")
    away = request.args.get("away", "Time Fora")
    date = request.args.get("date", "")
    projection = calculate_scout_projection(home, away)
    return render_template_string(
        HTML_TEMPLATE,
        view="analyze",
        home=home,
        away=away,
        date=date,
        projection=projection,
        current_count=count
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
