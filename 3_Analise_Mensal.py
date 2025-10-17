# app_representatividade_manual_final_exec.py
import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Analise Mensal — Executivo", layout="wide")
st.title("📊 Análise Mensal — Visão Executiva")
st.markdown(
    "**Pergunta:** Analisar os Grupos verificando quais possuem maior representatividade "
    " e analisar as linhas estudando a evolução mensal, apontando as tendências positivas e negativas para cada filial"
)
st.write("---")
# ---------- helpers ----------
def br_to_float(s):
    if s is None:
        return np.nan
    s = str(s).strip()
    if s in ("", "-", "—"):
        return np.nan
    s = re.sub(r"R\$\s*", "", s)
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return np.nan

def format_brl(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    try:
        v = float(x)
    except:
        return ""
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s

def trend_summary(values):
    """Recebe lista/array numérico (meses) e retorna pct change e slope (regressão linear)."""
    vals = np.array(values, dtype=float)
    mask = ~np.isnan(vals)
    if mask.sum() < 2:
        return {"pct": np.nan, "slope": 0.0}
    x = np.arange(len(vals))
    coeffs = np.polyfit(x[mask], vals[mask], 1)
    slope = float(coeffs[0])
    first = vals[mask][0]
    last = vals[mask][-1]
    pct = (last - first) / first * 100 if first != 0 else np.nan
    return {"pct": pct, "slope": slope}

def label_trend(pct, slope):
    """Retorna rótulo curto para uso executivo."""
    if np.isnan(pct):
        return "Indeterminado"
    if pct > 8 or slope > 0:
        return f"Crescimento forte ({pct:.1f}%)"
    if pct > 3 or slope > 0:
        return f"Crescimento moderado ({pct:.1f}%)"
    if pct >= -3 and pct <= 3:
        return f"Estável ({pct:.1f}%)"
    if pct < -8 or slope < 0:
        return f"Queda forte ({pct:.1f}%)"
    return f"Queda moderada ({pct:.1f}%)"

# ---------- meses ----------
months = [
    "Janeiro - 2017", "Fevereiro  - 2017", "Março - 2017", "Abril - 2017", "Maio - 2017",
    "Janeiro - 2018", "Fevereiro - 2018", "Março - 2018", "Abril - 2018", "Maio - 2018"
]

# ---------- dados (mantive exatamente os valores fornecidos) ----------
rows_main = [
    {"Grupo": "Frete", "Distribuição": "R$ 14.317.401,69", "Outras Áreas": "R$ 8.279.807,12", "Total Geral": "R$ 22.597.208,81", "% Sobre o total": "71,00%"},
    {"Grupo": "Manutenção", "Distribuição": "R$ 2.893.248,38", "Outras Áreas": "R$ 664.938,80", "Total Geral": "R$ 3.558.187,18", "% Sobre o total": "11,18%"},
    {"Grupo": "RH", "Distribuição": "R$ 2.035.753,58", "Outras Áreas": "R$ 3.636.647,39", "Total Geral": "R$ 5.672.400,97", "% Sobre o total": "17,82%"},
    {"Grupo": "Total Geral", "Distribuição": "R$ 19.246.403,65", "Outras Áreas": "R$ 12.581.393,31", "Total Geral": "R$ 31.827.796,96", "% Sobre o total": ""}
]
df_main = pd.DataFrame(rows_main)
st.subheader("Resumo por Grupo")
st.table(df_main[["Grupo", "Distribuição", "Outras Áreas", "Total Geral", "% Sobre o total"]])

st.write("")  # espaço

# ---------- TABELA 1: FRETE ----------
rows_frete = [
 {"Rótulos de Linha":"Ananindeua","Janeiro - 2017":"R$ 457.199,82","Fevereiro  - 2017":"R$ 267.015,40","Março - 2017":"R$ 327.562,57",
  "Abril - 2017":"R$ 322.974,56","Maio - 2017":"R$ 283.511,52","Janeiro - 2018":"R$ 259.605,22","Fevereiro - 2018":"R$ 300.674,09",
  "Março - 2018":"R$ 297.978,77","Abril - 2018":"R$ 271.997,26","Maio - 2018":"R$ 297.902,06","Total":"R$ 3.086.421,27"},
 {"Rótulos de Linha":"Pernambuco","Janeiro - 2017":"R$ 189.610,14","Fevereiro  - 2017":"R$ 207.022,17","Março - 2017":"R$ 216.308,26",
  "Abril - 2017":"R$ 201.952,37","Maio - 2017":"R$ 189.673,31","Janeiro - 2018":"R$ 210.895,41","Fevereiro - 2018":"R$ 202.862,30",
  "Março - 2018":"R$ 193.496,15","Abril - 2018":"R$ 178.164,65","Maio - 2018":"R$ 189.959,52","Total":"R$ 1.979.944,28"},
 {"Rótulos de Linha":"São Paulo ( Industrial )","Janeiro - 2017":"R$ 172.238,77","Fevereiro  - 2017":"R$ 146.658,05","Março - 2017":"R$ 215.116,11",
  "Abril - 2017":"R$ 225.065,03","Maio - 2017":"R$ 231.049,51","Janeiro - 2018":"R$ 95.514,75","Fevereiro - 2018":"R$ 279.747,94",
  "Março - 2018":"R$ 167.637,46","Abril - 2018":"R$ 146.849,61","Maio - 2018":"R$ 194.669,65","Total":"R$ 1.874.546,88"},
 {"Rótulos de Linha":"Parauapebas","Janeiro - 2017":"R$ 181.196,12","Fevereiro  - 2017":"R$ 200.966,86","Março - 2017":"R$ 204.190,63",
  "Abril - 2017":"R$ 185.114,15","Maio - 2017":"R$ 190.417,60","Janeiro - 2018":"R$ 184.809,50","Fevereiro - 2018":"R$ 195.686,75",
  "Março - 2018":"R$ 199.581,23","Abril - 2018":"R$ 190.527,79","Maio - 2018":"R$ 103.916,28","Total":"R$ 1.836.406,91"},
 {"Rótulos de Linha":"São Paulo ( Medicinal )","Janeiro - 2017":"R$ 186.255,93","Fevereiro  - 2017":"R$ 178.324,76","Março - 2017":"R$ 181.560,24",
  "Abril - 2017":"R$ 131.743,62","Maio - 2017":"R$ 215.541,30","Janeiro - 2018":"R$ 254.676,67","Fevereiro - 2018":"R$ 49.938,57",
  "Março - 2018":"R$ 165.226,29","Abril - 2018":"R$ 125.722,93","Maio - 2018":"R$ 194.669,65","Total":"R$ 1.683.659,96"},
 {"Rótulos de Linha":"São Luis","Janeiro - 2017":"R$ 161.895,94","Fevereiro  - 2017":"R$ 125.976,07","Março - 2017":"R$ 145.900,63",
  "Abril - 2017":"R$ 123.333,46","Maio - 2017":"R$ 150.133,84","Janeiro - 2018":"R$ 180.944,70","Fevereiro - 2018":"R$ 133.158,12",
  "Março - 2018":"R$ 140.879,66","Abril - 2018":"R$ 190.477,55","Maio - 2018":"R$ 145.983,52","Total":"R$ 1.498.683,49"},
 {"Rótulos de Linha":"Bahia","Janeiro - 2017":"R$ 32.520,84","Fevereiro  - 2017":"R$ 175.950,37","Março - 2017":"R$ 178.218,64",
  "Abril - 2017":"R$ 135.348,55","Maio - 2017":"R$ 144.039,62","Janeiro - 2018":"R$ 114.956,04","Fevereiro - 2018":"R$ 112.029,00",
  "Março - 2018":"R$ 109.386,41","Abril - 2018":"R$ 105.860,45","Maio - 2018":"R$ 131.603,21","Total":"R$ 1.239.913,13"},
 {"Rótulos de Linha":"Imperatriz","Janeiro - 2017":"R$ 82.974,46","Fevereiro  - 2017":"R$ 73.385,06","Março - 2017":"R$ 126.617,03",
  "Abril - 2017":"R$ 56.497,86","Maio - 2017":"R$ 122.626,52","Janeiro - 2018":"R$ 129.856,26","Fevereiro - 2018":"R$ 172.007,01",
  "Março - 2018":"R$ 103.534,67","Abril - 2018":"R$ 89.731,56","Maio - 2018":"R$ 160.595,34","Total":"R$ 1.117.825,77"},
 {"Rótulos de Linha":"Total Geral","Janeiro - 2017":"R$ 1.463.892,02","Fevereiro  - 2017":"R$ 1.375.298,74","Março - 2017":"R$ 1.595.474,11",
  "Abril - 2017":"R$ 1.382.029,60","Maio - 2017":"R$ 1.526.993,22","Janeiro - 2018":"R$ 1.431.258,55","Fevereiro - 2018":"R$ 1.446.103,78",
  "Março - 2018":"R$ 1.377.720,64","Abril - 2018":"R$ 1.299.331,80","Maio - 2018":"R$ 1.419.299,23","Total":"R$ 14.317.401,69"}
]
df_frete = pd.DataFrame(rows_frete)

st.subheader("Frete — Apenas Distribuição")
st.table(df_frete)

st.write("")

# ---------- TABELA 2: MANUTENÇÃO ----------
rows_manut = [
 {"Rótulos de Linha":"Imperatriz","Janeiro - 2017":"R$ 64.580,57","Fevereiro  - 2017":"R$ 109.574,63","Março - 2017":"R$ 207.296,76",
  "Abril - 2017":"R$ 109.204,52","Maio - 2017":"R$ 71.708,18","Janeiro - 2018":"R$ 109.349,69","Fevereiro - 2018":"R$ 116.884,46",
  "Março - 2018":"R$ 100.183,31","Abril - 2018":"R$ 172.386,05","Maio - 2018":"R$ 103.773,82","Total":"R$ 1.164.941,99"},
 {"Rótulos de Linha":"Pernambuco","Janeiro - 2017":"R$ 38.506,63","Fevereiro  - 2017":"R$ 45.903,71","Março - 2017":"R$ 54.441,98",
  "Abril - 2017":"R$ 53.930,59","Maio - 2017":"R$ 41.193,66","Janeiro - 2018":"R$ 67.588,21","Fevereiro - 2018":"R$ 67.116,47",
  "Março - 2018":"R$ 74.705,21","Abril - 2018":"R$ 68.961,46","Maio - 2018":"R$ 103.062,75","Total":"R$ 615.410,67"},
 {"Rótulos de Linha":"Parauapebas","Janeiro - 2017":"R$ 32.682,43","Fevereiro  - 2017":"R$ 45.574,13","Março - 2017":"R$ 45.505,31",
  "Abril - 2017":"R$ 39.326,83","Maio - 2017":"R$ 14.436,04","Janeiro - 2018":"R$ 50.473,02","Fevereiro - 2018":"R$ 60.000,09",
  "Março - 2018":"R$ 58.950,10","Abril - 2018":"R$ 38.171,57","Maio - 2018":"R$ 59.991,95","Total":"R$ 445.111,47"},
 {"Rótulos de Linha":"São Paulo ( Industrial )","Janeiro - 2017":"R$ 28.188,66","Fevereiro  - 2017":"R$ 30.322,10","Março - 2017":"R$ 26.742,73",
  "Abril - 2017":"R$ 26.458,91","Maio - 2017":"R$ 29.974,08","Janeiro - 2018":"R$ 24.601,55","Fevereiro - 2018":"R$ 9.807,27",
  "Março - 2018":"R$ 38.874,59","Abril - 2018":"R$ 51.655,32","Maio - 2018":"R$ 31.517,36","Total":"R$ 298.142,57"},
 {"Rótulos de Linha":"Bahia","Janeiro - 2017":"R$ 9.783,25","Fevereiro  - 2017":"R$ 7.969,78","Março - 2017":"R$ 10.622,72",
  "Abril - 2017":"R$ 9.841,29","Maio - 2017":"R$ 11.584,52","Janeiro - 2018":"R$ 18.572,23","Fevereiro - 2018":"R$ 21.738,50",
  "Março - 2018":"R$ 13.395,46","Abril - 2018":"R$ 20.774,75","Maio - 2018":"R$ 17.821,73","Total":"R$ 142.104,23"},
 {"Rótulos de Linha":"São Paulo ( Medicinal )","Janeiro - 2017":"R$ 15.125,43","Fevereiro  - 2017":"R$ 15.614,11","Março - 2017":"R$ 11.412,85",
  "Abril - 2017":"R$ 13.259,78","Maio - 2017":"R$ 12.697,30","Janeiro - 2018":"R$ 11.604,28","Fevereiro - 2018":"R$ 5.344,52",
  "Março - 2018":"R$ 12.066,43","Abril - 2018":"R$ 18.841,23","Maio - 2018":"R$ 7.619,49","Total":"R$ 123.585,42"},
 {"Rótulos de Linha":"Ananindeua","Janeiro - 2017":"R$ 12.928,52","Fevereiro  - 2017":"R$ 6.980,70","Março - 2017":"R$ 9.276,01",
  "Abril - 2017":"R$ 6.991,32","Maio - 2017":"R$ 7.676,17","Janeiro - 2018":"R$ 7.897,42","Fevereiro - 2018":"R$ 8.547,33",
  "Março - 2018":"R$ 8.149,32","Abril - 2018":"R$ 8.379,23","Maio - 2018":"R$ 6.892,11","Total":"R$ 83.718,13"},
 {"Rótulos de Linha":"São Luis","Janeiro - 2017":"-","Fevereiro  - 2017":"-","Março - 2017":"R$ 4.706,57",
  "Abril - 2017":"-","Maio - 2017":"R$ 1.250,39","Janeiro - 2018":"R$ 845,43","Fevereiro - 2018":"R$ 2.165,14",
  "Março - 2018":"R$ 5.530,26","Abril - 2018":"R$ 2.910,39","Maio - 2018":"R$ 2.825,72","Total":"R$ 20.233,90"},
 {"Rótulos de Linha":"Total Geral","Janeiro - 2017":"R$ 201.795,49","Fevereiro  - 2017":"R$ 261.939,16","Março - 2017":"R$ 370.004,93",
  "Abril - 2017":"R$ 259.013,24","Maio - 2017":"R$ 190.520,34","Janeiro - 2018":"R$ 290.931,83","Fevereiro - 2018":"R$ 291.603,78",
  "Março - 2018":"R$ 311.854,68","Abril - 2018":"R$ 382.080,00","Maio - 2018":"R$ 333.504,93","Total":"R$ 2.893.248,38"},
]
df_manut = pd.DataFrame(rows_manut)

st.subheader("Manutenção — Apenas Distribuição")
st.table(df_manut)

st.write("")

# ---------- TABELA 3: RH ----------
rows_rh = [
 {"Rótulos de Linha":"São Paulo ( Industrial )","Janeiro - 2017":"R$ 62.356,61","Fevereiro  - 2017":"R$ 70.596,33","Março - 2017":"R$ 69.878,15",
  "Abril - 2017":"R$ 73.640,91","Maio - 2017":"R$ 73.095,88","Janeiro - 2018":"R$ 55.657,24","Fevereiro - 2018":"R$ 80.091,68",
  "Março - 2018":"R$ 67.470,17","Abril - 2018":"R$ 78.793,75","Maio - 2018":"R$ 84.629,56","Total":"R$ 716.210,28"},
 {"Rótulos de Linha":"Parauapebas","Janeiro - 2017":"R$ 35.871,32","Fevereiro  - 2017":"R$ 49.553,58","Março - 2017":"R$ 42.526,45",
  "Abril - 2017":"R$ 50.308,61","Maio - 2017":"R$ 47.059,25","Janeiro - 2018":"R$ 46.126,65","Fevereiro - 2018":"R$ 49.003,73",
  "Março - 2018":"R$ 46.909,33","Abril - 2018":"R$ 48.506,14","Maio - 2018":"R$ 45.772,32","Total":"R$ 461.637,38"},
 {"Rótulos de Linha":"Ananindeua","Janeiro - 2017":"R$ 37.799,60","Fevereiro  - 2017":"R$ 35.491,84","Março - 2017":"R$ 33.648,37",
  "Abril - 2017":"R$ 26.597,78","Maio - 2017":"R$ 30.812,45","Janeiro - 2018":"R$ 33.595,24","Fevereiro - 2018":"R$ 34.094,77",
  "Março - 2018":"R$ 32.260,54","Abril - 2018":"R$ 38.137,28","Maio - 2018":"R$ 29.997,92","Total":"R$ 332.435,79"},
 {"Rótulos de Linha":"São Luis","Janeiro - 2017":"R$ 12.711,00","Fevereiro  - 2017":"R$ 12.404,71","Março - 2017":"R$ 12.346,50",
  "Abril - 2017":"R$ 14.105,40","Maio - 2017":"R$ 15.550,89","Janeiro - 2018":"R$ 17.937,40","Fevereiro - 2018":"R$ 20.663,19",
  "Março - 2018":"R$ 19.399,14","Abril - 2018":"R$ 20.559,95","Maio - 2018":"R$ 20.686,85","Total":"R$ 166.365,03"},
 {"Rótulos de Linha":"Bahia","Janeiro - 2017":"R$ 12.096,54","Fevereiro  - 2017":"R$ 9.292,21","Março - 2017":"R$ 12.927,86",
  "Abril - 2017":"R$ 12.899,76","Maio - 2017":"R$ 14.397,46","Janeiro - 2018":"R$ 10.829,59","Fevereiro - 2018":"R$ 11.388,17",
  "Março - 2018":"R$ 12.286,49","Abril - 2018":"R$ 8.830,13","Maio - 2018":"R$ 16.875,79","Total":"R$ 121.824,00"},
 {"Rótulos de Linha":"Imperatriz","Janeiro - 2017":"R$ 6.869,77","Fevereiro  - 2017":"R$ 9.460,65","Março - 2017":"R$ 10.405,68",
  "Abril - 2017":"R$ 10.405,69","Maio - 2017":"R$ 10.405,64","Janeiro - 2018":"R$ 8.739,09","Fevereiro - 2018":"R$ 11.226,05",
  "Março - 2018":"R$ 10.914,74","Abril - 2018":"R$ 11.362,33","Maio - 2018":"R$ 11.059,82","Total":"R$ 100.849,46"},
 {"Rótulos de Linha":"São Paulo ( Medicinal )","Janeiro - 2017":"R$ 10.212,16","Fevereiro  - 2017":"R$ 10.212,16","Março - 2017":"R$ 10.206,56",
  "Abril - 2017":"R$ 10.212,15","Maio - 2017":"R$ 3.176,33","Janeiro - 2018":"R$ 10.386,20","Fevereiro - 2018":"R$ 10.386,23",
  "Março - 2018":"R$ 11.016,62","Abril - 2018":"R$ 3.267,16","Maio - 2018":"R$ 10.340,69","Total":"R$ 89.416,26"},
 {"Rótulos de Linha":"Pernambuco","Janeiro - 2017":"R$ 4.681,88","Fevereiro  - 2017":"R$ 4.487,21","Março - 2017":"R$ 4.692,01",
  "Abril - 2017":"R$ 4.487,21","Maio - 2017":"R$ 4.487,21","Janeiro - 2018":"R$ 5.621,57","Fevereiro - 2018":"R$ 5.690,61",
  "Março - 2018":"R$ 5.425,91","Abril - 2018":"R$ 1.572,88","Maio - 2018":"R$ 5.868,89","Total":"R$ 47.015,38"},
 {"Rótulos de Linha":"Total Geral","Janeiro - 2017":"R$ 182.598,88","Fevereiro  - 2017":"R$ 201.498,69","Março - 2017":"R$ 196.631,58",
  "Abril - 2017":"R$ 202.657,51","Maio - 2017":"R$ 198.985,11","Janeiro - 2018":"R$ 188.892,98","Fevereiro - 2018":"R$ 222.544,43",
  "Março - 2018":"R$ 205.682,94","Abril - 2018":"R$ 211.029,62","Maio - 2018":"R$ 225.231,84","Total":"R$ 2.035.753,58"},
]
df_rh = pd.DataFrame(rows_rh)

st.subheader("RH — Apenas Distribuição")
st.table(df_rh)

st.write("")

# ---------- ANÁLISE EXECUTIVA ----------
st.subheader("Análise executiva — destaques e recomendações")

def analyze_table_exec(df, table_name):
    metrics = []
    for _, row in df.iterrows():
        label = row["Rótulos de Linha"]
        vals = [br_to_float(row.get(m, "")) for m in months]
        tr = trend_summary(vals)
        pct = tr["pct"]
        slope = tr["slope"]
        lbl = label_trend(pct, slope)
        metrics.append({"label": label, "pct": pct, "slope": slope, "label_short": lbl})
    mdf = pd.DataFrame(metrics).set_index("label")
    # identificar top positivos/negativos (ignorando NaN)
    valid = mdf.dropna(subset=["pct"])
    top_pos = valid.sort_values("pct", ascending=False).head(2)
    top_neg = valid.sort_values("pct").head(2)
    # construir resumo executivo curto
    parts = []
    if not top_pos.empty:
        parts.append("Maior crescimento: " + ", ".join([f"{i} ({row['pct']:.1f}%)" for i,row in top_pos.iterrows()]))
    if not top_neg.empty:
        parts.append("Maior queda: " + ", ".join([f"{i} ({row['pct']:.1f}%)" for i,row in top_neg.iterrows()]))
    if parts:
        summary = f"{table_name}: " + " • ".join(parts) + "."
    else:
        summary = f"{table_name}: sem tendência clara."
    # recomendações rápidas
    recs = []
    if not top_pos.empty:
        recs.append(f"Investigar fatores que sustentam o crescimento em {', '.join(top_pos.index.tolist())}; avaliar oportunidades de replicar práticas.")
    if not top_neg.empty:
        recs.append(f"Aprofundar causas da redução em {', '.join(top_neg.index.tolist())}; priorizar ações corretivas de curto prazo.")
    if not recs:
        recs = ["Manter monitoramento mensal."]
    # insights por filial (linha curta)
    bullets = []
    for label, row in mdf.iterrows():
        pct = row["pct"]
        short = row["label_short"]
        if np.isnan(pct):
            bullets.append(f"- {label}: dados insuficientes.")
        else:
            bullets.append(f"- {label}: {short}.")
    return summary, recs, bullets

# gerar para cada tabela
sum_frete, recs_frete, bullets_frete = analyze_table_exec(df_frete, "Frete")
sum_manut, recs_manut, bullets_manut = analyze_table_exec(df_manut, "Manutenção")
sum_rh, recs_rh, bullets_rh = analyze_table_exec(df_rh, "RH")

# exibir executive summaries
st.markdown(f"**Resumo — Frete:** {sum_frete}")
for r in recs_frete:
    st.markdown(f"- {r}")

st.markdown("")
st.markdown("**Insights por filial — Frete**")
for b in bullets_frete:
    st.markdown(b)

st.markdown("---")
st.markdown(f"**Resumo — Manutenção:** {sum_manut}")
for r in recs_manut:
    st.markdown(f"- {r}")

st.markdown("")
st.markdown("**Insights por filial — Manutenção**")
for b in bullets_manut:
    st.markdown(b)

st.markdown("---")
st.markdown(f"**Resumo — RH:** {sum_rh}")
for r in recs_rh:
    st.markdown(f"- {r}")

st.markdown("")
st.markdown("**Insights por filial — RH**")
for b in bullets_rh:
    st.markdown(b)
