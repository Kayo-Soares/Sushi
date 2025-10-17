# app_custos_filiais.py (enxuto — pergunta fixa em Markdown)
import streamlit as st
import pandas as pd
import re
from pathlib import Path

# ---------- Config ----------
st.set_page_config(page_title="Ranking de Custos por Filial", layout="wide")
FILE_PATH = Path(“./Base de Dados - Teste de Gestão de Custos (2).xlsx")
SHEET_NAME = "Banco"

# ---------- Utilitários mínimos ----------
def norm(s): return re.sub(r'[^a-z0-9]+','_', ''.join(ch for ch in str(s).lower().strip()))
def find_col(df, keys):
    norm_map = {norm(c): c for c in df.columns}
    for k in keys:
        for n, orig in norm_map.items():
            if k in n: return orig
    return None

def read_sheet(path, sheet):
    df0 = pd.read_excel(path, sheet_name=sheet, header=0, engine="openpyxl")
    if len(df0)>0 and all((pd.isna(x) or (isinstance(x,str) and x.strip()=="")) for x in df0.iloc[0]):
        return pd.read_excel(path, sheet_name=sheet, header=1, engine="openpyxl")
    return df0

def to_num(s):
    s = s.astype(str).fillna("").str.strip().replace(r'^\s*$','', regex=True)
    s = s.str.replace(r'[Rr]\$\s*','', regex=True).str.replace(r'[^\d,.-]','', regex=True)
    def conv(x):
        if x == "" or pd.isna(x): return pd.NA
        if x.count(',')>0 and x.count('.')==0: x = x.replace('.','').replace(',','.')
        elif x.count('.')>1: x = x.replace('.','')
        try: return float(x)
        except: return pd.NA
    return s.map(conv)

def format_brl_val(x):
    try: x = float(x)
    except: return ""
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s

def extract_code(v):
    if pd.isna(v): return None
    m = re.match(r'^\s*(\d{1,4})\b', str(v).strip())
    if m:
        try: return int(m.group(1))
        except: return None
    if isinstance(v,(int,float)) and not pd.isna(v):
        return int(v)
    return None

# ---------- App ----------
st.title("📊 Ranking de Custos por Filial — Distribuição")

# pergunta fixa (Markdown)
st.markdown("**Pergunta:** Realizar dinâmica para organização dos custos por filial, ranqueando do maior custo para o menor custo considerando o CUSTO TOTAL (todos os grupos) e CUSTO DE FRETE (somente grupo 84). Importante: a unidade de São Paulo é composta de dois códigos de filiais = 28 e 80, logo precisam ser consolidados na análise.")

# leitura
try:
    df = read_sheet(FILE_PATH, SHEET_NAME)
except FileNotFoundError:
    st.error(f"Arquivo não encontrado: {FILE_PATH}")
    st.stop()
except Exception as e:
    st.error(f"Erro ao ler a aba '{SHEET_NAME}': {e}")
    st.stop()

# detectar colunas essenciais
col_nome = find_col(df, ['nome','filial_nome'])
col_code = find_col(df, ['filial','codigo_filial','cod_filial'])
col_val = find_col(df, ['valor','valores','total'])
col_frete = find_col(df, ['frete','apenas_frete','so_frete'])
col_distrib = find_col(df, ['apenas_distribuicao','apenas_distrib','distribuicao'])

if not (col_nome and col_val and col_frete):
    st.error("Não foi possível identificar colunas obrigatórias (Nome Filial / Valores / Apenas Frete). Colunas detectadas: " + ", ".join(df.columns))
    st.stop()

# preparar dados
df['__nome__'] = df[col_nome].astype(str).fillna("").str.strip()
df['__code__'] = df.get(col_code)
df['__code2__'] = df['__nome__'].apply(extract_code)
def code_final(r):
    for v in (r.get(col_code), r.get('__code__'), r.get('__code2__')):
        if pd.notna(v):
            try: return int(v)
            except: pass
    return None
df['__code_final__'] = df.apply(lambda r: code_final(r), axis=1)

def consolidate(r):
    c = r['__code_final__']; n = r['__nome__']
    if c in (28,80): return "São Paulo"
    if isinstance(n,str) and re.search(r'\b(sao ?paulo|s\.? ?paulo)\b', n, flags=re.I): return "São Paulo"
    return n
df['Nome Filial'] = df.apply(consolidate, axis=1)

# filtro por Apenas_Distribuicao (se existir)
if col_distrib:
    opts = ["Todos"] + sorted(df[col_distrib].dropna().astype(str).str.strip().unique().tolist())
    sel = st.selectbox("Filtro (Apenas_Distribuicao)", opts, index=0)
    if sel != "Todos":
        df = df[df[col_distrib].astype(str).str.strip() == sel].copy()

# converter colunas numéricas
df['_val_'] = to_num(df[col_val])
df['_frete_'] = to_num(df[col_frete])

# agregação
agg = df.groupby('Nome Filial', dropna=False).agg(
    custo_total = pd.NamedAgg(column='_val_', aggfunc='sum'),
    custo_frete = pd.NamedAgg(column='_frete_', aggfunc='sum')
).reset_index().fillna(0.0)

agg = agg.sort_values('custo_total', ascending=False).reset_index(drop=True)
agg.index += 1
agg['Ranking'] = agg.index

# preparar display (renomear/formatar)
disp = agg[['Ranking','Nome Filial','custo_total','custo_frete']].copy()
disp['CUSTO TOTAL'] = disp['custo_total'].map(format_brl_val)
disp['CUSTO FRETE'] = disp['custo_frete'].map(format_brl_val)
disp_display = disp[['Ranking','Nome Filial','CUSTO TOTAL','CUSTO FRETE']].copy()

# linha total
tot_ct = agg['custo_total'].sum(); tot_cf = agg['custo_frete'].sum()
total_row = {'Ranking':'—','Nome Filial':'Total Geral','CUSTO TOTAL':format_brl_val(tot_ct),'CUSTO FRETE':format_brl_val(tot_cf)}
disp_display_tot = pd.concat([disp_display, pd.DataFrame([total_row])], ignore_index=True)

# exibição HTML para esconder índice e manter ordenação/colunas
st.markdown("### Resultado da análise")
st.markdown(disp_display_tot.to_html(index=False, justify='left', classes='table table-striped', border=0), unsafe_allow_html=True)

# download CSV (numérico, sem linha de total)
st.download_button("⬇️ Baixar CSV (agregado por filial)", agg[['Ranking','Nome Filial','custo_total','custo_frete']].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), file_name="custos_por_filial_aggregado.csv", mime="text/csv")


