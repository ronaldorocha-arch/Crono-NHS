import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# --- 1. CONFIGURAÇÃO DE FICHEIROS/DADOS ---
FILE_TP = "trabalho_padronizado_dados.csv"
FILE_POSTOS = "config_postos.csv"

def extrair_numero_posto(nome):
    match = re.search(r'\d+', str(nome))
    return int(match.group()) if match else 999

def carregar_tp():
    if not os.path.exists(FILE_TP):
        return pd.DataFrame(columns=["Produto", "Posto", "Atividade", "Tempo (s)", "Classificação"])
    df = pd.read_csv(FILE_TP)
    df['Tempo (s)'] = pd.to_numeric(df['Tempo (s)'], errors='coerce').fillna(0.0)
    return df

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

st.set_page_config(page_title="Trabalho Padronizado - Tecnologia de Processos", layout="wide")

# --- CSS ESTRUTURAL E IMPRESSÃO (CORREÇÃO DEFINITIVA DE CORTE LATERAL) ---
st.markdown("""
    <style>
    @media print {
        header, footer, .stApp > header, .stTabs [data-baseweb="tab-list"], #MainMenu, [data-testid="stSidebar"], h1, .no-print, [data-testid="stMultiSelect"], [data-testid="stSelectbox"], [data-testid="stRadio"], .stExpander { 
            display: none !important; 
        }
        
        * { 
            -webkit-print-color-adjust: exact !important; 
            color-adjust: exact !important; 
            box-sizing: border-box !important; 
        }
        
        html, body, .stApp, .main { 
            width: 100% !important; 
            max-width: 100% !important; 
            background-color: white !important; 
            margin: 0 !important; 
            padding: 0 !important;
            overflow: hidden !important;
        }
        
        /* 🚨 TRAVA DE SEGURANÇA: Limita a 92% da largura da tela para criar uma margem direita forçada 🚨 */
        .block-container { 
            width: 92vw !important; 
            max-width: 92vw !important; 
            margin: 0 !important; 
            padding: 0 !important;
            padding-right: 2vw !important; 
        }
        
        /* Força as colunas a terem exatamente 48% do espaço com 4% de respiro no meio */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            justify-content: space-between !important;
            gap: 4% !important; 
        }
        
        [data-testid="column"] { 
            width: 48% !important;
            flex: 0 0 48% !important; 
            min-width: 0 !important; 
            padding: 0 !important;
            margin: 0 !important;
            page-break-inside: avoid !important;
        }
        
        .js-plotly-plot, .plot-container {
            width: 100% !important;
        }
        
        .stDataFrame, [data-testid="stDataFrame"], [data-testid="stGridVirtualizer"] {
            width: 100% !important;
            overflow: visible !important;
        }
    }
    
    body { font-family: 'Arial', sans-serif; }
    .caixa-cabecalho { border: 1px solid #000; padding: 6px; text-align: center; font-weight: bold; font-size: 14px; background-color: #f4f4f4;}
    .titulo-secao { text-align: center; font-weight: bold; font-size: 15px; margin: 15px 0 10px 0; color: #000; text-transform: uppercase; border-bottom: 2px solid #000;}
    
    .caixa-padrao { border: 1px solid #000; padding: 8px; margin-bottom: 5px; font-size: 12px; background: #fff;}
    .icon-legenda { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px; vertical-align: middle;}
    .epi-text { font-size: 20px; text-align: center; margin: 0 4px; display: inline-block; }
    
    .tabela-cap { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 5px; }
    .tabela-cap th { background-color: #f4f4f4; border: 1px solid #999; padding: 6px; text-align: center !important; font-weight: bold; color: #000;}
    .tabela-cap td { border: 1px solid #999; padding: 6px; text-align: center !important; color: #333;}
    
    .layout-linha { display: flex; justify-content: center; align-items: center; flex-wrap: nowrap; gap: 0px; padding: 40px 10px; width: 100%; overflow-x: auto;}
    
    .caixa-posto { 
        min-width: 120px; 
        flex: 1; 
        height: 120px !important; 
        border: 2px solid #333; 
        background-color: #fff; 
        position: relative; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0px !important; 
    }
    
    .ponto-uso { position: absolute; top: 0; left: -2px; right: -2px; height: 16px; background: #bbb; border-bottom: 1px solid #333; font-size: 10px; line-height: 16px; color: #000; font-weight: bold; z-index: 5; text-align: center;}
    .andon { position: absolute; top: -10px; left: -10px; width: 20px; height: 20px; background-color: red; border-radius: 50%; border: 2px solid yellow; box-shadow: 0 0 5px red; z-index: 10;}
    .wip-badge { position: absolute; bottom: -10px; right: -10px; width: 24px; height: 24px; background-color: #000; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; z-index: 10; border: 2px solid #fff;}
    
    .bolinha { display: inline-flex; height: 22px; width: 22px; border-radius: 50%; align-items: center; justify-content: center; color: #000; font-weight: bold; margin: 2px; font-size: 11px; z-index: 5;}
    .b-1 { background-color: #00bcd4; } .b-2 { background-color: #4caf50; } .b-3 { background-color: #e040fb; } .b-4 { background-color: #ff9800; } .b-5 { background-color: #9c27b0; }
    
    .operador-icon { position: absolute; font-size: 26px; z-index: 10; }
    .op-frente { bottom: -35px; left: calc(50% - 13px); }
    .op-tras { top: -35px; left: calc(50% - 13px); }
    .op-esq { top: calc(50% - 13px); left: -35px; }
    .op-dir { top: calc(50% - 13px); right: -35px; }
    
    .seta-fluxo { font-size: 20px; color: #000; font-weight: bold; margin: 0 8px; flex-shrink: 0;}
    </style>
""", unsafe_allow_html=True)

st.title("📋 Trabalho Padronizado - Tecnologia de Processos")

df_tp = carregar_tp()
df_cfg = carregar_cfg_postos()

tab_cad, tab_dash = st.tabs(["📝 1. Inserir Dados e Layout", "🖥️ 2. Dashboard A3/A4 (Ctrl+P para PDF)"])

# =====================================================================
# --- ABA 1: INSERÇÃO E CONFIGURAÇÃO DE DADOS ---
# =====================================================================
with tab_cad:
    with st.expander("🗑️ Excluir Produto Existente"):
        produtos_salvos = df_tp['Produto'].unique() if not df_tp.empty else []
        if len(produtos_salvos) > 0:
            c_del1, c_del2 = st.columns([3, 1])
            prod_excluir = c_del1.selectbox("Selecione o produto para remover permanentemente:", produtos_salvos)
            if c_del2.button("⚠️ Excluir", use_container_width=True):
                df_tp = df_tp[df_tp["Produto"] != prod_excluir]
                df_cfg = df_cfg[df_cfg["Produto"] != prod_excluir]
                df_tp.to_csv(FILE_TP, index=False)
                df_cfg.to_csv(FILE_POSTOS, index=False)
                if st.session_state.get('produto_ativo') == prod_excluir:
                    st.session_state['produto_ativo'] = ""
                st.success(f"Produto '{prod_excluir}' foi apagado.")
                st.rerun()
        else:
            st.info("Nenhum produto cadastrado no momento.")

    col_info1, col_info2 = st.columns(2)
    elaborador = col_info1.text_input("Elaborado por:", value=st.session_state.get('elaborador', ""))
    depto = col_info2.text_input("Departamento:", value=st.session_state.get('depto', "Tecnologia de Processos"))
    
    st.write("---")
    
    modo = st.radio("Ação:", ["➕ Criar Novo Produto", "✏️ Editar Produto Existente"], horizontal=True)
    produtos_cadastrados = list(df_tp['Produto'].unique()) if not df_tp.empty else []
    
    c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1])
    
    if modo == "✏️ Editar Produto Existente" and produtos_cadastrados:
        prod = c1.selectbox("Selecione o Produto:", produtos_cadastrados)
        cfg_existente = df_cfg[df_cfg["Produto"] == prod]
        postos_existentes = len(cfg_existente) if not cfg_existente.empty else 4
        qtd_postos = c2.number_input("Nº de Postos", min_value=1, value=postos_existentes)
    else:
        if modo == "✏️ Editar Produto Existente" and not produtos_cadastrados:
            st.warning("Nenhum produto salvo ainda. Você está no modo de criação.")
        prod = c1.text_input("Nome do Novo Produto", value="")
        qtd_postos = c2.number_input("Nº de Postos", min_value=1, value=4)
        
    takt_input = c3.number_input("Takt Time (s)", min_value=1.0, value=261.0)
    demanda_input = c4.number_input("Demanda Diária", min_value=1, value=116)
    tempo_disp_input = c5.number_input("Tempo Disp. (s)", min_value=1, value=30312)
    
    epis_selecionados = st.multiselect("EPIs Necessários", ["🥽 Óculos", "🥼 Jaleco", "👞 Sapato", "🧤 Luvas", "🎧 Protetor", "🧢 Touca"], default=["🥽 Óculos", "🥼 Jaleco", "👞 Sapato", "🧤 Luvas"])
    
    st.session_state.update({'elaborador': elaborador, 'depto': depto, 'takt': takt_input, 'demanda': demanda_input, 'tempo_disp': tempo_disp_input, 'epis': epis_selecionados, 'layout': 'Em Linha'})

    st.write("---")
    sub_tab_ativ, sub_tab_postos = st.tabs(["⏱️ Tempos e Atividades", "🏭 Configuração Física (Ponto Uso, Andon, WIP, Operador)"])
    
    lista_postos = [f"Posto {i}" for i in range(1, int(qtd_postos) + 1)]
    
    with sub_tab_ativ:
        st.markdown("**Passo a Passo das Atividades:**")
        
        df_prod = df_tp[df_tp["Produto"] == prod].copy()
        
        if df_prod.empty and prod != "": 
            df_prod = pd.DataFrame({
                "Produto": [prod] * int(qtd_postos),
                "Posto": lista_postos,
                "Atividade": [""] * int(qtd_postos),
                "Tempo (s)": [0.0] * int(qtd_postos),
                "Classificação": ["Agrega"] * int(qtd_postos)
            })
            
        df_prod['num_posto'] = df_prod['Posto'].apply(extrair_numero_posto)
        df_prod = df_prod.sort_values('num_posto').drop(columns=['num_posto']).reset_index(drop=True)
        
        st.info("💡 Dica: Adicione atividades no final da tabela. Elas se agruparão automaticamente com o posto correto ao salvar.")
        
        edited_df = st.data_editor(
            df_prod, 
            num_rows="dynamic", 
            use_container_width=True,
            hide_index=True,
            column_order=["Posto", "Atividade", "Tempo (s)", "Classificação"], 
            column_config={
                "Posto": st.column_config.SelectboxColumn("Posto", options=lista_postos, required=True),
                "Atividade": st.column_config.TextColumn("Descrição", required=True),
                "Tempo (s)": st.column_config.NumberColumn("Tempo (s)", format="%.1f", required=True),
                "Classificação": st.column_config.SelectboxColumn("Agregação de Valor", options=["Agrega", "Semi Agrega", "Não Agrega"], required=True)
            }
        )
        
    with sub_tab_postos:
        st.markdown("**Mapeamento do Layout da Linha:**")
        df_cfg_prod = df_cfg[df_cfg["Produto"] == prod].copy()
        
        if df_cfg_prod.empty or len(df_cfg_prod) != len(lista_postos):
            df_cfg_prod = pd.DataFrame({
                "Posto": lista_postos, 
                "Ponto de Uso": ["Não"]*len(lista_postos), 
                "Andon": ["Não"]*len(lista_postos), 
                "WIP": [0]*len(lista_postos), 
                "Posição Operador": ["Frente"]*len(lista_postos)
            })
        
        edited_cfg = st.data_editor(
            df_cfg_prod, hide_index=True, use_container_width=True,
            column_config={
                "Posto": st.column_config.TextColumn("Posto", disabled=True),
                "Ponto de Uso": st.column_config.SelectboxColumn("Possui Ponto de Uso?", options=["Sim", "Não"]),
                "Andon": st.column_config.SelectboxColumn("Possui Andon?", options=["Sim", "Não"]),
                "WIP": st.column_config.NumberColumn("Qtd de WIP", min_value=0, step=1),
                "Posição Operador": st.column_config.SelectboxColumn("Onde fica o Operador?", options=["Frente", "Trás", "Esquerda", "Direita"])
            }
        )
        
    if st.button("💾 SALVAR PRODUTO E CONFIGURAÇÕES", type="primary", use_container_width=True):
        if prod.strip() == "":
            st.error("Por favor, digite um nome para o Produto antes de salvar.")
        else:
            edited_df["Produto"] = prod
            edited_df['num_posto'] = edited_df['Posto'].apply(extrair_numero_posto)
            edited_df = edited_df.sort_values('num_posto').drop(columns=['num_posto'])
            
            pd.concat([df_tp[df_tp["Produto"] != prod], edited_df], ignore_index=True).to_csv(FILE_TP, index=False)
            
            edited_cfg["Produto"] = prod
            pd.concat([df_cfg[df_cfg["Produto"] != prod], edited_cfg], ignore_index=True).to_csv(FILE_POSTOS, index=False)
            
            st.session_state['produto_ativo'] = prod 
            st.success("Guardado com sucesso e postos agrupados!")
            st.rerun()

# =====================================================================
# --- ABA 2: DASHBOARD COMPLETO (QUADRANTE A3/A4) ---
# =====================================================================
with tab_dash:
    df_tp = carregar_tp()
    df_cfg = carregar_cfg_postos()
    
    if not df_tp.empty:
        st.markdown("<div class='no-print' style='background:#eef7ff; padding:15px; border-radius:5px; border:1px solid #b3d4fc; margin-bottom:15px;'><b style='color:#0056b3; font-size: 15px;'>🖨️ Tamanho da Impressão (Ctrl+P)</b><br><span style='font-size: 13px; color: #555;'>Selecione a folha abaixo antes de imprimir. O sistema ajustará o zoom automaticamente para evitar cortes.</span></div>", unsafe_allow_html=True)
        tam_folha = st.radio("Selecione o tamanho:", ["A3", "A4"], horizontal=True, label_visibility="collapsed")

        if tam_folha == "A4":
            st.markdown("""
                <style>
                @media print {
                    @page { size: A4 landscape; margin: 5mm !important; }
                    .block-container { zoom: 0.60 !important; }
                }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                @media print {
                    @page { size: A3 landscape; margin: 5mm !important; }
                    .block-container { zoom: 0.90 !important; }
                }
                </style>
            """, unsafe_allow_html=True)

        lista_produtos = list(df_tp['Produto'].unique())
        idx_selecionado = 0
        if st.session_state.get('produto_ativo') in lista_produtos:
            idx_selecionado = lista_produtos.index(st.session_state['produto_ativo'])

        p_sel = st.selectbox("Visualizar Célula:", lista_produtos, index=idx_selecionado)
        df_f = df_tp[df_tp['Produto'] == p_sel].sort_values(by=["Posto"]).copy()
        df_c = df_cfg[df_cfg['Produto'] == p_sel].copy()
        
        takt = st.session_state.get('takt', 261.0)
        demanda = st.session_state.get('demanda', 116)
        tempo_disp = st.session_state.get('tempo_disp', 30312)
        
        if not df_f.empty:
            df_f['num_posto'] = df_f['Posto'].apply(extrair_numero_posto)
            df_f = df_f.sort_values(['num_posto']).reset_index(drop=True)
            
            df_f['Início (s)'] = df_f.groupby('Posto')['Tempo (s)'].cumsum() - df_f['Tempo (s)']
            tc_total, tc_max = df_f['Tempo (s)'].sum().round(1), df_f.groupby('Posto')['Tempo (s)'].sum().max().round(1)
            
            df_f['Passo_Unico'] = (df_f.index + 1).astype(str) + ". " + df_f['Atividade']
        else:
            tc_total, tc_max = 0, 0
            
        st.markdown(f"<div class='caixa-cabecalho' style='font-size:16px;'>TRABALHO PADRONIZADO - CÉLULA {p_sel}</div>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1: st.markdown(f"<div class='caixa-cabecalho'>Elaborado por: {st.session_state.get('elaborador')}</div>", unsafe_allow_html=True)
        with cc2: st.markdown(f"<div class='caixa-cabecalho'>Depto: {st.session_state.get('depto')}</div>", unsafe_allow_html=True)
        with cc3: st.markdown(f"<div class='caixa-cabecalho'>Tc total: {tc_total}s | Gargalo: {tc_max}s | Demanda: {demanda} unid</div>", unsafe_allow_html=True)
        st.write("")
        
        color_map = {"Agrega": "#00ff00", "Semi Agrega": "#ffff00", "Não Agrega": "#ff9900"}

        col_sup_esq, col_sup_dir = st.columns([1, 1])
        
        with col_sup_esq:
            st.markdown(f"<div class='titulo-secao'>CARTA DE TRABALHO</div>", unsafe_allow_html=True)
            
            postos_disp = list(df_c['Posto'].unique())
            postos_disp.sort(key=extrair_numero_posto)
            
            st.markdown("<div class='no-print' style='background:#f4f4f4; padding:10px; border-radius:5px; border:1px solid #ccc; margin-bottom:15px;'><b>⚙️ Ajuste Rápido do Layout</b></div>", unsafe_allow_html=True)
            
            andons_atuais = [p for p in postos_disp if not df_c[df_c['Posto']==p].empty and df_c[df_c['Posto']==p]['Andon'].values[0] == 'Sim']
            flows_atuais = [p for p in postos_disp if not df_c[df_c['Posto']==p].empty and df_c[df_c['Posto']==p]['Ponto de Uso'].values[0] == 'Sim']
            
            c_q1, c_q2 = st.columns(2)
            novos_andons = c_q1.multiselect("📍 Postos com Andon:", postos_disp, default=andons_atuais, key="m_andon")
            novos_flows = c_q2.multiselect("📦 Postos com Ponto de Uso:", postos_disp, default=flows_atuais, key="m_flow")
            
            if set(novos_andons) != set(andons_atuais) or set(novos_flows) != set(flows_atuais):
                for p in postos_disp:
                    idx = df_cfg[(df_cfg['Produto'] == p_sel) & (df_cfg['Posto'] == p)].index
                    if not idx.empty:
                        df_cfg.loc[idx, 'Andon'] = 'Sim' if p in novos_andons else 'Não'
                        df_cfg.loc[idx, 'Ponto de Uso'] = 'Sim' if p in novos_flows else 'Não'
                df_cfg.to_csv(FILE_POSTOS, index=False)
                df_c = df_cfg[df_cfg['Produto'] == p_sel].copy()

            c_leg_epi, c_layout_desenho = st.columns([0.3, 0.7])
            with c_leg_epi:
                st.markdown("<div class='caixa-padrao'><b>LEGENDA (Layout)</b><br><span class='icon-legenda' style='background:red; border:1px solid yellow;'></span> Andon<br><span class='icon-legenda' style='background:#000;'></span> WIP<br><span class='icon-legenda' style='border:1px solid #000; background:#bbb; border-radius:0;'></span> Ponto de Uso</div>", unsafe_allow_html=True)
                epis_html = "".join([f"<span class='epi-text'>{epi.split(' ')[0]}</span>" for epi in st.session_state.get('epis', [])])
                st.markdown(f"<div class='caixa-padrao' style='text-align:center;'><b>EPI'S:</b><br>{epis_html}</div>", unsafe_allow_html=True)
                
            with c_layout_desenho:
                html_layout = "<div class='layout-linha'>"
                postos_display = list(postos_disp)
                
                for i, p_nome in enumerate(postos_display):
                    cfg_p = df_c[df_c['Posto'] == p_nome]
                    tem_flow = "Sim" in cfg_p['Ponto de Uso'].values
                    tem_andon = "Sim" in cfg_p['Andon'].values
                    wip = int(cfg_p['WIP'].values[0]) if not cfg_p.empty else 0
                    pos_op = cfg_p['Posição Operador'].values[0] if 'Posição Operador' in cfg_p.columns and not cfg_p.empty else 'Frente'
                    
                    idx_cor = (extrair_numero_posto(p_nome) % 5) + 1
                    qtd_ativ = len(df_f[(df_f['Posto'] == p_nome) & (df_f['Tempo (s)'] > 0)])
                    bolinhas = "".join([f"<span class='bolinha b-{idx_cor}'>{j+1}</span>" for j in range(qtd_ativ)])
                    
                    html_posto = f"<div class='caixa-posto'>"
                    
                    html_posto += f"<div style='margin-top: {'15px' if tem_flow else '0px'}; font-size:13px;'><b>{p_nome}</b><hr style='margin:4px 0;'>{bolinhas}</div>"
                    
                    if tem_andon: 
                        html_posto += f"<div class='andon'></div>"
                    if tem_flow: 
                        html_posto += f"<div class='ponto-uso'>PONTO DE USO</div>"
                    if wip > 0: 
                        html_posto += f"<div class='wip-badge'>{wip}</div>"
                        
                    if pos_op == 'Trás': html_posto += f"<div class='operador-icon op-tras'>👤</div>"
                    elif pos_op == 'Esquerda': html_posto += f"<div class='operador-icon op-esq'>👤</div>"
                    elif pos_op == 'Direita': html_posto += f"<div class='operador-icon op-dir'>👤</div>"
                    else: html_posto += f"<div class='operador-icon op-frente'>👤</div>"
                    
                    html_posto += "</div>"
                    html_layout += html_posto
                    
                    if i < len(postos_display) - 1:
                        html_layout += "<div class='seta-fluxo'>&#10140;</div>"
                        
                html_layout += "</div>"
                st.markdown(html_layout, unsafe_allow_html=True)

        with col_sup_dir:
            st.markdown("<div class='titulo-secao'>GBO (VALOR AGREGADO)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                fig_gbo = px.bar(df_f, x="Posto", y="Tempo (s)", color="Tempo (s)", 
                                 color_continuous_scale=["#A0CBE8", "#629BCE", "#2C69B0"], text="Tempo (s)", barmode="stack")
                fig_gbo.add_hline(y=takt, line_dash="solid", line_color="red")
                
                totais_gbo = df_f.groupby('Posto')['Tempo (s)'].sum()
                max_val = max(totais_gbo.max(), takt) if not totais_gbo.empty else takt

                for posto, total in totais_gbo.items():
                    fig_gbo.add_annotation(
                        x=posto, y=total, 
                        text=f"<b style='font-size:14px; color:#000;'>{round(total, 1)}s</b>", 
                        showarrow=False, yshift=15
                    )

                fig_gbo.update_layout(height=260, margin=dict(l=0, r=0, t=30, b=0), showlegend=False, coloraxis_showscale=False)
                fig_gbo.update_yaxes(range=[0, max_val * 1.25]) 
                fig_gbo.update_traces(textposition='inside', insidetextanchor='middle', marker_line_color='black', marker_line_width=1)
                st.plotly_chart(fig_gbo, use_container_width=True, key="gbo_chart")
                
                postos_gbo = sorted(df_f['Posto'].unique(), key=extrair_numero_posto)
                cols_pizza = st.columns(len(postos_gbo))
                
                for idx, p_nome in enumerate(postos_gbo):
                    with cols_pizza[idx]:
                        st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; color:#555;'>{p_nome}</div>", unsafe_allow_html=True)
                        df_p_pizza = df_f[df_f['Posto'] == p_nome].groupby('Classificação')['Tempo (s)'].sum().reset_index()
                        
                        fig_p_pie = px.pie(df_p_pizza, values='Tempo (s)', names='Classificação', color='Classificação', color_discrete_map=color_map)
                        fig_p_pie.update_traces(textposition='inside', textinfo='percent')
                        fig_p_pie.update_layout(height=120, margin=dict(l=2, r=2, t=2, b=2), showlegend=False)
                        st.plotly_chart(fig_p_pie, use_container_width=True, key=f"pie_{p_nome}")
                
                st.markdown("<div style='text-align:center; font-size: 13px; margin-top: 10px;'> "
                            "<span class='icon-legenda' style='background:#00ff00;'></span> Agrega "
                            "<span class='icon-legenda' style='background:#ffff00; margin-left:15px;'></span> Semi Agrega "
                            "<span class='icon-legenda' style='background:#ff9900; margin-left:15px;'></span> Não Agrega"
                            "</div>", unsafe_allow_html=True)

        st.write(" ")
        col_inf_esq, col_inf_dir = st.columns([1, 1])
        
        with col_inf_esq:
            st.markdown("<div class='titulo-secao'>TABELA COMBINADA (YAMAZUMI)</div>", unsafe_allow_html=True)
            if not df_f.empty:
                fig_gantt = px.bar(df_f, x="Tempo (s)", y="Passo_Unico", base="Início (s)", color="Posto", 
                                   orientation='h', text="Tempo (s)",
                                   color_discrete_sequence=["#00bcd4", "#4caf50", "#e040fb", "#ff9800", "#9c27b0"])
                fig_gantt.add_vline(x=takt, line_dash="solid", line_color="red")
                
                altura_grafico = max(260, len(df_f) * 26)
                fig_gantt.update_layout(
                    yaxis={'autorange': 'reversed', 'title': '', 'visible': True}, 
                    xaxis={'title': 'Tempo (s)'},
                    showlegend=False, 
                    height=altura_grafico, 
                    margin=dict(l=10, r=10, t=10, b=15)
                )
                fig_gantt.update_traces(textposition='inside', insidetextanchor='middle')
                st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_chart")

        with col_inf_dir:
            st.markdown("<div class='titulo-secao'>QUADRO DE CAPACIDADE</div>", unsafe_allow_html=True)
            if not df_f.empty:
                df_cap = df_f.groupby('Posto')['Tempo (s)'].sum().reset_index()
                df_cap['num_posto'] = df_cap['Posto'].apply(extrair_numero_posto)
                df_cap = df_cap.sort_values('num_posto').drop(columns=['num_posto'])
                
                df_cap.rename(columns={'Posto': 'Operação', 'Tempo (s)': 'Tc'}, inplace=True)
                
                df_cap['Tc<br>(saturação)'] = (df_cap['Tc'] * 1.10).round(0).astype(int)
                df_cap['Takt'] = int(takt)
                df_cap['Cap.<br>diária'] = (tempo_disp / df_cap['Tc<br>(saturação)']).apply(lambda x: round(x, 1) if x > 0 else 0)
                df_cap['Op.'] = 1  
                
                df_cap['Capacidade<br>(saturação) %'] = df_cap.apply(
                    lambda row: f"{round(((tempo_disp / row['Takt']) / row['Cap.<br>diária']) * 100, 2)}%" if row['Cap.<br>diária'] > 0 else "0%", 
                    axis=1
                )
                
                df_cap['Demanda<br>(pçs/dia)'] = int(demanda)
                
                colunas_mostrar = ['Operação', 'Tc', 'Tc<br>(saturação)', 'Takt', 'Cap.<br>diária', 'Op.', 'Capacidade<br>(saturação) %', 'Demanda<br>(pçs/dia)']
                df_cap_display = df_cap[colunas_mostrar]
                
                tabela_html = df_cap_display.to_html(index=False, classes="tabela-cap", escape=False)
                st.markdown(tabela_html, unsafe_allow_html=True)
