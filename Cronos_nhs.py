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
        return pd.DataFrame(columns=["Produto", "Posto", "Flow Rack", "Andon", "WIP (Estoque)"])
    return pd.read_csv(FILE_POSTOS)

st.set_page_config(page_title="CronoNHS 2.0 - A3", layout="wide")

# --- HACK ULTRA ESTRITO DE CSS PARA IMPRESSÃO EM 1 PÁGINA A3 ---
st.markdown("""
    <style>
    /* ---------------------------------------------------
       FORÇAR TODO O CONTEÚDO EM APENAS 1 PÁGINA A3
    --------------------------------------------------- */
    @media print {
        @page { 
            size: A3 landscape; 
            margin: 0mm !important; 
        }
        
        /* Esconde menus do Streamlit, Abas, Título Principal E OS CONTROLES RÁPIDOS */
        header, footer, .stApp > header, .stTabs [data-baseweb="tab-list"], #MainMenu, [data-testid="stSidebar"], h1, .no-print, [data-testid="stMultiSelect"], [data-testid="stSelectbox"] { 
            display: none !important; 
        }
        
        /* Força as cores dos gráficos a aparecerem no papel */
        * { 
            -webkit-print-color-adjust: exact !important; 
            color-adjust: exact !important; 
        }
        
        /* Destrava larguras, elimina paddings e remove barras de rolagem */
        html, body, .stApp, .block-container { 
            width: 100% !important; 
            max-width: 100% !important; 
            background-color: white !important; 
            margin: 0 !important; 
            padding: 0 !important;
            overflow: visible !important;
        }
        
        /* Margem física sutil nas bordas da folha impressa */
        .block-container {
            padding: 5mm 8mm 0mm 8mm !important;
        }
        
        /* Comprime os espaços vazios entre os blocos nativos do Streamlit */
        [data-testid="stVerticalBlock"] {
            gap: 2px !important;
        }
        
        /* ESCALA GLOBAL: Reduz proporcionalmente todo o painel para travar estritamente em 1 página */
        .stMain {
            transform: scale(0.68) !important;
            transform-origin: top left !important;
            width: 147% !important; /* Compensa a perda de largura gerada pelo scale(0.68) */
            height: auto !important;
            page-break-inside: avoid !important;
        }
        
        /* Impede que as colunas quebrem linhas ou criem páginas extra */
        [data-testid="column"] { 
            min-width: 0 !important; 
            page-break-inside: avoid !important;
        }
        
        /* Garante a exibição por inteiro do Quadro de Capacidade (elimina o scroll) */
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
       ESTILOS VISUAIS DO DASHBOARD (TELA)
    --------------------------------------------------- */
    body { font-family: 'Arial', sans-serif; }
    .caixa-cabecalho { border: 1px solid #000; padding: 6px; text-align: center; font-weight: bold; font-size: 13px; background-color: #f4f4f4;}
    .titulo-secao { text-align: center; font-weight: bold; font-size: 14px; margin: 5px 0 8px 0; color: #000; text-transform: uppercase; border-bottom: 2px solid #000;}
    
    /* Legendas e Caixas de Informação */
    .caixa-padrao { border: 1px solid #000; padding: 6px; margin-bottom: 5px; font-size: 11px; background: #fff;}
    .icon-legenda { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px; vertical-align: middle;}
    .epi-text { font-size: 18px; text-align: center; margin: 0 4px; display: inline-block; }
    
    /* Elementos Visuais da Carta de Trabalho */
    .layout-linha { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: nowrap; gap: 8px; }
    .layout-u { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; max-width: 800px; margin: 0 auto;}
    
    .caixa-posto { border: 2px solid #333; padding: 8px; text-align: center; background-color: #fff; position: relative; min-width: 110px; flex: 1;}
    .flow-rack { width: 100%; height: 14px; background: #bbb; border: 1px solid #555; margin-bottom: 8px; font-size: 9px; line-height: 14px; color: #000;}
    .andon { position: absolute; top: -10px; left: -10px; width: 18px; height: 18px; background-color: red; border-radius: 50%; border: 2px solid yellow; box-shadow: 0 0 5px red;}
    .wip-badge { position: absolute; top: 40%; right: -12px; width: 22px; height: 22px; background-color: #666; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; z-index: 10; border: 2px solid #fff;}
    
    .bolinha { display: inline-flex; height: 20px; width: 20px; border-radius: 50%; align-items: center; justify-content: center; color: #000; font-weight: bold; margin: 2px; font-size: 10px;}
    .b-1 { background-color: #00bcd4; }
    .b-2 { background-color: #4caf50; }
    .b-3 { background-color: #e040fb; }
    .b-4 { background-color: #ff9800; }
    .b-5 { background-color: #9c27b0; }
    
    .operador { font-size: 22px; margin-top: 5px; color: #555;}
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
    sub_tab_ativ, sub_tab_postos = st.tabs(["⏱️ Tempos e Atividades", "🏭 Configuração Física (Flow Rack, Andon, WIP)"])
    
    lista_postos = [f"Posto {i}" for i in range(1, int(qtd_postos) + 1)]
    
    with sub_tab_ativ:
        st.markdown("**Passo a Passo das Atividades:**")
        st.info("💡 **Dica:** Para excluir uma linha, clique na pequena caixa vazia na ponta esquerda da linha e carregue na tecla 'Delete' ou 'Backspace' do seu teclado.")
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
        st.success("Guardado com sucesso!")
        st.rerun()


# =====================================================================
# --- ABA 2: DASHBOARD COMPLETO (QUADRANTE A3 EXEMPLAR) ---
# =====================================================================
with tab_dash:
    if not df_tp.empty:
        # Seletor de visualização fica oculto na impressão pelo CSS genérico de selectbox
        p_sel = st.selectbox("Visualizar Célula:", df_tp['Produto'].unique())
        df_f = df_tp[df_tp['Produto'] == p_sel].sort_values(by=["Posto"]).copy()
        df_c = df_cfg[df_cfg['Produto'] == p_sel].copy()
        
        takt = st.session_state.get('takt', 261.0)
        demanda = st.session_state.get('demanda', 116)
        
        if not df_f.empty:
            df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
            tc_total, tc_max = df_f['Tempo (s)'].sum().round(1), df_f.groupby('Posto')['Tempo (s)'].sum().max().round(1)
        else:
            tc_total, tc_max = 0, 0
            
        # 1. CABEÇALHO SUPERIOR UNIFICADO DO A3
        st.markdown(f"<div class='caixa-cabecalho' style='font-size:16px;'>TRABALHO PADRONIZADO - CÉLULA {p_sel}</div>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1: st.markdown(f"<div class='caixa-cabecalho'>Elaborado por: {st.session_state.get('elaborador')}</div>", unsafe_allow_html=True)
        with cc2: st.markdown(f"<div class='caixa-cabecalho'>Depto: {st.session_state.get('depto')}</div>", unsafe_allow_html=True)
        with cc3: st.markdown(f"<div class='caixa-cabecalho'>TC Total: {tc_total}s | Gargalo: {tc_max}s | Demanda: {demanda} unid</div>", unsafe_allow_html=True)
        st.write("")
        
        # Mapeamento de Cores para o GBO e as Pizzas
        color_map = {"Agrega": "#00ff00", "Semi Agrega": "#ffff00", "Não Agrega": "#ff9900"}

        # =====================================================================
        # QUADRANTE SUPERIOR (PARTE DE CIMA)
        # =====================================================================
        col_sup_esq, col_sup_dir = st.columns([1.1, 0.9])
        
        # --- LADO ESQUERDO SUPERIOR: CARTA DE TRABALHO E AJUSTES RÁPIDOS ---
        with col_sup_esq:
            st.markdown(f"<div class='titulo-secao'>CARTA DE TRABALHO ({st.session_state.get('layout')})</div>", unsafe_allow_html=True)
            
            postos_disp = list(df_f['Posto'].unique())
            
            # --- 🛠️ INÍCIO DOS CONTROLES RÁPIDOS ---
            st.markdown("<div class='no-print' style='background:#f4f4f4; padding:10px; border-radius:5px; border:1px solid #ccc; margin-bottom:15px;'><b>⚙️ Ajuste Rápido do Layout (Desaparece na impressão)</b></div>", unsafe_allow_html=True)
            
            # Pega as configurações atuais para deixar selecionado
            andons_atuais = [p for p in postos_disp if not df_c[df_c['Posto']==p].empty and df_c[df_c['Posto']==p]['Andon'].values[0] == 'Sim']
            flows_atuais = [p for p in postos_disp if not df_c[df_c['Posto']==p].empty and df_c[df_c['Posto']==p]['Flow Rack'].values[0] == 'Sim']
            
            c_q1, c_q2 = st.columns(2)
            novos_andons = c_q1.multiselect("📍 Postos com Andon:", postos_disp, default=andons_atuais, key="m_andon")
            novos_flows = c_q2.multiselect("📦 Postos com Flow Rack:", postos_disp, default=flows_atuais, key="m_flow")
            
            # Atualiza os dados imediatamente se o utilizador modificar os controlos na tela
            if set(novos_andons) != set(andons_atuais) or set(novos_flows) != set(flows_atuais):
                for p in postos_disp:
                    idx = df_cfg[(df_cfg['Produto'] == p_sel) & (df_cfg['Posto'] == p)].index
                    if not idx.empty:
                        df_cfg.loc[idx, 'Andon'] = 'Sim' if p in novos_andons else 'Não'
                        df_cfg.loc[idx, 'Flow Rack'] = 'Sim' if p in novos_flows else 'Não'
                # Salva no arquivo CSV para não perder e recarrega na memória
                df_cfg.to_csv(FILE_POSTOS, index=False)
                df_c = df_cfg[df_cfg['Produto'] == p_sel].copy()
            # --- 🛠️ FIM DOS CONTROLES RÁPIDOS ---

            c_leg_epi, c_layout_desenho = st.columns([0.3, 0.7])
            with c_leg_epi:
                st.markdown("<div class='caixa-padrao' style='font-size:10px;'><b>LEGENDA (Layout)</b><br><span class='icon-legenda' style='background:red; border:1px solid yellow;'></span> Andon<br><span class='icon-legenda' style='background:#666;'></span> WIP<br><span class='icon-legenda' style='border:1px solid #000; background:#bbb; border-radius:0;'></span> FlowRack</div>", unsafe_allow_html=True)
                epis_html = "".join([f"<span class='epi-text'>{epi.split(' ')[0]}</span>" for epi in st.session_state.get('epis', [])])
                st.markdown(f"<div class='caixa-padrao' style='text-align:center; font-size:10px;'><b>EPI'S:</b><br>{epis_html}</div>", unsafe_allow_html=True)
                
            with c_layout_desenho:
                postos = df_f['Posto'].unique()
                html_layout = f"<div class='{'layout-u' if st.session_state.get('layout') == 'Célula em U' else 'layout-linha'}'>"
                postos_display = list(postos)
                
                if st.session_state.get('layout') == 'Célula em U' and len(postos_display) > 2:
                    metade = (len(postos_display) + 1) // 2
                    postos_display = postos_display[:metade] + list(reversed(postos_display[metade:]))
                
                for i, p_nome in enumerate(postos_display):
                    cfg_p = df_c[df_c['Posto'] == p_nome]
                    tem_flow = "Sim" in cfg_p['Flow Rack'].values
                    tem_andon = "Sim" in cfg_p['Andon'].values
                    wip = int(cfg_p['WIP (Estoque)'].values[0]) if not cfg_p.empty else 0
                    
                    idx_cor = (list(postos).index(p_nome) % 5) + 1
                    qtd_ativ = len(df_f[df_f['Posto'] == p_nome])
                    bolinhas = "".join([f"<span class='bolinha b-{idx_cor}'>{j+1}</span>" for j in range(qtd_ativ)])
                    
                    html_posto = f"<div class='caixa-posto'>"
                    if tem_andon: 
                        html_posto += f"<div class='andon'></div>"
                    if tem_flow: 
                        html_posto += f"<div class='flow-rack'>FLOW RACK</div>"
                    
                    html_posto += f"<b>{p_nome}</b><hr style='margin:4px 0;'>{bolinhas}<div class='operador'>👤</div>"
                    if wip > 0: html_posto += f"<div class='wip-badge'>{wip}</div>"
                    html_posto += "</div>"
                    html_layout += html_posto
                html_layout += "</div>"
                st.markdown(html_layout, unsafe_allow_html=True)

        # --- LADO DIREITO SUPERIOR: GBO + PIZZAS SINCRO-ALINHADAS ---
        with col_sup_dir:
            st.markdown("<div class='titulo-secao'>GBO (VALOR AGREGADO)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                fig_gbo = px.bar(df_f, x="Posto", y="Tempo (s)", color="Classificação", color_discrete_map=color_map, text="Tempo (s)", barmode="stack")
                fig_gbo.add_hline(y=takt, line_dash="solid", line_color="red")
                
                totais_gbo = df_f.groupby('Posto')['Tempo (s)'].sum()
                for posto, total in totais_gbo.items():
                    fig_gbo.add_annotation(x=posto, y=total, text=f"<b>{round(total, 1)}s</b>", showarrow=False, yshift=10)

                fig_gbo.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
                fig_gbo.update_traces(textposition='inside', insidetextanchor='middle')
                st.plotly_chart(fig_gbo, use_container_width=True, key="gbo_chart")
                
                postos_gbo = sorted(df_f['Posto'].unique())
                cols_pizza = st.columns(len(postos_gbo))
                
                for idx, p_nome in enumerate(postos_gbo):
                    with cols_pizza[idx]:
                        st.markdown(f"<div style='text-align:center; font-size:10px; font-weight:bold; color:#555;'>{p_nome}</div>", unsafe_allow_html=True)
                        df_p_pizza = df_f[df_f['Posto'] == p_nome].groupby('Classificação')['Tempo (s)'].sum().reset_index()
                        
                        fig_p_pie = px.pie(df_p_pizza, values='Tempo (s)', names='Classificação', color='Classificação', color_discrete_map=color_map)
                        fig_p_pie.update_traces(textposition='inside', textinfo='percent')
                        fig_p_pie.update_layout(height=80, margin=dict(l=2, r=2, t=2, b=2), showlegend=False)
                        st.plotly_chart(fig_p_pie, use_container_width=True, key=f"pie_{p_nome}")
                
                st.markdown("<div style='text-align:center; font-size: 11px; margin-top: 4px;'> "
                            "<span class='icon-legenda' style='background:#00ff00;'></span> Agrega "
                            "<span class='icon-legenda' style='background:#ffff00; margin-left:10px;'></span> Semi Agrega "
                            "<span class='icon-legenda' style='background:#ff9900; margin-left:10px;'></span> Não Agrega"
                            "</div>", unsafe_allow_html=True)


        # =====================================================================
        # QUADRANTE INFERIOR (PARTE DE BAIXO)
        # =====================================================================
        st.write(" ")
        col_inf_esq, col_inf_dir = st.columns([1.1, 0.9])
        
        # --- LADO ESQUERDO INFERIOR: TABELA COMBINADA (YAMAZUMI) ---
        with col_inf_esq:
            st.markdown("<div class='titulo-secao'>TABELA COMBINADA (YAMAZUMI)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                fig_gantt = px.bar(df_f, x="Tempo (s)", y="Atividade", base="Início (s)", color="Posto", 
                                   orientation='h', text="Tempo (s)",
                                   color_discrete_sequence=["#00bcd4", "#4caf50", "#e040fb", "#ff9800", "#9c27b0"])
                fig_gantt.add_vline(x=takt, line_dash="solid", line_color="red")
                
                altura_grafico = max(180, len(df_f) * 22)
                fig_gantt.update_layout(
                    yaxis={'autorange': 'reversed', 'title': '', 'visible': True}, 
                    xaxis={'title': 'Tempo (s)'},
                    showlegend=False, 
                    height=altura_grafico, 
                    margin=dict(l=10, r=10, t=5, b=15)
                )
                fig_gantt.update_traces(textposition='inside', insidetextanchor='middle')
                st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_chart")

        # --- LADO DIREITO INFERIOR: QUADRO DE CAPACIDADE (COMPLETO) ---
        with col_inf_dir:
            st.markdown("<div class='titulo-secao'>QUADRO DE CAPACIDADE</div>", unsafe_allow_html=True)
            if not df_f.empty:
                df_cap = df_f.groupby('Posto')['Tempo (s)'].sum().reset_index()
                df_cap.rename(columns={'Posto': 'OPERAÇÃO', 'Tempo (s)': 'TC'}, inplace=True)
                
                df_cap['TC (saturação)'] = (df_cap['TC'] * 1.10).round(0).astype(int)
                df_cap['TAKT'] = int(takt)
                
                df_cap['CAP. DIÁRIA'] = (28800 / df_cap['TC (saturação)']).apply(lambda x: round(x, 1) if x > 0 else 0)
                df_cap['OP.'] = 1  
                df_cap['Capacidade (saturação) %'] = ((df_cap['TC (saturação)'] / takt) * 100).round(2).astype(str) + "%"
                df_cap['TAKT objetivo (pçs/dia)'] = int(demanda)
                
                st.dataframe(df_cap, use_container_width=True, hide_index=True)
