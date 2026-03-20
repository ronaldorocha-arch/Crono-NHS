import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAÇÃO ---
FILE_TP = "trabal_padronizado.csv"

def carregar_tp():
    if not os.path.exists(FILE_TP):
        return pd.DataFrame(columns=["ID", "Produto", "Posto", "Atividade", "Tempo"])
    return pd.read_csv(FILE_TP)

st.set_page_config(page_title="CronoNHS 2.0 - NHS", layout="wide")

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    .bolinha { height: 20px; width: 20px; background-color: #ff4b4b; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; }
    [data-testid="stMetricValue"] { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()

st.title("📋 CronoNHS 2.0 - Gestão de Processos NHS")

tab_cad, tab_yamazumi, tab_carta = st.tabs(["📝 Cadastro", "📊 Gráfico Yamazumi (Gantt)", "📍 Carta de Trabalho"])

# --- ABA 1: CADASTRO COM MÚLTIPLAS ATIVIDADES ---
with tab_cad:
    st.subheader("Cadastro de Sequência de Trabalho")
    with st.form("form_multi"):
        c1, c2 = st.columns(2)
        prod = c1.selectbox("Produto/UPS", ["UPS - 1", "UPS - 2", "UPS - 3", "UPS - 4", "ACS - 01"])
        posto_sel = c2.selectbox("Selecione o Posto", ["Posto 1", "Posto 2", "Posto 3", "Posto 4", "Posto 5", "Posto 6"])
        
        st.write("---")
        st.write("Digite as atividades abaixo (pode preencher várias):")
        
        atividades_data = []
        for i in range(1, 8): # Permite até 7 atividades por vez
            ca, ct = st.columns([3, 1])
            desc = ca.text_input(f"Atividade {i}", key=f"desc_{i}")
            seg = ct.number_input(f"Tempo {i} (s)", min_value=0.0, step=0.5, key=f"seg_{i}")
            if desc and seg > 0:
                atividades_data.append({"ID": int(pd.Timestamp.now().timestamp() + i), "Produto": prod, "Posto": posto_sel, "Atividade": desc, "Tempo": seg})
        
        btn_salvar = st.form_submit_button("💾 SALVAR TODAS AS ATIVIDADES")
        
        if btn_salvar and atividades_data:
            novos_dados = pd.DataFrame(atividades_data)
            df_tp = pd.concat([df_tp, novos_dados], ignore_index=True)
            df_tp.to_csv(FILE_TP, index=False)
            st.success(f"Foram salvas {len(atividades_data)} atividades no {posto_sel}!")
            st.rerun()

# --- ABA 2: YAMAZUMI DEITADO + TABELA ---
with tab_yamazumi:
    if not df_tp.empty:
        p_sel = st.selectbox("Escolha o Produto:", df_tp['Produto'].unique(), key="sel_p")
        takt = st.number_input("Takt Time Alvo (s):", value=60)
        
        df_f = df_tp[df_tp['Produto'] == p_sel]
        
        # Gráfico Horizontal (Deitado)
        fig = px.bar(df_f, 
                     y="Posto", x="Tempo", color="Atividade",
                     orientation='h',
                     title=f"Balanceamento de Célula - {p_sel}",
                     category_orders={"Posto": ["Posto 6", "Posto 5", "Posto 4", "Posto 3", "Posto 2", "Posto 1"]},
                     text="Atividade")
        
        fig.add_vline(x=takt, line_dash="dash", line_color="red", annotation_text="TAKT TIME")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Tabela de Atividades x Takt")
        df_tabela = df_f.copy()
        df_tabela['Acumulado no Posto'] = df_tabela.groupby('Posto')['Tempo'].cumsum()
        st.dataframe(df_tabela[["Posto", "Atividade", "Tempo", "Acumulado no Posto"]], use_container_width=True)
    else:
        st.info("Aguardando cadastro...")

# --- ABA 3: CARTA DE TRABALHO (BOLINHAS) ---
with tab_carta:
    if not df_tp.empty:
        p_sel_c = st.selectbox("Visualizar Fluxo do Produto:", df_tp['Produto'].unique(), key="sel_c")
        df_c = df_tp[df_tp['Produto'] == p_sel_c]
        
        st.subheader(f"Mapa da Célula: {p_sel_c}")
        colunas_postos = st.columns(6)
        
        postos_lista = ["Posto 1", "Posto 2", "Posto 3", "Posto 4", "Posto 5", "Posto 6"]
        
        for i, p_nome in enumerate(postos_lista):
            with colunas_postos[i]:
                # Conta quantas atividades tem no posto
                qtd = len(df_c[df_c['Posto'] == p_nome])
                st.markdown(f"**{p_nome}**")
                st.write(f"{qtd} atividades")
                
                # Gera as bolinhas visuais
                bolinhas_html = "".join(['<div class="bolinha"></div>' for _ in range(qtd)])
                st.markdown(bolinhas_html, unsafe_allow_html=True)
                
                # Lista as atividades embaixo
                for a in df_c[df_c['Posto'] == p_nome]['Atividade']:
                    st.caption(f"- {a}")
    else:
        st.info("Cadastre os postos para ver a carta de trabalho.")
