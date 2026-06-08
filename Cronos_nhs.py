import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURAÇÃO ---
FILE_TP = "trabalho_padronizado_dados.csv"

def carregar_tp():
    if not os.path.exists(FILE_TP):
        return pd.DataFrame(columns=["Produto", "Posto", "Atividade", "Tempo (s)", "Classificação"])
    return pd.read_csv(FILE_TP)

st.set_page_config(page_title="CronoNHS 2.0 - Trabalho Padronizado", layout="wide")

# --- 2. ESTILO CSS PARA O DASHBOARD ---
st.markdown("""
    <style>
    .caixa-cabecalho { border: 1px solid #000; padding: 10px; text-align: center; font-weight: bold; font-size: 14px; background-color: #f8f9fa;}
    .titulo-secao { text-align: center; font-weight: bold; font-size: 16px; margin-top: 15px; margin-bottom: 10px; color: #333; text-transform: uppercase;}
    .bolinha-1 { height: 25px; width: 25px; background-color: #00bcd4; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 3px; font-size: 12px;}
    .bolinha-2 { height: 25px; width: 25px; background-color: #4caf50; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 3px; font-size: 12px;}
    .bolinha-3 { height: 25px; width: 25px; background-color: #e040fb; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 3px; font-size: 12px;}
    .caixa-posto { border: 2px solid #ccc; padding: 10px; min-height: 120px; text-align: center;}
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()

st.title("📋 CronoNHS 2.0")

# Abas principais
tab_cad, tab_dash = st.tabs(["📝 1. Inserir Dados", "🖥️ 2. Dashboard Completo (A3)"])

# --- ABA 1: INSERÇÃO DE DADOS ---
with tab_cad:
    st.subheader("Cadastro de Atividades")
    with st.form("form_multi"):
        c1, c2, c3 = st.columns([2, 2, 1])
        prod = c1.selectbox("Produto/Família", ["UPS - 02", "COMPLUS 1200"])
        posto_sel = c2.selectbox("Posto de Trabalho", ["Posto 1", "Posto 2", "Posto 3"])
        takt_input = c3.number_input("Takt Time Alvo (s)", min_value=1.0, value=261.0, step=1.0)
        
        st.write("---")
        atividades_data = []
        for i in range(1, 6):
            col_desc, col_tempo, col_valor = st.columns([3, 1, 1.5])
            desc = col_desc.text_input(f"Atividade {i}", key=f"desc_{i}")
            seg = col_tempo.number_input(f"Tempo {i} (s)", min_value=0.0, step=0.5, key=f"seg_{i}")
            val = col_valor.selectbox(f"Classificação {i}", ["Agrega", "Semi Agrega", "Não Agrega"], key=f"val_{i}")
            
            if desc and seg > 0:
                atividades_data.append({"Produto": prod, "Posto": posto_sel, "Atividade": desc, "Tempo (s)": seg, "Classificação": val})
        
        btn_salvar = st.form_submit_button("💾 SALVAR ATIVIDADES")
        if btn_salvar and atividades_data:
            novos_dados = pd.DataFrame(atividades_data)
            df_tp = pd.concat([df_tp, novos_dados], ignore_index=True)
            df_tp.to_csv(FILE_TP, index=False)
            st.success("Salvo com sucesso!")
            st.rerun()
            
    st.session_state['takt'] = takt_input

# --- ABA 2: DASHBOARD COMPLETO (Baseado na imagem 5.jpg) ---
with tab_dash:
    if not df_tp.empty:
        p_sel = df_tp['Produto'].iloc[-1]
        df_f = df_tp[df_tp['Produto'] == p_sel].copy()
        takt = st.session_state.get('takt', 261.0)
        
        # Cálculos de Início e Fim para a Tabela Combinada
        df_f = df_f.sort_values(by=["Posto"])
        df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
        
        tempo_processamento = df_f['Tempo (s)'].sum()
        tempo_ciclo = df_f.groupby('Posto')['Tempo (s)'].sum().max()
        
        # 1. CABEÇALHO (Igual à imagem)
        st.markdown(f"<div class='caixa-cabecalho'>CÉLULA {p_sel}</div>", unsafe_allow_html=True)
        col_cab1, col_cab2, col_cab3, col_cab4 = st.columns(4)
        with col_cab1: st.markdown("<div class='caixa-cabecalho'>Elaborado por: Engenharia</div>", unsafe_allow_html=True)
        with col_cab2: st.markdown("<div class='caixa-cabecalho'>Depto: Melhoria Contínua</div>", unsafe_allow_html=True)
        with col_cab3: st.markdown(f"<div class='caixa-cabecalho'>Tempo Processamento: {tempo_processamento}s<br>Tempo de Ciclo: {tempo_ciclo}s</div>", unsafe_allow_html=True)
        with col_cab4: st.markdown("<div class='caixa-cabecalho'>Revisão: 00</div>", unsafe_allow_html=True)
        
        st.write("---")
        
        # DIVISÃO DA TELA: ESQUERDA E DIREITA
        col_esq, col_dir = st.columns([1.2, 1])
        
        # ==========================================
        # LADO ESQUERDO (Carta de Trabalho + Gantt)
        # ==========================================
        with col_esq:
            # CARTA DE TRABALHO
            st.markdown("<div class='titulo-secao'>CARTA DE TRABALHO</div>", unsafe_allow_html=True)
            
            postos = sorted(df_f['Posto'].unique())
            cols_postos = st.columns(len(postos) if len(postos) > 0 else 1)
            
            for i, p_nome in enumerate(postos):
                with cols_postos[i]:
                    st.markdown(f"<div style='text-align:center; font-weight:bold;'>{p_nome}</div>", unsafe_allow_html=True)
                    # Define a classe da bolinha baseada no índice do posto (para mudar a cor)
                    classe_bola = f"bolinha-{(i % 3) + 1}"
                    
                    qtd_ativ = len(df_f[df_f['Posto'] == p_nome])
                    bolinhas_html = "".join([f"<div class='{classe_bola}'>{j+1}</div>" for j in range(qtd_ativ)])
                    
                    st.markdown(f"<div class='caixa-posto'>{bolinhas_html}<br><br>👤 (Operador)</div>", unsafe_allow_html=True)

            # TABELA COMBINADA (GANTT CASCATA)
            st.markdown("<div class='titulo-secao'>TABELA COMBINADA</div>", unsafe_allow_html=True)
            
            fig_gantt = px.bar(
                df_f, x="Tempo (s)", y="Atividade", base="Início (s)", color="Posto",
                orientation='h', text="Tempo (s)",
                color_discrete_sequence=["#00bcd4", "#4caf50", "#e040fb"] # Cores batendo com as bolinhas
            )
            fig_gantt.add_vline(x=takt, line_dash="solid", line_color="red", line_width=3)
            fig_gantt.update_layout(
                yaxis={'autorange': 'reversed'}, # Inverte o eixo Y para a Atividade 1 ficar no topo
                showlegend=False, 
                height=350,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_gantt, use_container_width=True)

        # ==========================================
        # LADO DIREITO (GBO + Quadro de Capacidade)
        # ==========================================
        with col_dir:
            # GBO (YAMAZUMI)
            st.markdown("<div class='titulo-secao'>GBO</div>", unsafe_allow_html=True)
            
            color_map = {"Agrega": "#00ff00", "Semi Agrega": "#ffff00", "Não Agrega": "#ff9900"}
            
            fig_gbo = px.bar(
                df_f, x="Posto", y="Tempo (s)", color="Classificação",
                color_discrete_map=color_map, text="Tempo (s)", barmode="stack"
            )
            fig_gbo.add_hline(y=takt, line_dash="solid", line_color="red", line_width=3)
            fig_gbo.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_gbo, use_container_width=True)
            
            # QUADRO DE CAPACIDADE
            st.markdown("<div class='titulo-secao'>QUADRO DE CAPACIDADE</div>", unsafe_allow_html=True)
            
            df_cap = df_f.groupby('Posto')['Tempo (s)'].sum().reset_index()
            df_cap.rename(columns={'Tempo (s)': 'TC (cronometrado)'}, inplace=True)
            df_cap['TC (saturação)'] = (df_cap['TC (cronometrado)'] * 1.10).round(0)
            df_cap['TAKT'] = takt
            df_cap['CAP. DIÁRIA'] = (28800 / df_cap['TC (saturação)']).apply(lambda x: round(x, 1))
            df_cap['OPERADORES'] = 1
            df_cap['Capacidade (%)'] = ((df_cap['TC (saturação)'] / df_cap['TAKT']) * 100).round(2).astype(str) + "%"
            
            st.dataframe(df_cap, use_container_width=True, hide_index=True)

    else:
        st.info("Cadastre os dados na aba 1 para gerar o Dashboard.")
