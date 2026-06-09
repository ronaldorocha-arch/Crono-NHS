import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAÇÃO ---
FILE_TP = "trabalho_padronizado_dados.csv"
FILE_POSTOS = "config_postos.csv"

def carregar_tp():
    if not os.path.exists(FILE_TP):
        return pd.DataFrame(columns=["Produto", "Posto", "Atividade", "Tempo (s)", "Classificação"])
    return pd.read_csv(FILE_TP)

def carregar_cfg_postos():
    if not os.path.exists(FILE_POSTOS):
        return pd.DataFrame(columns=["Produto", "Posto", "Flow Rack", "Andon", "WIP (Estoque)"])
    return pd.read_csv(FILE_POSTOS)

st.set_page_config(page_title="CronoNHS 2.0 - A4", layout="wide")

# --- CSS PROFISSIONAL & CORREÇÃO DE IMPRESSÃO A4 ---
st.markdown("""
    <style>
    /* ---------------------------------------------------
       BORDA GLOBAL PARA O CONTEÚDO (TELA E IMPRESSÃO)
    --------------------------------------------------- */
    .folha-impressao {
        border: 3px solid #000;
        padding: 15px;
        background-color: #fff;
        border-radius: 4px;
        box-sizing: border-box;
    }

    /* ---------------------------------------------------
       HACK PARA IMPRESSÃO A4 PAISAGEM PERFEITA
    --------------------------------------------------- */
    @media print {
        @page { 
            size: A4 landscape; 
            margin: 5mm; /* Margem mínima da página física */
        }
        
        /* Esconde menus, rodapés e abas do Streamlit */
        header, footer, .stApp > header, .stTabs [data-baseweb="tab-list"], #MainMenu, [data-testid="stSidebar"] { 
            display: none !important; 
        }
        
        /* Força as cores a aparecerem no papel */
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
        }
        
        /* Aplica o zoom para caber na folha sem espremer os gráficos */
        body { zoom: 0.75; }
        
        /* Configura a borda para ocupar todo o espaço visível na impressão */
        .folha-impressao {
            border: 3px solid #000 !important;
            padding: 10mm !important;
            min-height: 95vh !important;
            page-break-inside: avoid;
        }

        /* Impede que as colunas quebrem de forma errada */
        [data-testid="column"] { min-width: 0 !important; }
    }
    
    /* ---------------------------------------------------
       ESTILOS VISUAIS DO DASHBOARD
    --------------------------------------------------- */
    body { font-family: 'Arial', sans-serif; }
    .caixa-cabecalho { border: 1px solid #000; padding: 6px; text-align: center; font-weight: bold; font-size: 13px; background-color: #f4f4f4;}
    .titulo-secao { text-align: center; font-weight: bold; font-size: 14px; margin: 15px 0 10px 0; color: #000; text-transform: uppercase; border-bottom: 2px solid #000;}
    
    /* Legendas e Caixas */
    .caixa-padrao { border: 1px solid #000; padding: 8px; margin-bottom: 10px; font-size: 11px; background: #fff;}
    .icon-legenda { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px; vertical-align: middle;}
    .epi-text { font-size: 20px; text-align: center; margin: 0 5px; display: inline-block; }
    
    /* Carta de Trabalho UI */
    .layout-linha { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: nowrap; gap: 10px; }
    .layout-u { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; max-width: 800px; margin: 0 auto;}
    
    .caixa-posto { border: 2px solid #333; padding: 10px; text-align: center; background-color: #fff; position: relative; min-width: 120px; flex: 1;}
    .flow-rack { width: 100%; height: 15px; background: #bbb; border: 1px solid #555; margin-bottom: 10px; font-size: 9px; line-height: 15px; color: #000;}
    .andon { position: absolute; top: -10px; left: -10px; width: 20px; height: 20px; background-color: red; border-radius: 50%; border: 2px solid yellow; box-shadow: 0 0 5px red;}
    .wip-badge { position: absolute; top: 40%; right: -15px; width: 25px; height: 25px; background-color: #666; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; z-index: 10; border: 2px solid #fff;}
    
    .bolinha { display: inline-flex; height: 22px; width: 22px; border-radius: 50%; align-items: center; justify-content: center; color: #000; font-weight: bold; margin: 2px; font-size: 11px;}
    .b-1 { background-color: #00bcd4; }
    .b-2 { background-color: #4caf50; }
    .b-3 { background-color: #e040fb; }
    .b-4 { background-color: #ff9800; }
    .b-5 { background-color: #9c27b0; }
    
    .operador { font-size: 24px; margin-top: 10px; color: #555;}
    </style>
    """, unsafe_allow_html=True)

df_tp = carregar_tp()
df_cfg = carregar_cfg_postos()

st.title("📋 CronoNHS 2.0 - Engenharia de Processos")

tab_cad, tab_dash = st.tabs(["📝 1. Inserir Dados e Layout", "🖥️ 2. Dashboard A4 (Ctrl+P para PDF)"])

# --- ABA 1: INSERÇÃO DE DADOS ---
with tab_cad:
    col_info1, col_info2 = st.columns(2)
    elaborador = col_info1.text_input("Elaborado por:", value=st.session_state.get('elaborador', "Engenharia"))
    depto = col_info2.text_input("Departamento:", value=st.session_state.get('depto', "Melhoria Contínua"))
    
    st.write("---")
    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1, 1, 1, 1, 1.5])
    prod = c1.text_input("Produto / Família", value="UPS - 02")
    qtd_postos = c2.number_input("Nº Postos", min_value=1, value=3)
    takt_input = c3.number_input("Takt Time (s)", min_value=1.0, value=261.0)
    demanda_input = c4.number_input("Demanda", min_value=1, value=116)
    tempo_disp_input = c5.number_input("Tempo Disp. (s)", min_value=1, value=30312) # <-- NOVO CAMPO PARA O CALCULO BATER
    layout_tipo = c6.selectbox("Layout", ["Em Linha (Reta)", "Célula em U"])
    
    epis_selecionados = st.multiselect("EPIs Necessários", ["🥽 Óculos", "🥼 Jaleco", "👞 Sapato", "🧤 Luvas", "🎧 Protetor", "🧢 Touca"], default=["🥽 Óculos", "🥼 Jaleco", "👞 Sapato", "🧤 Luvas"])
    
    st.session_state.update({'elaborador': elaborador, 'depto': depto, 'takt': takt_input, 'demanda': demanda_input, 'tempo_disp': tempo_disp_input, 'epis': epis_selecionados, 'layout': layout_tipo})

    st.write("---")
    sub_tab_ativ, sub_tab_postos = st.tabs(["⏱️ Tempos e Atividades", "🏭 Configuração Física (Flow Rack, Andon, WIP)"])
    
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
        st.markdown("**Mapeamento do Layout da Linha:**")
        df_cfg_prod = df_cfg[df_cfg["Produto"] == prod].copy()
        if df_cfg_prod.empty:
            df_cfg_prod = pd.DataFrame({"Posto": lista_postos, "Flow Rack": ["Não"]*len(lista_postos), "Andon": ["Não"]*len(lista_postos), "WIP (Estoque)": [0]*len(lista_postos)})
        
        edited_cfg = st.data_editor(
            df_cfg_prod, hide_index=True, use_container_width=True,
            column_config={
                "Posto": st.column_config.TextColumn("Posto", disabled=True),
                "Flow Rack": st.column_config.SelectboxColumn("Possui Flow Rack?", options=["Sim", "Não"]),
                "Andon": st.column_config.SelectboxColumn("Possui Andon?", options=["Sim", "Não"]),
                "WIP (Estoque)": st.column_config.NumberColumn("Estoque APÓS este posto", min_value=0, step=1)
            }
        )
        
    if st.button("💾 SALVAR PRODUTO E CONFIGURAÇÕES", type="primary", use_container_width=True):
        edited_df["Produto"] = prod
        pd.concat([df_tp[df_tp["Produto"] != prod], edited_df], ignore_index=True).to_csv(FILE_TP, index=False)
        
        edited_cfg["Produto"] = prod
        pd.concat([df_cfg[df_cfg["Produto"] != prod], edited_cfg], ignore_index=True).to_csv(FILE_POSTOS, index=False)
        st.success("Tudo salvo com sucesso!")
        st.rerun()

# --- ABA 2: DASHBOARD COMPLETO ---
with tab_dash:
    if not df_tp.empty:
        p_sel = st.selectbox("Visualizar Célula:", df_tp['Produto'].unique())
        df_f = df_tp[df_tp['Produto'] == p_sel].sort_values(by=["Posto"]).copy()
        df_c = df_cfg[df_cfg['Produto'] == p_sel].copy()
        
        takt = st.session_state.get('takt', 261.0)
        demanda = st.session_state.get('demanda', 116)
        tempo_disp = st.session_state.get('tempo_disp', 30312)
        
        if not df_f.empty:
            df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
            tc_total, tc_max = df_f['Tempo (s)'].sum().round(1), df_f.groupby('Posto')['Tempo (s)'].sum().max().round(1)
        else:
            tc_total, tc_max = 0, 0
            
        # --- ABRINDO A DIV DA BORDA GERAL ---
        st.markdown("<div class='folha-impressao'>", unsafe_allow_html=True)
        
        # CABEÇALHO
        st.markdown(f"<div class='caixa-cabecalho' style='font-size:16px;'>TRABALHO PADRONIZADO - CÉLULA {p_sel}</div>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1: st.markdown(f"<div class='caixa-cabecalho'>Elaborado por: {st.session_state.get('elaborador')}</div>", unsafe_allow_html=True)
        with cc2: st.markdown(f"<div class='caixa-cabecalho'>Depto: {st.session_state.get('depto')}</div>", unsafe_allow_html=True)
        with cc3: st.markdown(f"<div class='caixa-cabecalho'>TC Total: {tc_total}s | Gargalo: {tc_max}s | Demanda: {demanda} unid</div>", unsafe_allow_html=True)
        st.write("")
        
        # GRID DO A4
        col_esq, col_meio, col_dir = st.columns([0.8, 2.0, 1.4])
        
        # --- ESQUERDA ---
        with col_esq:
            st.markdown("<div class='caixa-padrao'><b>LEGENDA (Layout)</b><br><br><span class='icon-legenda' style='background:red; border:1px solid yellow;'></span> Andon (Sinalização)<br><br><span class='icon-legenda' style='background:#666;'></span> Estoque Intermediário<br><br><span class='icon-legenda' style='border:1px solid #000; background:#bbb; border-radius:0;'></span> Flow Rack (Ponto de Uso)</div>", unsafe_allow_html=True)
            
            epis_html = "".join([f"<span class='epi-text'>{epi.split(' ')[0]}</span>" for epi in st.session_state.get('epis', [])])
            st.markdown(f"<div class='caixa-padrao' style='text-align:center;'><b>EPI'S EXIGIDOS:</b><br>{epis_html}</div>", unsafe_allow_html=True)

        # --- MEIO: CARTA DE TRABALHO E GANTT ---
        with col_meio:
            st.markdown(f"<div class='titulo-secao'>CARTA DE TRABALHO ({st.session_state.get('layout')})</div>", unsafe_allow_html=True)
            
            postos = df_f['Posto'].unique()
            html_layout = f"<div class='{'layout-u' if st.session_state.get('layout') == 'Célula em U' else 'layout-linha'}'>"
            
            postos_display = list(postos)
            if st.session_state.get('layout') == 'Célula em U' and len(postos_display) > 2:
                metade = (len(postos_display) + 1) // 2
                fileira1 = postos_display[:metade]
                fileira2 = list(reversed(postos_display[metade:]))
                postos_display = fileira1 + fileira2
            
            for i, p_nome in enumerate(postos_display):
                cfg_p = df_c[df_c['Posto'] == p_nome]
                tem_flow = "Sim" in cfg_p['Flow Rack'].values
                tem_andon = "Sim" in cfg_p['Andon'].values
                wip = int(cfg_p['WIP (Estoque)'].values[0]) if not cfg_p.empty else 0
                
                idx_cor = (list(postos).index(p_nome) % 5) + 1
                qtd_ativ = len(df_f[df_f['Posto'] == p_nome])
                bolinhas = "".join([f"<span class='bolinha b-{idx_cor}'>{j+1}</span>" for j in range(qtd_ativ)])
                
                html_posto = f"<div class='caixa-posto'>"
                if tem_andon: html_posto += "<div class='andon'></div>"
                if tem_flow: html_posto += "<div class='flow-rack'>FLOW RACK</div>"
                html_posto += f"<b>{p_nome}</b><hr style='margin:5px 0;'>{bolinhas}<div class='operador'>👤</div>"
                if wip > 0: html_posto += f"<div class='wip-badge'>{wip}</div>"
                html_posto += "</div>"
                html_layout += html_posto
                
            html_layout += "</div>"
            st.markdown(html_layout, unsafe_allow_html=True)

            st.markdown("<div class='titulo-secao'>TABELA COMBINADA (YAMAZUMI)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                fig_gantt = px.bar(df_f, x="Tempo (s)", y="Atividade", base="Início (s)", color="Posto", 
                                   orientation='h', text="Tempo (s)",
                                   color_discrete_sequence=["#00bcd4", "#4caf50", "#e040fb", "#ff9800", "#9c27b0"])
                fig_gantt.add_vline(x=takt, line_dash="solid", line_color="red")
                
                altura_grafico = max(250, len(df_f) * 25)
                fig_gantt.update_layout(
                    yaxis={'autorange': 'reversed', 'title': '', 'visible': True}, 
                    xaxis={'title': 'Tempo (s)'},
                    showlegend=False, 
                    height=altura_grafico, 
                    margin=dict(l=10, r=10, t=10, b=20)
                )
                fig_gantt.update_traces(textposition='inside', insidetextanchor='middle')
                st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_chart")

        # --- DIREITA: GBO E CAPACIDADE ---
        with col_dir:
            st.markdown("<div class='titulo-secao'>GBO (VALOR AGREGADO)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                color_map = {"Agrega": "#00ff00", "Semi Agrega": "#ffff00", "Não Agrega": "#ff9900"}
                fig_gbo = px.bar(df_f, x="Posto", y="Tempo (s)", color="Classificação", color_discrete_map=color_map, text="Tempo (s)", barmode="stack")
                fig_gbo.add_hline(y=takt, line_dash="solid", line_color="red")
                fig_gbo.update_layout(height=240, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                fig_gbo.update_traces(textposition='inside', insidetextanchor='middle')
                st.plotly_chart(fig_gbo, use_container_width=True, key="gbo_chart")
                
                st.markdown("<div style='text-align:center; font-size: 11px; margin-top: 10px;'>"
                            "<span class='icon-legenda' style='background:#00ff00;'></span> Agrega "
                            "<span class='icon-legenda' style='background:#ffff00; margin-left:10px;'></span> Semi Agrega "
                            "<span class='icon-legenda' style='background:#ff9900; margin-left:10px;'></span> Não Agrega"
                            "</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='titulo-secao'>QUADRO DE CAPACIDADE</div>", unsafe_allow_html=True)
            if not df_f.empty:
                df_cap = df_f.groupby('Posto')['Tempo (s)'].sum().reset_index()
                df_cap.rename(columns={'Posto': 'OPERAÇÃO', 'Tempo (s)': 'TC (cronometrado)'}, inplace=True)
                
                # --- APLICANDO A LÓGICA DE CÁLCULO EXATA DO SEU EXCEL ---
                df_cap['TC (saturação)'] = (df_cap['TC (cronometrado)'] * 1.10).round(0).astype(int)
                df_cap['TAKT'] = int(takt)
                
                # CAP. DIÁRIA = Tempo Disponível (ex: 30312) / TC(saturação)
                df_cap['CAP. DIÁRIA'] = (tempo_disp / df_cap['TC (saturação)']).apply(lambda x: round(x, 1) if x > 0 else 0)
                df_cap['OPERADOR RES'] = 1
                
                # CÁLCULO DA CAPACIDADE (%): =(A10/D3)/E3 -> (Tempo_Disp/TAKT) / Cap_Diária
                df_cap['Capacidade (%)'] = (((tempo_disp / df_cap['TAKT']) / df_cap['CAP. DIÁRIA']) * 100).round(2).astype(str) + "%"
                
                df_cap['TAKT objetivo (pçs/dia)'] = int(demanda)
                
                st.dataframe(df_cap, use_container_width=True, hide_index=True)

        # --- FECHANDO A DIV DA BORDA GERAL ---
        st.markdown("</div>", unsafe_allow_html=True)
