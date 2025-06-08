
import random
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulador de Bac Bo", layout="centered")

st.title("🎲 Simulador de Bac Bo com IA Simples")

# === Configurações do usuário ===
col1, col2 = st.columns(2)
with col1:
    saldo_inicial = st.number_input("Saldo inicial (R$)", 100, 100000, 1000, step=100)
    aposta_base = st.number_input("Aposta base (R$)", 1, 1000, 10, step=1)
    max_martingale = st.slider("Máximo Martingale", 1, 10, 4)
with col2:
    stop_win = st.number_input("Stop Win (R$)", 10, 10000, 300, step=10)
    stop_loss = st.number_input("Stop Loss (R$)", -10000, -10, -300, step=10)
    sequencia_limite = st.slider("Apostar contra sequência de:", 2, 10, 4)

aposta_tie = st.checkbox("Incluir apostas no Tie (Empate)?", value=True)
tie_prob = st.slider("Probabilidade estimada do Tie (%)", 1, 20, 7)
tie_payout = 8  # Fixo no Bac Bo

rodadas = st.slider("Número de rodadas a simular", 10, 10000, 1000, step=100)

if st.button("🎯 Iniciar Simulação"):

    saldo = saldo_inicial
    aposta = aposta_base
    perdas_consecutivas = 0
    lado_atual = None
    sequencia = {"Player": 0, "Banker": 0}
    historico = []

    def jogar_bacbo():
        p1, p2 = random.randint(1,6), random.randint(1,6)
        b1, b2 = random.randint(1,6), random.randint(1,6)
        pt = p1 + p2
        bt = b1 + b2
        if pt > bt:
            return "Player"
        elif bt > pt:
            return "Banker"
        else:
            return "Tie"

    for i in range(rodadas):
        resultado = jogar_bacbo()

        if resultado == lado_atual:
            sequencia[lado_atual] += 1
        else:
            sequencia = {"Player": 0, "Banker": 0}
            lado_atual = resultado
            sequencia[lado_atual] = 1

        # Estratégia IA
        if sequencia["Player"] >= sequencia_limite:
            aposta_lado = "Banker"
        elif sequencia["Banker"] >= sequencia_limite:
            aposta_lado = "Player"
        else:
            aposta_lado = random.choice(["Player", "Banker"])

        aposta_tie_ativa = aposta_tie and random.randint(1, 100) <= tie_prob

        ganho = 0
        if resultado == "Tie" and aposta_tie_ativa:
            ganho += aposta * tie_payout
        elif resultado == aposta_lado:
            ganho += aposta
        else:
            ganho -= aposta

        saldo += ganho

        historico.append({
            "Rodada": i+1,
            "Resultado": resultado,
            "Aposta": aposta_lado,
            "Apostou Tie": aposta_tie_ativa,
            "Ganho/Perda": ganho,
            "Saldo": saldo
        })

        if ganho < 0:
            perdas_consecutivas += 1
            if perdas_consecutivas < max_martingale:
                aposta *= 2
            else:
                aposta = aposta_base
                perdas_consecutivas = 0
        else:
            aposta = aposta_base
            perdas_consecutivas = 0

        if saldo - saldo_inicial >= stop_win:
            st.warning(f"🎉 Stop Win atingido na rodada {i+1}")
            break
        if saldo - saldo_inicial <= stop_loss:
            st.error(f"⛔ Stop Loss atingido na rodada {i+1}")
            break

    # DataFrame
    df = pd.DataFrame(historico)

    st.subheader("📈 Evolução do Saldo")
    fig = px.line(df, x="Rodada", y="Saldo", title="Saldo ao longo do tempo")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Histórico das Apostas")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar CSV", data=csv, file_name="historico_bacbo.csv", mime='text/csv')
