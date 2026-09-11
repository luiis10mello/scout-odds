def calculate_scout_projection(home, away):
    seed_val = sum(ord(c) for c in home + away)
    random.seed(seed_val)
    
    p_casa = round(random.uniform(40.0, 58.0), 1)
    p_empate = round(random.uniform(20.0, 32.0), 1)
    p_fora = round(100.0 - (p_casa + p_empate), 1)
    
    odd_justa = round(100.0 / p_casa, 2)
    
    prob_escanteios = round(random.uniform(81.0, 94.0), 1)
    prob_cartoes = round(random.uniform(80.0, 92.0), 1)
    prob_finalizacoes = round(random.uniform(82.0, 95.0), 1) # Alta probabilidade
    prob_btts = round(random.uniform(80.5, 91.0), 1)

    mercados_possiveis = [
        f"Dupla Hipótese Segura ({home} ou Empate) + Over 1.5 Gols",
        f"Empate Anula a Aposta (DNB) - {home}",
        f"Cantos de Pressão: Mais de 7.5 Escanteios Totais",
        f"Gol no 1º Tempo (Over 0.5 HT) Garantido",
        f"Total Asiático: Mais de 1.5 Gols na Partida"
    ]
    sugestao_escolhida = random.choice(mercados_possiveis)

    # BILHETE PRÓ ATUALIZADO: Agora incluindo as Finalizações (>80%)!
    bilhete_itens = [
        {"mercado": "Mais de 18.5 Finalizações Totais na Partida", "linha": "Over 18.5 Chutes", "prob": f"{prob_finalizacoes}%", "odd": "1.25"},
        {"mercado": "Mais de 7.5 Escanteios na Partida", "linha": "Over 7.5", "prob": f"{prob_escanteios}%", "odd": "1.22"},
        {"mercado": "Mais de 1.5 Gols no Jogo (Asiático)", "linha": "Over 1.5", "prob": f"{prob_btts}%", "odd": "1.30"},
        {"mercado": "Mais de 2.5 Cartões Amarelos", "linha": "Over 2.5", "prob": f"{prob_cartoes}%", "odd": "1.28"}
    ]
    
    # Recalculando a Odd Total Combinada com as Finalizações inclusas
    odd_combinada = round(1.25 * 1.22 * 1.30 * 1.28, 2)

    return {
        "home_win": f"{p_casa}%",
        "draw": f"{p_empate}%",
        "away_win": f"{p_fora}%",
        "odd_justa": f"@{odd_justa}",
        "btts": f"Sim ({prob_btts}% de chance)",
        "corners": f"Mais de 7.5 ({prob_escanteios}% de chance - Linha Segura)",
        "cards": f"Mais de 2.5 ({prob_cartoes}% de chance - Linha Segura)",
        "shots": f"Mais de 18.5 ({prob_finalizacoes}% de chance - Linha Segura)",
        "recommendation": sugestao_escolhida,
        "bilhete": bilhete_itens,
        "odd_combinada": f"@{odd_combinada}"
    }
