import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAÇÃO E DADOS ---
# O arquivo CSV será criado automaticamente na primeira vez que você salvar uma atividade
FILE_TP = "trabalho_padronizado.csv"

def carregar_tp():
    if not os.path.exists(FILE_TP):
        return pd.DataFrame(columns=["ID", "Produto", "Posto", "Atividade", "Tempo"])
    try:
        df = pd.read_csv(FILE_TP)
        return df
    except:
        return pd.DataFrame(columns=["ID", "Produto", "Posto", "Atividade", "Tempo"])

st.set_page_config(page_title="CronoNHS - Trabalho Padronizado", layout="wide", page_icon="📋")

# --- 2. ESTILO CSS PARA LIMPEZA VISUAL ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 400 !important; }
    .stButton > button { width: 100%; height: 50px; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()

# --- 3. TÍTULO E NAVEGAÇÃO ---
st.title("📋 CronoNHS - Gestão de Trabalho Padronizado")
tab_cad, tab_graph, tab_dados = st.tabs(["📝 Cadastro", "📊 Gráfico de Balanceamento (Yamazumi)", "📂 Gerenciar Base"])

# --- ABA 1: CADASTRO DE ATIVIDADES ---
with tab_cad:
    st.subheader("Inserir Nova Atividade")
    with st.form("form_cadastro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        produto = c1.selectbox("Produto / Modelo", ["UPS - 1", "UPS - 2", "UPS - 3", "UPS - 4", "ACS - 01", "Outro"])
        posto = c2.selectbox("Posto de Trabalho", ["Posto 1", "Posto 2", "Posto 3", "Posto 4", "Posto 5", "Posto 6"])
        
        c3, c4 = st.columns([3, 1])
        ativ = c3.text_input("Descrição da Atividade (Ex: Fixar Placa)")
        tempo = c4.number_input("Tempo (segundos)", min_value=0.1, step=0.5)
        
        btn_add = st.form_submit_button("💾 Salvar Atividade")
        
        if btn_add and ativ:
            # Gera um ID único baseado na data/hora
            novo_id = int(pd.Timestamp.now().timestamp() * 100)
            nova_linha = pd.DataFrame([{"ID": novo_id, "Produto": produto, "Posto": posto, "Atividade": ativ, "Tempo": tempo}])
            df_tp = pd.concat([df_tp, nova_linha], ignore_index=True)
            df_tp.to_csv(FILE_TP, index=False)
            st.success(f"Adicionado: {ativ} no {posto}")
            st.rerun()

# --- ABA 2: GRÁFICO YAMAZUMI E CÁLCULOS ---
with tab_graph:
    if not df_tp.empty:
        col_filtro1, col_filtro2 = st.columns([2, 2])
        prod_sel = col_filtro1.selectbox("Filtrar Produto para Análise:", df_tp['Produto'].unique())
        takt_meta = col_filtro2.number_input("Meta de Takt Time (segundos):", min_value=1, value=60)
        
        df_filtrado = df_tp[df_tp['Produto'] == prod_sel]
        
        if not df_filtrado.empty:
            # Cálculos de Indicadores de Produção
            tempos_por_posto = df_filtrado.groupby("Posto")["Tempo"].sum().reset_index()
            tempo_total = tempos_por_posto["Tempo"].sum()
            gargalo_valor = tempos_por_posto["Tempo"].max()
            posto_gargalo = tempos_por_posto.loc[tempos_por_posto["Tempo"].idxmax(), "Posto"]
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tempo Total Processo", f"{tempo_total:.1f}s")
            m2.metric("Posto Gargalo", posto_gargalo)
            m3.metric("Tempo do Gargalo", f"{gargalo_valor:.1f}s")
            cap_hora = int(3600 / gargalo_valor) if gargalo_valor > 0 else 0
            m4.metric("Capacidade Estimada", f"{cap_hora} pçs/h")

            st.divider()

            # Ordem dos postos no gráfico
            ordem_postos = ["Posto 1", "Posto 2", "Posto 3", "Posto 4", "Posto 5", "Posto 6"]
            
            fig = px.bar(df_filtrado, 
                         x="Posto", 
                         y="Tempo", 
                         color="Atividade", 
                         title=f"Gráfico de Balanceamento (Yamazumi) - {prod_sel}",
                         text="Atividade",
                         category_orders={"Posto": ordem_postos},
                         color_discrete_sequence=px.colors.qualitative.Bold)
            
            # Linha Vermelha de Takt Time
            fig.add_hline(y=takt_meta, line_dash="dash", line_color="red", 
                          annotation_text=f"LIMITE TAKT ({takt_meta}s)", annotation_position="top right")
            
            fig.update_layout(showlegend=True, height=600, barmode='stack')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecione um produto para visualizar o gráfico.")
    else:
        st.info("Cadastre dados na aba 'Cadastro' para gerar a análise.")

# --- ABA 3: GERENCIAR DADOS ---
with tab_dados:
    st.subheader("Histórico e Exclusão")
    if not df_tp.empty:
        st.write("Lista de atividades cadastradas:")
        for i, row in df_tp.iterrows():
            col_dados, col_btn = st.columns([9, 1])
            col_dados.write(f"**ID:** {row['ID']} | **{row['Produto']}** | {row['Posto']} | {row['Atividade']} | {row['Tempo']}s")
            if col_btn.button("🗑️", key=f"del_{row['ID']}"):
                df_tp = df_tp[df_tp['ID'] != row['ID']]
                df_tp.to_csv(FILE_TP, index=False)
                st.success("Removido com sucesso!")
                st.rerun()
        
        st.divider()
        if st.button("⚠️ APAGAR TODA A BASE"):
            if os.path.exists(FILE_TP):
                os.remove(FILE_TP)
                st.rerun()
    else:
        st.warning("Banco de dados vazio.")
