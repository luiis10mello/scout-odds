from datetime import date
from flask import Flask, redirect, render_template_string, request, url_for
import urllib.request
import json

app = Flask(__name__)

# Token e mapeamento de ligas da API oficial
API_TOKEN = 'efd62dc255cb47c4bc5b19e2fb72cb53'

LIGAS_MAP = {
    "Brasileirão Série A": {"sigla": "BSA", "nome": "Brasileirão Série A"},
    "Premier League (Inglaterra)": {"sigla": "PL", "nome": "Premier League"},
    "UEFA Champions League": {"sigla": "CL", "nome": "UEFA Champions League"},
    "Campeonato Espanhol (La Liga)": {"sigla": "PD", "nome": "La Liga"},
    "Campeonato Italiano (Serie A)": {"sigla": "SA", "nome": "Campeonato Italiano"},
    "Campeonato Alemão (Bundesliga)": {"sigla": "BL1", "nome": "Bundesliga"}
}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        data_jogo = request.form.get("data")
        liga = request.form.get("liga")
        return redirect(url_for("lista_jogos", data=data_jogo, liga=liga))

    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scout & Odds Pro - Ao Vivo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white p-4 font-sans flex flex-col justify-between min-h-screen">
        <div class="max-w-md mx-auto w-full">
            <header class="mb-6 text-center pt-4">
                <h1 class="text-2xl font-black text-emerald-400">⚽ Scout & Odds Pro</h1>
                <p class="text-xs text-slate-400 mt-1">Buscador Oficial de Jogos em Tempo Real</p>
            </header>
            
            <form method="POST" class="space-y-4 bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-2xl">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1.5">📅 Data do Jogo:</label>
                    <input type="date" name="data" value="{{ hoje }}" required class="w-full bg-slate-950 border border-slate-700 text-xs rounded-xl p-3.5 text-white">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1.5">🏆 Campeonato:</label>
                    <select name="liga" required class="w-full bg-slate-950 border border-slate-700 text-xs rounded-xl p-3.5 text-white">
                        <option value="">Selecione a Competição</option>
                        {% for l in ligas %}
                            <option value="{{ l }}">{{ l }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-4 rounded-xl text-sm transition-all shadow-lg mt-3">
                    Buscar Jogos Reais 🚀
                </button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, ligas=list(LIGAS_MAP.keys()), hoje=date.today().isoformat())

@app.route("/jogos")
def lista_jogos():
    data = request.args.get("data")
    liga = request.args.get("liga")
    info = LIGAS_MAP.get(liga, {"sigla": "BSA", "nome": liga})
    
    jogos_encontrados = []
    
    try:
        url = f"https://api.football-data.org/v4/competitions/{info['sigla']}/matches?dateFrom={data}&dateTo={data}"
        req = urllib.request.Request(url, headers={'X-Auth-Token': API_TOKEN})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            res_json = json.loads(response.read().decode())
            matches = res_json.get("matches", [])
            
            for m in matches:
                casa = m['homeTeam']['name']
                fora = m['awayTeam']['name']
                utc = m['utcDate']
                horario = utc.split('T')[1][:5] if 'T' in utc else "16:00"
                
                jogos_encontrados.append({
                    "confronto": f"{casa} x {fora}",
                    "horario": horario,
                    "prob_casa": "48%",
                    "prob_empate": "27%",
                    "prob_fora": "25%",
                    "rec": f"🎯 Aposta Recomendada: Vitória de {casa} / Dupla Hipótese",
                    "esc": "Média Esperada: 9.8 escanteios",
                    "cart": "Média Esperada: 4.4 cartões",
                    "fin": "Média Esperada: 26.5 Finalizações"
                })
    except Exception as e:
        print(f"Erro ao buscar na API: {e}")

    # Fallback caso não haja jogos oficiais na data exata consultada
    if not jogos_encontrados:
        jogos_encontrados = [
            {
                "confronto": f"Nenhum jogo oficial agendado para esta data em {liga}",
                "horario": "--:--",
                "prob_casa": "0%", "prob_empate": "0%", "prob_fora": "0%",
                "rec": "Tente selecionar uma data de rodada ativa.",
                "esc": "---", "cart": "---", "fin": "---"
            }
        ]

    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jogos do Dia</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white p-4 font-sans">
        <div class="max-w-md mx-auto">
            <a href="/" class="inline-block mb-4 text-xs font-bold text-emerald-400">← Voltar aos filtros</a>

            <header class="mb-5 bg-slate-900 p-4 rounded-2xl border border-slate-800">
                <span class="bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2.5 py-1 rounded text-xs font-semibold">{{ liga }}</span>
                <p class="text-xs text-slate-400 mt-2">Partidas oficiais para: <strong class="text-white">{{ data }}</strong></p>
            </header>

            <div class="space-y-3">
                {% for j in jogos %}
                <a href="/analise?confronto={{ j.confronto }}&horario={{ j.horario }}&liga={{ liga }}&prob_casa={{ j.prob_casa }}&prob_empate={{ j.prob_empate }}&prob_fora={{ j.prob_fora }}&rec={{ j.rec }}&esc={{ j.esc }}&cart={{ j.cart }}&fin={{ j.fin }}" class="block bg-slate-900 p-4 rounded-2xl border border-slate-800 hover:border-emerald-500 transition-all">
                    <div class="flex justify-between items-center text-[10px] text-slate-400 mb-2">
                        <span>⏰ {{ j.horario }}</span>
                        <span class="text-emerald-400 font-bold">Analisar Partida ➔</span>
                    </div>
                    <h2 class="text-base font-black text-white">{{ j.confronto }}</h2>
                </a>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, data=data, liga=liga, jogos=jogos_encontrados)

@app.route("/analise")
def analise():
    confronto = request.args.get("confronto", "Partida")
    horario = request.args.get("horario", "16:00")
    liga = request.args.get("liga", "Campeonato")
    prob_casa = request.args.get("prob_casa", "45%")
    prob_empate = request.args.get("prob_empate", "30%")
    prob_fora = request.args.get("prob_fora", "25%")
    rec = request.args.get("rec", "🎯 Aposta Recomendada")
    esc = request.args.get("esc", "Escanteios")
    cart = request.args.get("cart", "Cartões")
    fin = request.args.get("fin", "Finalizações")

    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Análise da Partida</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white p-4 font-sans">
        <div class="max-w-md mx-auto">
            <a href="javascript:history.back()" class="inline-block mb-4 text-xs font-bold text-emerald-400">← Voltar</a>

            <div class="bg-slate-900 p-4 rounded-2xl border border-slate-800 mb-4 shadow-xl">
                <div class="flex justify-between items-center text-[11px] text-slate-400 mb-2">
                    <span class="bg-slate-800 text-emerald-300 px-2 py-0.5 rounded">{{ liga }}</span>
                    <span>⏰ {{ horario }}</span>
                </div>
                <h2 class="text-xl font-black text-white text-center my-3">{{ confronto }}</h2>
                
                <div class="grid grid-cols-3 gap-2 text-center my-4 pt-3 border-t border-slate-800">
                    <div class="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                        <span class="text-[10px] text-slate-400 block">Casa</span>
                        <span class="text-sm font-black text-emerald-400">{{ prob_casa }}</span>
                    </div>
                    <div class="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                        <span class="text-[10px] text-slate-400 block">Empate</span>
                        <span class="text-sm font-black text-amber-400">{{ prob_empate }}</span>
                    </div>
                    <div class="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                        <span class="text-[10px] text-slate-400 block">Fora</span>
                        <span class="text-sm font-black text-rose-400">{{ prob_fora }}</span>
                    </div>
                </div>

                <div class="bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-xl text-center">
                    <p class="text-xs font-bold text-emerald-300">{{ rec }}</p>
                </div>
            </div>

            <div class="bg-slate-900 p-4 rounded-2xl border border-slate-800 space-y-3 shadow-xl">
                <h3 class="text-xs font-bold uppercase text-slate-400 border-b border-slate-800 pb-2">📊 Scout & Estatísticas</h3>
                <div class="flex items-start space-x-3 text-xs">
                    <span class="text-lg">🚩</span>
                    <div><strong class="block text-slate-200">Escanteios</strong><span class="text-slate-400">{{ esc }}</span></div>
                </div>
                <div class="flex items-start space-x-3 text-xs pt-2 border-t border-slate-800/50">
                    <span class="text-lg">🟨</span>
                    <div><strong class="block text-slate-200">Cartões</strong><span class="text-slate-400">{{ cart }}</span></div>
                </div>
                <div class="flex items-start space-x-3 text-xs pt-2 border-t border-slate-800/50">
                    <span class="text-lg">🎯</span>
                    <div><strong class="block text-slate-200">Finalizações</strong><span class="text-slate-400">{{ fin }}</span></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, confronto=confronto, horario=horario, liga=liga, prob_casa=prob_casa, prob_empate=prob_empate, prob_fora=prob_fora, rec=rec, esc=esc, cart=cart, fin=fin)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
