import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURAÇÃO ---
FILE_TP = "trabalho_padronizado_dados.csv"

def carregar_tp():
    if not os.path.exists(FILE_TP):
        # Adicionei a coluna "Classificação" para o GBO (Valor Agregado)
        return pd.DataFrame(columns=["Produto", "Posto", "Atividade", "Tempo (s)", "Classificação"])
    return pd.read_csv(FILE_TP)

st.set_page_config(page_title="CronoNHS 2.0 - Trabalho Padronizado", layout="wide")

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    .card-posto { border: 1px solid #1f77b4; padding: 15px; border-radius: 5px; margin-bottom: 10px; background-color: #f0f8ff; color: #000;}
    .metric-box { text-align: center; padding: 10px; background-color: #e6f2ff; border-radius: 8px; border: 1px solid #b3d9ff;}
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()

st.title("📋 CronoNHS 2.0 - Trabalho Padronizado Automático")

# Divisão de abas conforme sua necessidade
tab_cad, tab_combinada, tab_gbo, tab_capacidade, tab_carta = st.tabs([
    "📝 Inserir Dados", 
    "⏱️ Tabela Combinada", 
    "📊 GBO (Yamazumi)", 
    "📈 Quadro de Capacidade",
    "📍 Carta de Trabalho"
])

# --- ABA 1: CADASTRO DE DADOS ---
with tab_cad:
    st.subheader("Cadastro de Atividades")
    with st.form("form_multi"):
        c1, c2, c3 = st.columns([2, 2, 1])
        prod = c1.selectbox("Produto/Família", ["COMPLUS 1200", "UPS - 1", "UPS - 2"])
        posto_sel = c2.selectbox("Posto de Trabalho", ["Posto 1", "Posto 2", "Posto 3", "Posto 4", "Posto 5"])
        takt_input = c3.number_input("Takt Time Alvo (s)", min_value=1.0, value=261.0, step=1.0) # Baseado na sua planilha
        
        st.write("---")
        st.write("Insira a sequência de atividades (O tempo de Início será calculado automaticamente):")
        
        atividades_data = []
        for i in range(1, 6): # Permite até 5 atividades por vez para não poluir a tela
            col_desc, col_tempo, col_valor = st.columns([3, 1, 1.5])
            desc = col_desc.text_input(f"Atividade {i}", key=f"desc_{i}")
            seg = col_tempo.number_input(f"Tempo {i} (s)", min_value=0.0, step=0.5, key=f"seg_{i}")
            val = col_valor.selectbox(f"Classificação {i}", ["Agrega Valor (AV)", "Semi-Agrega (S/AV)", "Não Agrega (N/AV)"], key=f"val_{i}")
            
            if desc and seg > 0:
                atividades_data.append({
                    "Produto": prod, 
                    "Posto": posto_sel, 
                    "Atividade": desc, 
                    "Tempo (s)": seg,
                    "Classificação": val
                })
        
        btn_salvar = st.form_submit_button("💾 SALVAR ATIVIDADES")
        
        if btn_salvar and atividades_data:
            novos_dados = pd.DataFrame(atividades_data)
            df_tp = pd.concat([df_tp, novos_dados], ignore_index=True)
            df_tp.to_csv(FILE_TP, index=False)
            st.success(f"{len(atividades_data)} atividades salvas no {posto_sel}!")
            st.rerun()
            
    # Variável global do Takt para as outras abas
    st.session_state['takt'] = takt_input

# Verificação se existem dados para processar
if not df_tp.empty:
    p_sel = df_tp['Produto'].iloc[-1] # Pega o último produto por padrão
    df_f = df_tp[df_tp['Produto'] == p_sel].copy()
    
    # Lógica de cálculo da Tabela Combinada (Início e Fim)
    df_f = df_f.sort_values(by=["Posto"])
    df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
    df_f['Fim (s)'] = df_f['Início (s)'] + df_f['Tempo (s)']

    # --- ABA 2: TABELA COMBINADA ---
    with tab_combinada:
        st.subheader(f"Tabela Combinada - {p_sel}")
        st.markdown("Visualização sequencial das atividades por posto e seus tempos iniciais e finais.")
        
        df_display = df_f[["Posto", "Atividade", "Início (s)", "Tempo (s)", "Fim (s)", "Classificação"]]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # --- ABA 3: GBO (GRÁFICO DE BALANCEAMENTO DE OPERAÇÕES) ---
    with tab_gbo:
        st.subheader(f"GBO (Gráfico Yamazumi) - {p_sel}")
        
        # Mapeamento de cores clássico para o Lean
        color_map = {
            "Agrega Valor (AV)": "#2ca02c",     # Verde
            "Semi-Agrega (S/AV)": "#ff7f0e",    # Laranja
            "Não Agrega (N/AV)": "#d62728"      # Vermelho
        }
        
        # Gráfico Vertical Empilhado
        fig = px.bar(
            df_f, 
            x="Posto", 
            y="Tempo (s)", 
            color="Classificação",
            color_discrete_map=color_map,
            text="Atividade",
            title=f"Balanceamento de Linha vs TAKT Time",
            hover_data=["Atividade", "Tempo (s)"]
        )
        
        # Adiciona a linha do Takt Time
        takt = st.session_state.get('takt', 261)
        fig.add_hline(y=takt, line_dash="dash", line_color="red", annotation_text=f"TAKT TIME ({takt}s)", annotation_position="top left")
        
        fig.update_layout(barmode='stack', xaxis_title="Postos de Trabalho", yaxis_title="Tempo Total (s)")
        st.plotly_chart(fig, use_container_width=True)

    # --- ABA 4: QUADRO DE CAPACIDADE ---
    with tab_capacidade:
        st.subheader(f"Quadro de Capacidade - {p_sel}")
        
        # Agrupa os tempos totais por posto (TC cronometrado)
        df_cap = df_f.groupby('Posto')['Tempo (s)'].sum().reset_index()
        df_cap.rename(columns={'Tempo (s)': 'TC (cronometrado)'}, inplace=True)
        
        # Aplica a saturação de 10% (exemplo que constava na sua planilha)
        df_cap['TC (saturação)'] = df_cap['TC (cronometrado)'] * 1.10
        df_cap['TAKT'] = takt
        
        # Calcula Capacidade Diária considerando 1 turno de 8h = 28.800 seg (ajuste conforme sua realidade)
        tempo_disponivel_dia_s = 28800 
        df_cap['Capacidade Diária (unid)'] = (tempo_disponivel_dia_s / df_cap['TC (saturação)']).apply(lambda x: int(x) if x > 0 else 0)
        
        df_cap['Operadores'] = 1
        df_cap['Saturação (%)'] = (df_cap['TC (saturação)'] / df_cap['TAKT'] * 100).round(2).astype(str) + "%"
        
        st.dataframe(df_cap, use_container_width=True, hide_index=True)
        
        # Destacar o gargalo
        gargalo = df_cap.loc[df_cap['TC (saturação)'].idxmax()]
        st.warning(f"⚠️ **Operação Gargalo:** {gargalo['Posto']} com Tempo de Ciclo Saturado de {gargalo['TC (saturação)']:.2f}s (Capacidade: {gargalo['Capacidade Diária (unid)']} unid/dia).")

    # --- ABA 5: CARTA DE TRABALHO ---
    with tab_carta:
        st.subheader(f"Carta de Trabalho Padrão - {p_sel}")
        st.markdown("Nesta aba fica o desenho do layout e a sequência de passos visuais do operador.")
        
        postos = df_f['Posto'].unique()
        cols = st.columns(len(postos) if len(postos) > 0 else 1)
        
        for i, p_nome in enumerate(postos):
            with cols[i]:
                st.markdown(f"<div class='card-posto'><b>{p_nome}</b><hr style='margin:5px 0'>", unsafe_allow_html=True)
                atividades_posto = df_f[df_f['Posto'] == p_nome]
                for idx, row in atividades_posto.reset_index().iterrows():
                    st.write(f"{idx+1}. {row['Atividade']} ({row['Tempo (s)']}s)")
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("💡 Dica: Na Carta de Trabalho física, você normalmente anexa a imagem do layout celular (diagrama de espaguete) mostrando o movimento (1, 2, 3...) entre as bancadas. Você pode adicionar um `st.file_uploader` aqui para anexar a foto do layout da linha!")
        
else:
    for tab in [tab_combinada, tab_gbo, tab_capacidade, tab_carta]:
        with tab:
            st.info("Aguardando inserção de dados na aba 'Cadastro'.")
