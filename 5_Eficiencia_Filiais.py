# streamlit_minha_analise_v3.py
import streamlit as st
import pandas as pd
import numpy as np
import re
import unicodedata
from pathlib import Path

st.set_page_config(page_title="Análise de Eficiência por Filial", layout="wide")
st.title("✅ Análise de Eficiência por Filial — Acumulado 2017 vs 2018")
# --- Pergunta / enunciado (solicitado)
st.markdown(
    "**Pergunta:** Com base nos estudos dos custos realizados, determinar qual  das filiais é a mais eficiente")

# -------- CONFIG (use seu caminho) --------
FILE_PATH = Path(
    r"C:\Users\emiva\OneDrive\Área de Trabalho\Streamlit Sushi Boulevard\Base de Dados - Teste de Gestão de Custos (2).xlsx"
)
SHEET_NAME = "Banco"

if not FILE_PATH.exists():
    st.error(f"Arquivo não encontrado em:\n{FILE_PATH}\nVerifique o caminho e se o Streamlit tem acesso ao arquivo.")
    st.stop()

# -------- helpers --------
def norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

def find_col(df, candidates):
    norm_map = {norm(c): c for c in df.columns}
    for cand in candidates:
        cand_norm = norm(cand)
        for n, orig in norm_map.items():
            if cand_norm in n:
                return orig
    return None

def to_numeric(col):
    if col is None:
        return pd.Series(dtype=float)
    if col.dtype == object or pd.api.types.is_string_dtype(col):
        s = col.astype(str).fillna("").str.strip()
        s = s.str.replace(r'[R$\s]', '', regex=True)
        has_point = s.str.contains(r'\.').any()
        has_comma = s.str.contains(r',').any()
        if has_point and has_comma:
            s = s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        else:
            s = s.str.replace(',', '.', regex=False)
        s = s.replace('', np.nan)
        return pd.to_numeric(s, errors='coerce')
    else:
        return pd.to_numeric(col, errors='coerce')

def fmt_br_money(v):
    try:
        if pd.isna(v):
            return "R$ 0,00"
        s = f"{float(v):,.2f}"          # "1,234,567.89"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")  # -> "1.234.567,89"
        return f"R$ {s}"
    except:
        return "R$ 0,00"

def min_max_norm(s):
    if s.max() == s.min():
        return pd.Series(0.0, index=s.index)
    return (s - s.min()) / (s.max() - s.min())

# -------- load sheet (detecção robusta de cabeçalho) --------
raw = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME, header=None)
header_idx = None
for i, row in raw.iterrows():
    if row.dropna().shape[0] > 0:
        header_idx = i
        break

if header_idx is None:
    st.error("Não foi possível detectar um cabeçalho na planilha.")
    st.stop()

raw.columns = list(range(raw.shape[1]))
header = raw.iloc[header_idx].fillna('').astype(str).str.strip()
df = raw.iloc[header_idx + 1 :].copy()
df.columns = header
df = df.loc[:, df.notna().any(axis=0)]
df = df.reset_index(drop=True)

# -------- identificar colunas --------
col_nome_filial = find_col(df, ["nome filial", "nome_filial", "filial", "nome filial normalizado", "nome"])
col_apenas_dist = find_col(df, ["apenas_distribuicao", "apenas distribuicao", "apenas distribuição", "apenas", "distribuicao", "distribuição"])
col_total_2017 = find_col(df, ["total 2017", "total2017", "total_2017", "2017"])
col_total_2018 = find_col(df, ["total 2018", "total2018", "total_2018", "2018"])

if col_nome_filial is None:
    st.error("Não encontrei a coluna de 'Nome Filial'. Verifique o nome da coluna na planilha.")
    st.stop()
if col_total_2017 is None or col_total_2018 is None:
    st.error("Não encontrei as colunas 'Total 2017' e/ou 'Total 2018'. Verifique os nomes na planilha.")
    st.stop()

# padroniza nome filial
df = df.rename(columns={col_nome_filial: "Nome Filial"})

# converte totais em numérico
df[col_total_2017] = to_numeric(df[col_total_2017])
df[col_total_2018] = to_numeric(df[col_total_2018])

# criar flag apenas distribuição (se existir coluna)
if col_apenas_dist is not None:
    s_flag = df[col_apenas_dist].astype(str).str.lower().str.strip()
    df["_apenas_dist_bool"] = s_flag.isin(["sim","s","true","1","yes","y"]) | s_flag.str.contains("distrib", na=False)
else:
    df["_apenas_dist_bool"] = False

# -------- agregação por filial --------
agg = df.groupby("Nome Filial", dropna=False).agg(
    Total_2017 = (col_total_2017, "sum"),
    Total_2018 = (col_total_2018, "sum")
).reset_index()

apenas = df[df["_apenas_dist_bool"]].groupby("Nome Filial", dropna=False).agg(
    Apenas_Distribuicao_2018 = (col_total_2018, "sum")
).reset_index()

agg = agg.merge(apenas, on="Nome Filial", how="left")
agg["Apenas_Distribuicao_2018"] = agg["Apenas_Distribuicao_2018"].fillna(0.0)
agg["Total_2017"] = agg["Total_2017"].fillna(0.0)
agg["Total_2018"] = agg["Total_2018"].fillna(0.0)

# -------- métricas --------
agg["Delta_Abs"] = agg["Total_2018"] - agg["Total_2017"]
agg["Delta_Pct"] = np.where(agg["Total_2017"] == 0, np.nan,
                            (agg["Total_2018"] - agg["Total_2017"]) / agg["Total_2017"] * 100)
agg["Distrib_Share"] = np.where(agg["Total_2018"] == 0, 0.0,
                                agg["Apenas_Distribuicao_2018"] / agg["Total_2018"])

# normalizações e score (mesma lógica)
agg["total2018_norm"] = min_max_norm(agg["Total_2018"])
agg["improvement"] = np.where(agg["Total_2017"] == 0, 0.0,
                              (agg["Total_2017"] - agg["Total_2018"]) / agg["Total_2017"])
agg["improvement_norm"] = min_max_norm(agg["improvement"])
agg["dist_share_norm"] = min_max_norm(agg["Distrib_Share"])

# Efficiency Score: pesos fixos (sem controles no sidebar)
w_total, w_improv, w_dist = 0.60, 0.30, 0.10
agg["Efficiency_Score"] = (
    w_total * agg["total2018_norm"]
    + w_improv * (1 - agg["improvement_norm"])
    + w_dist * agg["dist_share_norm"]
)

agg = agg.sort_values("Efficiency_Score").reset_index(drop=True)

# -------- único filtro no sidebar: filiais --------
st.sidebar.markdown("### Filiais")
filiais_all = agg["Nome Filial"].dropna().astype(str).tolist()
selected_filials = st.sidebar.multiselect("", options=filiais_all, default=filiais_all)

filtered = agg.copy()
if selected_filials:
    filtered = filtered[filtered["Nome Filial"].isin(selected_filials)]

# -------- exibição tabela --------
st.subheader("Tabela resumida por filial (ordenada por Efficiency Score — menor melhor)")
display = filtered[[
    "Nome Filial", "Total_2017", "Total_2018", "Apenas_Distribuicao_2018", "Delta_Abs", "Delta_Pct", "Distrib_Share", "Efficiency_Score"
]].copy()

display["Total 2017"] = display["Total_2017"].map(fmt_br_money)
display["Total 2018"] = display["Total_2018"].map(fmt_br_money)
display["Apenas Distribuição (2018)"] = display["Apenas_Distribuicao_2018"].map(fmt_br_money)
display["Delta Absoluto"] = display["Delta_Abs"].map(fmt_br_money)
display["Δ %"] = display["Delta_Pct"].map(lambda v: "" if pd.isna(v) else f"{v:.2f}%")
display["Distrib Share"] = display["Distrib_Share"].map(lambda v: f"{v:.2%}")
display["Efficiency Score"] = display["Efficiency_Score"].map(lambda v: f"{v:.4f}")

display = display[[
    "Nome Filial", "Total 2017", "Total 2018", "Apenas Distribuição (2018)",
    "Delta Absoluto", "Δ %", "Distrib Share", "Efficiency Score"
]]

st.dataframe(display, height=420)

# -------- Top5 / Bottom5 charts (verticais, um embaixo do outro) --------
st.markdown("---")
st.subheader("Top 5 — Mais eficientes (Total 2018)")
top5 = filtered.head(5).copy()
if not top5.empty:
    top5_chart = top5.set_index("Nome Filial")[["Total_2018"]].sort_values("Total_2018", ascending=True)
    st.bar_chart(top5_chart)
    top5_vis = top5[["Nome Filial","Total_2018","Delta_Pct","Distrib_Share","Efficiency_Score"]].copy()
    top5_vis["Total 2018"] = top5_vis["Total_2018"].map(fmt_br_money)
    top5_vis["Δ %"] = top5_vis["Delta_Pct"].map(lambda v: "" if pd.isna(v) else f"{v:.2f}%")
    top5_vis["Distrib Share"] = top5_vis["Distrib_Share"].map(lambda v: f"{v:.2%}")
    top5_vis["Efficiency Score"] = top5_vis["Efficiency_Score"].map(lambda v: f"{v:.4f}")
    st.table(top5_vis.rename(columns={"Nome Filial":"Filial"}))
else:
    st.info("Top 5 vazio — ajuste os filtros.")

st.markdown("---")
st.subheader("Top 5 — Menos eficientes (Total 2018)")
bottom5 = filtered.tail(5).copy()
if not bottom5.empty:
    bottom5_chart = bottom5.set_index("Nome Filial")[["Total_2018"]].sort_values("Total_2018", ascending=False)
    st.bar_chart(bottom5_chart)
    bottom5_vis = bottom5[["Nome Filial","Total_2018","Delta_Pct","Distrib_Share","Efficiency_Score"]].copy()
    bottom5_vis["Total 2018"] = bottom5_vis["Total_2018"].map(fmt_br_money)
    bottom5_vis["Δ %"] = bottom5_vis["Delta_Pct"].map(lambda v: "" if pd.isna(v) else f"{v:.2f}%")
    bottom5_vis["Distrib Share"] = bottom5_vis["Distrib_Share"].map(lambda v: f"{v:.2%}")
    bottom5_vis["Efficiency Score"] = bottom5_vis["Efficiency_Score"].map(lambda v: f"{v:.4f}")
    st.table(bottom5_vis.rename(columns={"Nome Filial":"Filial"}))
else:
    st.info("Bottom 5 vazio — ajuste os filtros.")

# -------- análise automática (texto) --------
st.markdown("---")
st.subheader("Análise — quem é mais eficiente e por quê")
if filtered.shape[0] == 0:
    st.info("Nenhuma filial selecionada.")
else:
    best = filtered.iloc[0]
    worst = filtered.iloc[-1]

    best_total2018 = best["Total_2018"]
    best_delta = best["Delta_Pct"]
    best_share = best["Distrib_Share"]
    best_score = best["Efficiency_Score"]

    worst_total2018 = worst["Total_2018"]
    worst_delta = worst["Delta_Pct"]
    worst_share = worst["Distrib_Share"]
    worst_score = worst["Efficiency_Score"]

    best_delta_str = "" if pd.isna(best_delta) else f"{best_delta:.2f}%"
    worst_delta_str = "" if pd.isna(worst_delta) else f"{worst_delta:.2f}%"

    st.markdown(f"**Filial mais eficiente (score mais baixo):** **{best['Nome Filial']}**")
    st.write(f"- Total 2018: **{fmt_br_money(best_total2018)}**")
    st.write(f"- Variação 2017→2018: **{best_delta_str}**")
    st.write(f"- Share Frete (Apenas Distribuição / Total 2018): **{best_share:.2%}**")
    st.write(f"- Efficiency Score: **{best_score:.4f}**")

    st.markdown(f"**Filial menos eficiente (score mais alto):** **{worst['Nome Filial']}**")
    st.write(f"- Total 2018: **{fmt_br_money(worst_total2018)}**")
    st.write(f"- Variação 2017→2018: **{worst_delta_str}**")
    st.write(f"- Share Frete (Apenas Distribuição / Total 2018): **{worst_share:.2%}**")
    st.write(f"- Efficiency Score: **{worst_score:.4f}**")

    st.markdown("### Observações gerenciais")
    st.write("- Critério usado: combinação de custo absoluto, melhoria ano-a-ano e participação do frete.")
    st.write("- Atenção: filiais com baixo volume absoluto podem aparecer eficientes — ideal normalizar por volume/entregas.")
    st.write("- Recomendação: verificar composição por grupo (RH, Frete, Manutenção) para entender origem da eficiência.")

# -------- export --------
st.markdown("---")
csv = agg.to_csv(index=False, sep=';')
st.download_button("Exportar ranking completo (CSV ; )", data=csv, file_name="ranking_eficiencia_filiais.csv", mime="text/csv")