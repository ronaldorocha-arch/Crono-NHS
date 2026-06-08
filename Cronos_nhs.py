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

st.set_page_config(page_title="CronoNHS 2.0", layout="wide")

# --- CSS PARA IMPRESSÃO A3 E VISUAL ---
st.markdown("""
    <style>
    /* CSS PARA TRANSFORMAR A TELA EM UM A3 NA HORA DE IMPRIMIR (Ctrl+P) */
    @media print {
        @page { size: A3 landscape; margin: 10mm; }
        header, footer, .stApp > header { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { display: none !important; }
        #MainMenu {visibility: hidden;}
        /* Ajustes extras para forçar a impressão das cores de fundo */
        * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
    }
    
    .caixa-cabecalho { border: 1px solid #000; padding: 10px; text-align: center; font-weight: bold; font-size: 14px; background-color: #f8f9fa;}
    .titulo-secao { text-align: center; font-weight: bold; font-size: 16px; margin-top: 15px; margin-bottom: 10px; color: #333; text-transform: uppercase; border-bottom: 2px solid #ccc;}
    
    /* Legenda e EPIs */
    .caixa-legenda { border: 1px solid #000; padding: 10px; margin-bottom: 15px; font-size: 12px;}
    .icon-legenda { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px;}
    .epi-text { font-size: 28px; text-align: center; margin: 5px; }
    
    .bolinha-1 { height: 25px; width: 25px; background-color: #00bcd4; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 3px;}
    .bolinha-2 { height: 25px; width: 25px; background-color: #4caf50; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 3px;}
    .bolinha-3 { height: 25px; width: 25px; background-color: #e040fb; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 3px;}
    .caixa-posto { border: 1px solid #000; padding: 10px; min-height: 120px; text-align: center; background-color: #fff;}
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()
st.title("📋 CronoNHS 2.0")

tab_cad, tab_dash = st.tabs(["📝 1. Inserir Dados", "🖥️ 2. Dashboard A3 (Ctrl+P para PDF)"])

# --- ABA 1: INSERÇÃO DE DADOS ---
with tab_cad:
    st.subheader("Informações do Documento")
    col_elab, col_depto = st.columns(2)
    elaborador_input = col_elab.text_input("Elaborado por:", value=st.session_state.get('elaborador', "Engenharia"))
    depto_input = col_depto.text_input("Departamento/Setor:", value=st.session_state.get('departamento', "Melhoria de Processos"))
    
    st.write("---")
    st.subheader("Configuração da Célula")
    
    col_prod, col_postos, col_takt = st.columns([2, 1, 1])
    prod = col_prod.text_input("Nome da Peça / Produto", value="UPS - 02")
    qtd_postos = col_postos.number_input("Qtd de Postos", min_value=1, value=3)
    takt_input = col_takt.number_input("Takt Time Alvo (s)", min_value=1.0, value=261.0)
    
    st.write("---")
    st.markdown("**EPIs Necessários para a Célula:**")
    lista_epis = ["🥽 Óculos", "🥼 Jaleco", "👞 Sapato Seg.", "🧤 Luvas", "🎧 Protetor Auricular", "🧢 Touca"]
    epis_selecionados = st.multiselect("Selecione os EPIs", lista_epis, default=["🥽 Óculos", "🥼 Jaleco", "👞 Sapato Seg.", "🧤 Luvas"])
    
    # Salvando configurações gerais na sessão
    st.session_state['elaborador'] = elaborador_input
    st.session_state['departamento'] = depto_input
    st.session_state['takt'] = takt_input
    st.session_state['epis'] = epis_selecionados

    st.write("---")
    st.markdown("Insira os tempos (Você pode adicionar linhas abaixo ou colar dados do Excel):")
    
    lista_postos = [f"Posto {i}" for i in range(1, int(qtd_postos) + 1)]
    df_prod = df_tp[df_tp["Produto"] == prod].copy()
    if df_prod.empty:
        df_prod = pd.DataFrame(columns=["Posto", "Atividade", "Tempo (s)", "Classificação"])
    
    edited_df = st.data_editor(
        df_prod, num_rows="dynamic", use_container_width=True,
        column_config={
            "Posto": st.column_config.SelectboxColumn("Posto", options=lista_postos),
            "Atividade": st.column_config.TextColumn("Descrição da Atividade"),
            "Tempo (s)": st.column_config.NumberColumn("Tempo (s)", format="%.1f"),
            "Classificação": st.column_config.SelectboxColumn("Valor", options=["Agrega", "Semi Agrega", "Não Agrega"])
        }
    )
    
    if st.button("💾 SALVAR PRODUTO"):
        edited_df["Produto"] = prod
        df_tp_clean = df_tp[df_tp["Produto"] != prod]
        df_final = pd.concat([df_tp_clean, edited_df], ignore_index=True)
        df_final.to_csv(FILE_TP, index=False)
        st.success("Produto salvo com sucesso!")
        st.rerun()

# --- ABA 2: DASHBOARD COMPLETO ---
with tab_dash:
    if not df_tp.empty:
        p_sel = st.selectbox("Visualizar Produto:", df_tp['Produto'].unique())
        df_f = df_tp[df_tp['Produto'] == p_sel].copy()
        
        # Recuperando as variáveis salvas na sessão
        takt = st.session_state.get('takt', 261.0)
        epis = st.session_state.get('epis', [])
        elaborador = st.session_state.get('elaborador', 'Engenharia')
        departamento = st.session_state.get('departamento', 'Melhoria de Processos')
        
        df_f = df_f.sort_values(by=["Posto"])
        
        if not df_f.empty:
            df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
            tc_total = df_f['Tempo (s)'].sum().round(1)
            tc_max = df_f.groupby('Posto')['Tempo (s)'].sum().max().round(1)
        else:
            tc_total, tc_max = 0, 0
        
        # 1. CABEÇALHO (Agora com as variáveis dinâmicas)
        st.markdown(f"<div class='caixa-cabecalho' style='font-size:18px;'>CÉLULA {p_sel}</div>", unsafe_allow_html=True)
        col_cab1, col_cab2, col_cab3 = st.columns(3)
        with col_cab1: st.markdown(f"<div class='caixa-cabecalho'>Elaborado por: {elaborador}</div>", unsafe_allow_html=True)
        with col_cab2: st.markdown(f"<div class='caixa-cabecalho'>Depto: {departamento}</div>", unsafe_allow_html=True)
        with col_cab3: st.markdown(f"<div class='caixa-cabecalho'>Tempo Processamento: {tc_total}s | Tempo de Ciclo: {tc_max}s</div>", unsafe_allow_html=True)
        
        st.write("")
        
        # DIVISÃO DA TELA: ESQUERDA (Legenda) | MEIO (Carta/Gantt) | DIREITA (GBO/Quadro)
        col_esq, col_meio, col_dir = st.columns([0.5, 1.5, 1.2])
        
        # --- COLUNA ESQUERDA: LEGENDA E EPIs ---
        with col_esq:
            st.markdown("<div class='caixa-legenda'><b>LEGENDA</b><br><br><span class='icon-legenda' style='background:red;'></span> ANDON<br><br><span class='icon-legenda' style='background:#555;'></span> ESTOQUE<br><br><span class='icon-legenda' style='border:1px solid #000;'></span> PONTO DE USO</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='caixa-legenda' style='text-align:center;'><b>EPI'S NECESSÁRIOS</b><br><br>", unsafe_allow_html=True)
            for epi in epis:
                st.markdown(f"<div class='epi-text'>{epi.split(' ')[0]}</div>", unsafe_allow_html=True) # Pega só o emoji
            st.markdown("</div>", unsafe_allow_html=True)

        # --- COLUNA MEIO: CARTA DE TRABALHO E GANTT ---
        with col_meio:
            st.markdown("<div class='titulo-secao'>CARTA DE TRABALHO</div>", unsafe_allow_html=True)
            postos = df_f['Posto'].unique()
            cols_postos = st.columns(len(postos) if len(postos) > 0 else 1)
            
            for i, p_nome in enumerate(postos):
                with cols_postos[i]:
                    classe_bola = f"bolinha-{(i % 3) + 1}"
                    qtd_ativ = len(df_f[df_f['Posto'] == p_nome])
                    bolinhas_html = "".join([f"<div class='{classe_bola}'>{j+1}</div>" for j in range(qtd_ativ)])
                    st.markdown(f"<div class='caixa-posto'><b>{p_nome}</b><hr>{bolinhas_html}<br><br>👤</div>", unsafe_allow_html=True)

            st.markdown("<div class='titulo-secao'>TABELA COMBINADA (YAMAZUMI)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                cores_postos = ["#00bcd4", "#4caf50", "#e040fb", "#ff9800", "#9c27b0", "#f44336", "#3f51b5", "#009688"]
                fig_gantt = px.bar(df_f, x="Tempo (s)", y="Atividade", base="Início (s)", color="Posto", orientation='h', color_discrete_sequence=cores_postos)
                fig_gantt.add_vline(x=takt, line_dash="solid", line_color="red")
                fig_gantt.update_layout(yaxis={'autorange': 'reversed', 'visible': False}, showlegend=False, height=250, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_chart")

        # --- COLUNA DIREITA: GBO E CAPACIDADE ---
        with col_dir:
            st.markdown("<div class='titulo-secao'>GBO & VALOR AGREGADO</div>", unsafe_allow_html=True)
            color_map = {"Agrega": "#00ff00", "Semi Agrega": "#ffff00", "Não Agrega": "#ff9900"}
            
            if not df_f.empty:
                fig_gbo = px.bar(df_f, x="Posto", y="Tempo (s)", color="Classificação", color_discrete_map=color_map, text="Tempo (s)", barmode="stack")
                fig_gbo.add_hline(y=takt, line_dash="solid", line_color="red")
                fig_gbo.update_layout(height=220, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                st.plotly_chart(fig_gbo, use_container_width=True, key="gbo_chart")
            
            # --- GRÁFICOS DE PIZZA (Porcentagem por Posto) ---
            if len(postos) > 0:
                cols_pie = st.columns(len(postos))
                for i, p_nome in enumerate(postos):
                    df_pie = df_f[df_f['Posto'] == p_nome].groupby('Classificação')['Tempo (s)'].sum().reset_index()
                    if not df_pie.empty:
                        fig_pie = px.pie(df_pie, values='Tempo (s)', names='Classificação', color='Classificação', color_discrete_map=color_map, hole=0.4)
                        fig_pie.update_traces(textposition='inside', textinfo='percent')
                        fig_pie.update_layout(height=120, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                        with cols_pie[i]:
                            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{i}_{p_nome}")
                            st.markdown(f"<div style='text-align:center; font-size:10px;'>{p_nome}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='titulo-secao'>QUADRO DE CAPACIDADE</div>", unsafe_allow_html=True)
            if not df_f.empty:
                df_cap = df_f.groupby('Posto')['Tempo (s)'].sum().reset_index()
                df_cap['TC(sat)'] = (df_cap['Tempo (s)'] * 1.10).round(0)
                df_cap['CAP. DIÁRIA'] = (28800 / df_cap['TC(sat)']).apply(lambda x: int(x) if x > 0 else 0)
                df_cap['Capacidade (%)'] = ((df_cap['TC(sat)'] / takt) * 100).round(1).astype(str) + "%"
                st.dataframe(df_cap[["Posto", "Tempo (s)", "TC(sat)", "CAP. DIÁRIA", "Capacidade (%)"]], use_container_width=True, hide_index=True)

    else:
        st.info("Nenhuma peça cadastrada. Vá para a aba '1. Inserir Dados' para começar.")
