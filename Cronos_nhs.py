import streamlit as st
import pandas as pd
import plotly.express as px
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

tab_cad, tab_dash = st.tabs(["📝 1. Inserir Dados", "🖥️ 2. Dashboard Completo (A3)"])

# --- ABA 1: INSERÇÃO DE DADOS DINÂMICA ---
with tab_cad:
    st.subheader("Configuração da Peça e Linha")
    
    # Layout de configuração inicial
    col_modo, col_prod, col_postos, col_takt = st.columns([1, 2, 1, 1])
    
    produtos_existentes = df_tp['Produto'].unique().tolist()
    modo = col_modo.radio("Ação:", ["Nova Peça", "Editar Existente"])
    
    if modo == "Nova Peça":
        prod = col_prod.text_input("Nome da Nova Peça / Produto", value="Produto X")
    else:
        if produtos_existentes:
            prod = col_prod.selectbox("Selecione a Peça", produtos_existentes)
        else:
            st.warning("Nenhuma peça cadastrada. Crie uma nova.")
            prod = "N/A"
            
    qtd_postos = col_postos.number_input("Quantidade de Postos", min_value=1, max_value=20, value=3)
    takt_input = col_takt.number_input("Takt Time Alvo (s)", min_value=1.0, value=261.0, step=1.0)
    st.session_state['takt'] = takt_input

    st.write("---")
    
    if prod != "N/A":
        st.subheader(f"Cadastro de Atividades: {prod}")
        st.markdown("💡 **Dica:** Você pode adicionar novas linhas clicando na tabela abaixo ou colar dados diretamente do Excel!")
        
        # Gera a lista dinâmica de postos com base na quantidade escolhida
        lista_postos = [f"Posto {i}" for i in range(1, int(qtd_postos) + 1)]
        
        # Filtra os dados existentes ou cria um dataframe vazio para edição
        df_prod = df_tp[df_tp["Produto"] == prod].copy()
        if df_prod.empty:
            df_prod = pd.DataFrame(columns=["Posto", "Atividade", "Tempo (s)", "Classificação"])
        else:
            df_prod = df_prod[["Posto", "Atividade", "Tempo (s)", "Classificação"]]
        
        # Tabela interativa
        edited_df = st.data_editor(
            df_prod,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Posto": st.column_config.SelectboxColumn("Posto", options=lista_postos, required=True),
                "Atividade": st.column_config.TextColumn("Descrição da Atividade", required=True),
                "Tempo (s)": st.column_config.NumberColumn("Tempo (s)", min_value=0.1, format="%.1f", required=True),
                "Classificação": st.column_config.SelectboxColumn("Valor Agregado", options=["Agrega", "Semi Agrega", "Não Agrega"], required=True)
            },
            key="editor_atividades"
        )
        
        if st.button("💾 SALVAR PEÇA / ATIVIDADES"):
            # Adiciona o nome do produto de volta aos dados editados
            edited_df["Produto"] = prod
            
            # Remove os dados antigos desse produto específico
            df_tp_clean = df_tp[df_tp["Produto"] != prod]
            
            # Junta com os novos dados editados
            df_tp_final = pd.concat([df_tp_clean, edited_df], ignore_index=True)
            
            # Salva no CSV
            df_tp_final.to_csv(FILE_TP, index=False)
            st.success(f"Dados do produto '{prod}' salvos com sucesso!")
            st.rerun()

# --- ABA 2: DASHBOARD COMPLETO (A3) ---
with tab_dash:
    if not df_tp.empty:
        # Selecionar qual peça visualizar no Dashboard
        p_sel = st.selectbox("Selecione a peça para visualizar o Dashboard:", df_tp['Produto'].unique())
        st.write("---")
        
        df_f = df_tp[df_tp['Produto'] == p_sel].copy()
        takt = st.session_state.get('takt', 261.0)
        
        # Cálculos de Início e Fim para a Tabela Combinada
        df_f = df_f.sort_values(by=["Posto"])
        df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
        
        tempo_processamento = df_f['Tempo (s)'].sum().round(1)
        tempo_ciclo = df_f.groupby('Posto')['Tempo (s)'].sum().max().round(1)
        
        # 1. CABEÇALHO
        st.markdown(f"<div class='caixa-cabecalho'>CÉLULA {p_sel}</div>", unsafe_allow_html=True)
        col_cab1, col_cab2, col_cab3, col_cab4 = st.columns(4)
        with col_cab1: st.markdown("<div class='caixa-cabecalho'>Elaborado por: Engenharia</div>", unsafe_allow_html=True)
        with col_cab2: st.markdown("<div class='caixa-cabecalho'>Depto: Melhoria Contínua</div>", unsafe_allow_html=True)
        with col_cab3: st.markdown(f"<div class='caixa-cabecalho'>Tempo Processamento: {tempo_processamento}s<br>Tempo de Ciclo: {tempo_ciclo}s</div>", unsafe_allow_html=True)
        with col_cab4: st.markdown("<div class='caixa-cabecalho'>Revisão: 00</div>", unsafe_allow_html=True)
        
        st.write("---")
        
        # DIVISÃO DA TELA: ESQUERDA E DIREITA
        col_esq, col_dir = st.columns([1.2, 1])
        
        # LADO ESQUERDO
        with col_esq:
            # CARTA DE TRABALHO
            st.markdown("<div class='titulo-secao'>CARTA DE TRABALHO</div>", unsafe_allow_html=True)
            
            postos = df_f['Posto'].unique()
            cols_postos = st.columns(len(postos) if len(postos) > 0 else 1)
            
            for i, p_nome in enumerate(postos):
                with cols_postos[i]:
                    st.markdown(f"<div style='text-align:center; font-weight:bold;'>{p_nome}</div>", unsafe_allow_html=True)
                    classe_bola = f"bolinha-{(i % 3) + 1}"
                    qtd_ativ = len(df_f[df_f['Posto'] == p_nome])
                    bolinhas_html = "".join([f"<div class='{classe_bola}'>{j+1}</div>" for j in range(qtd_ativ)])
                    st.markdown(f"<div class='caixa-posto'>{bolinhas_html}<br><br>👤</div>", unsafe_allow_html=True)

            # TABELA COMBINADA
            st.markdown("<div class='titulo-secao'>TABELA COMBINADA</div>", unsafe_allow_html=True)
            
            fig_gantt = px.bar(
                df_f, x="Tempo (s)", y="Atividade", base="Início (s)", color="Posto",
                orientation='h', text="Tempo (s)",
                color_discrete_sequence=["#00bcd4", "#4caf50", "#e040fb", "#ff9800", "#9c27b0", "#f44336"]
            )
            fig_gantt.add_vline(x=takt, line_dash="solid", line_color="red", line_width=3)
            fig_gantt.update_layout(yaxis={'autorange': 'reversed'}, showlegend=False, height=350, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_gantt, use_container_width=True)

        # LADO DIREITO
        with col_dir:
            # GBO
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
        st.info("Nenhuma peça cadastrada. Vá para a aba 1 para começar.")
