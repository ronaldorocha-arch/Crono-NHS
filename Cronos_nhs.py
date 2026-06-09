import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAÇÃO DE FICHEIROS/DADOS ---
FILE_TP = "trabalho_padronizado_dados.csv"
FILE_POSTOS = "config_postos.csv"

def carregar_tp():
    if not os.path.exists(FILE_TP):
        return pd.DataFrame(columns=["Produto", "Posto", "Atividade", "Tempo (s)", "Classificação"])
    return pd.read_csv(FILE_TP)

def carregar_cfg_postos():
    if not os.path.exists(FILE_POSTOS):
        return pd.DataFrame(columns=["Produto", "Posto", "Ponto de Uso", "Andon", "WIP", "Posição Operador"])
    
    df = pd.read_csv(FILE_POSTOS)
    if "Flow Rack" in df.columns:
        df.rename(columns={"Flow Rack": "Ponto de Uso"}, inplace=True)
    if "WIP (Estoque)" in df.columns:
        df.rename(columns={"WIP (Estoque)": "WIP"}, inplace=True)
    if "Posição Operador" not in df.columns:
        df["Posição Operador"] = "Frente"
    return df

st.set_page_config(page_title="CronoNHS 2.0 - A3", layout="wide")

# --- CSS ESTRUTURAL E IMPRESSÃO ---
st.markdown("""
    <style>
    /* ---------------------------------------------------
       IMPRESSÃO A3 - CORREÇÃO DE COLUNAS E ESCALA
    --------------------------------------------------- */
    @media print {
        @page { 
            size: A3 landscape; 
            margin: 5mm !important; 
        }
        
        header, footer, .stApp > header, .stTabs [data-baseweb="tab-list"], #MainMenu, [data-testid="stSidebar"], h1, .no-print, [data-testid="stMultiSelect"], [data-testid="stSelectbox"] { 
            display: none !important; 
        }
        
        * { 
            -webkit-print-color-adjust: exact !important; 
            color-adjust: exact !important; 
        }
        
        html, body, .stApp, .block-container { 
            width: 100% !important; 
            max-width: 100% !important; 
            background-color: white !important; 
            margin: 0 !important; 
            padding: 0 !important;
            overflow: visible !important;
        }
        
        .block-container {
            zoom: 0.75 !important;
        }
        
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 15px !important;
        }
        
        [data-testid="column"] { 
            flex: 1 1 0% !important;
            min-width: 0 !important; 
            display: block !important;
            page-break-inside: avoid !important;
        }
        
        .stDataFrame, [data-testid="stDataFrame"], [data-testid="stGridVirtualizer"] {
            width: 100% !important;
            overflow: visible !important;
        }
        div[data-testid="stDataFrame"] > div {
            overflow: visible !important;
            max-height: none !important;
        }
    }
    
    /* ---------------------------------------------------
       ESTILOS VISUAIS DO DASHBOARD E POSTOS
    --------------------------------------------------- */
    body { font-family: 'Arial', sans-serif; }
    .caixa-cabecalho { border: 1px solid #000; padding: 6px; text-align: center; font-weight: bold; font-size: 13px; background-color: #f4f4f4;}
    .titulo-secao { text-align: center; font-weight: bold; font-size: 14px; margin: 5px 0 8px 0; color: #000; text-transform: uppercase; border-bottom: 2px solid #000;}
    
    .caixa-padrao { border: 1px solid #000; padding: 6px; margin-bottom: 5px; font-size: 11px; background: #fff;}
    .icon-legenda { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px; vertical-align: middle;}
    .epi-text { font-size: 18px; text-align: center; margin: 0 4px; display: inline-block; }
    
    /* 🚨 FORÇA O GAP ZERO E CENTRALIZA A BANCADA 🚨 */
    .layout-linha { display: flex; justify-content: center; align-items: center; flex-wrap: nowrap; gap: 0px !important; padding: 45px 10px; }
    .layout-u { display: flex; flex-wrap: wrap; justify-content: center; gap: 0px !important; max-width: 800px; margin: 0 auto; padding: 45px 10px;}
    
    /* 🚨 CAIXA DO POSTO: IMPEDE O STREAMLIT DE SEPARÁ-LOS (flex: none) 🚨 */
    .caixa-posto { 
        width: 200px !important; 
        height: 100px !important; 
        border: 2px solid #333; 
        background-color: #fff; 
        position: relative; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0px !important; 
        margin-right: -2px !important; /* Sobrepõe as bordas para fundir as mesas */
        margin-bottom: -2px !important;
        flex: none !important; /* Bloqueia o alongamento automático do Streamlit */
        box-sizing: border-box !important;
    }
    
    /* PONTO DE USO TRAVADO NO TOPO */
    .ponto-uso { position: absolute; top: 0; left: -2px; right: -2px; height: 18px; background: #bbb; border-bottom: 1px solid #333; font-size: 10px; line-height: 18px; color: #000; font-weight: bold; z-index: 5; text-align: center;}
    
    /* INDICADORES */
    .andon { position: absolute; top: -12px; left: -12px; width: 22px; height: 22px; background-color: red; border-radius: 50%; border: 2px solid yellow; box-shadow: 0 0 5px red; z-index: 10;}
    /* WIP movido para a direita (right: -12px) */
    .wip-badge { position: absolute; bottom: -12px; right: -12px; width: 24px; height: 24px; background-color: #000; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; z-index: 10; border: 2px solid #fff;}
    
    .bolinha { display: inline-flex; height: 22px; width: 22px; border-radius: 50%; align-items: center; justify-content: center; color: #000; font-weight: bold; margin: 2px; font-size: 11px; z-index: 5;}
    .b-1 { background-color: #00bcd4; } .b-2 { background-color: #4caf50; } .b-3 { background-color: #e040fb; } .b-4 { background-color: #ff9800; } .b-5 { background-color: #9c27b0; }
    
    /* POSIÇÕES DO OPERADOR */
    .operador-icon { position: absolute; font-size: 26px; z-index: 10; }
    .op-frente { bottom: -38px; left: calc(50% - 13px); }
    .op-tras { top: -38px; left: calc(50% - 13px); }
    .op-esq { top: calc(50% - 13px); left: -38px; }
    .op-dir { top: calc(50% - 13px); right: -38px; }
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()
df_cfg = carregar_cfg_postos()

st.title("📋 CronoNHS 2.0 - Engenharia de Processos")

tab_cad, tab_dash = st.tabs(["📝 1. Inserir Dados e Layout", "🖥️ 2. Dashboard A3 (Ctrl+P para PDF)"])

# =====================================================================
# --- ABA 1: INSERÇÃO E CONFIGURAÇÃO DE DADOS ---
# =====================================================================
with tab_cad:
    col_info1, col_info2 = st.columns(2)
    elaborador = col_info1.text_input("Elaborado por:", value=st.session_state.get('elaborador', "Engenharia"))
    depto = col_info2.text_input("Departamento:", value=st.session_state.get('depto', "Melhoria Contínua"))
    
    st.write("---")
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1.5])
    prod = c1.text_input("Produto / Família", value="UPS - 02")
    qtd_postos = c2.number_input("Nº de Postos", min_value=1, value=3)
    takt_input = c3.number_input("Takt Time (s)", min_value=1.0, value=261.0)
    demanda_input = c4.number_input("Demanda Diária", min_value=1, value=116)
    layout_tipo = c5.selectbox("Formato do Layout", ["Em Linha", "Célula em U"])
    
    epis_selecionados = st.multiselect("EPIs Necessários", ["🥽 Óculos", "🥼 Jaleco", "👞 Sapato", "🧤 Luvas", "🎧 Protetor", "🧢 Touca"], default=["🥽 Óculos", "🥼 Jaleco", "👞 Sapato", "🧤 Luvas"])
    
    st.session_state.update({'elaborador': elaborador, 'depto': depto, 'takt': takt_input, 'demanda': demanda_input, 'epis': epis_selecionados, 'layout': layout_tipo})

    st.write("---")
    sub_tab_ativ, sub_tab_postos = st.tabs(["⏱️ Tempos e Atividades", "🏭 Configuração Física (Ponto Uso, Andon, WIP, Operador)"])
    
    lista_postos = [f"Posto {i}" for i in range(1, int(qtd_postos) + 1)]
    
    with sub_tab_ativ:
        st.markdown("**Passo a Passo das Atividades:**")
        df_prod = df_tp[df_tp["Produto"] == prod].copy()
        if df_prod.empty: df_prod = pd.DataFrame(columns=["Posto", "Atividade", "Tempo (s)", "Classificação"])
        
        edited_df = st.data_editor(
            df_prod, num_rows="dynamic", use_container_width=True,
            column_config={
                "Posto": st.column_config.SelectboxColumn("Posto", options=lista_postos),
                "Atividade": st.column_config.TextColumn("Descrição"),
                "Tempo (s)": st.column_config.NumberColumn("Tempo (s)", format="%.1f"),
                "Classificação": st.column_config.SelectboxColumn("Agregação de Valor", options=["Agrega", "Semi Agrega", "Não Agrega"])
            }
        )
        
    with sub_tab_postos:
        st.markdown
