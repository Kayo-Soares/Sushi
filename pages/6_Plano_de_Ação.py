# app_frete_texto.py
# Run: streamlit run app_frete_texto.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re

st.set_page_config(page_title="Plano de Ação", layout="wide")
st.title("Plano de ação -  Análise de Linha -  Frete")
st.markdown(
    "**Pergunta:** Concluir o estudo apontando os 3 principais problemas de custos identificados sendo geral, por filial ou por grupo - fica a critério do candidato e elaborar um plano de ação propondo melhorias para redução ou equalização dos custos")


# ------------------------
# Dados (colados do texto do usuário)
# ------------------------
rows = [
    ("Frete", "7.343.687,69", "6.973.714,00", "14.317.401,69"),
    ("Para Vendas Distribuicao Gasosa", "2.155.862,72", "2.225.763,77", "4.381.626,49"),
    ("Frete Variavel Vendas", "1.435.886,00", "1.306.075,71", "2.741.961,71"),
    ("Para Vendas", "1.226.171,81", "1.162.315,63", "2.388.487,44"),
    ("Para Transferencias", "657.720,34", "521.010,71", "1.178.731,05"),
    ("Fretes Extraordinários Distribui", "334.957,18", "405.966,74", "740.923,92"),
    ("Para Transferencias Distribuição", "242.112,44", "226.897,33", "469.009,77"),
    ("Outros Transportes", "270.230,19", "188.766,39", "458.996,58"),
    ("Para Vendas Distribuição Gasosa", "246.657,49", "190.432,80", "437.090,29"),
    ("Para Vendas DG Contagem", "197.006,80", "160.524,58", "357.531,38"),
    ("Transportes Offshore", "177.687,32", "2.268,75", "179.956,07"),
    ("Transportes Offshore - Belford Roxo", "300,00", "150.364,20", "150.664,20"),
    ("Frete Extra", "33.803,16", "98.026,32", "131.829,48"),
    ("Pedagio s/frete DG Camp", "60.489,34", "54.517,80", "115.007,14"),
    ("Para Transferencias MEDICINAL-SA", "65.888,94", "40.436,20", "106.325,14"),
    ("Fretes Extraordinários Distrib.", "36.540,84", "48.211,03", "84.751,87"),
    ("Pedagio s/ Frete Transferencia", "32.799,18", "29.559,36", "62.358,54"),
    ("Pedagio s/frete DG Sert", "32.250,53", "27.713,22", "59.963,75"),
    ("Pedagio s/frete DG PW", "26.468,51", "30.112,54", "56.581,05"),
    ("Pedagio s/frete DG BRoxo", "30.176,93", "19.998,14", "50.175,07"),
    ("Fretes Extraordinários", "11.290,66", "17.768,67", "29.059,33"),
    ("Fretes Extraordinários DG Sert", "14.823,12", "10.822,66", "25.645,78"),
    ("Pedagio s/frete", "15.957,17", "6.490,53", "22.447,70"),
    ("Fretes Extraordinários DG Contag", "1.388,53", "20.050,39", "21.438,92"),
    ("Pedagio s/frete DG PW M", "11.272,64", "9.230,08", "20.502,72"),
    ("Fretes Extraordinários DG Camp", "3.883,68", "12.391,62", "16.275,30"),
    ("Outros Transportes DG Contagem", "7.689,62", "4.671,34", "12.360,96"),
    ("Outros Transportes DG Sert", "7.733,41", "1.364,63", "9.098,04"),
    ("Pedagio s/frete DG Contagem", "4.807,86", "1.962,86", "6.770,72"),
    ("Pedagio s/frete DISTRIBUICAO GAS", "1.831,28", "-", "1.831,28"),
]

# ------------------------
# Util: parse BRL text -> float
# ------------------------
def parse_brl(s):
    if s is None:
        return np.nan
    s = str(s).strip()
    if s == "-" or s == "":
        return np.nan
    # handle parentheses negatives
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    # remove any non-digit, non-comma, non-dot, non-minus
    s = re.sub(r"[^\d\.,\-]", "", s)
    if s.count("-") > 0:
        s = s.replace("-", "")
        neg = True
    s = s.replace(".", "").replace(",", ".")
    try:
        v = float(s)
    except:
        v = np.nan
    return -v if neg and not np.isnan(v) else v

def brl_fmt(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "-"
    s = f"{v:,.2f}"
    # make BRL style: thousand point, decimal comma
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s

# ------------------------
# Build DataFrame
# ------------------------
df = pd.DataFrame(rows, columns=["Linha", "Total 2017 (txt)", "Total 2018 (txt)", "Total Geral (txt)"])
df["Total 2017"] = df["Total 2017 (txt)"].apply(parse_brl).fillna(0.0)
df["Total 2018"] = df["Total 2018 (txt)"].apply(parse_brl).fillna(0.0)
# if Total Geral provided, use it; else sum 2017+2018
df["Total Geral"] = df["Total Geral (txt)"].apply(lambda x: parse_brl(x) if x and x != "-" else np.nan)
df["Total Geral"] = df["Total Geral"].fillna(df["Total 2017"] + df["Total 2018"])

# Remove any explicit "Frete" summary row from detailed list for Top N if needed.
# Keep it only as a KPI if present.
summary_row_mask = df["Linha"].str.strip().str.lower() == "frete"
# compute aggregated totals (trusting provided totals)
total_frete = df.loc[summary_row_mask, "Total Geral"].sum()
if total_frete == 0:
    total_frete = df["Total Geral"].sum()

# ------------------------
# KPIs
# ------------------------
st.header("✅ KPIs principais (Frete)")
col1, col2, col3 = st.columns(3)
total_empresa = total_frete  # focused only on frete
col1.metric("Total Frete (2017+2018)", brl_fmt(total_frete))

# Force the "maior item" to be "Para Vendas Distribuicao Gasosa" as requested,
# and show the requested ratio 74,39% do total da distribuição.
major_item_name = "Para Vendas Distribuicao Gasosa"
# try to find its value in the table; fallback to top3 first item
if major_item_name in df["Linha"].values:
    major_value = df.loc[df["Linha"] == major_item_name, "Total Geral"].sum()
else:
    # fallback: largest item excluding summary
    major_value = df.loc[~summary_row_mask, "Total Geral"].max()

col2.metric("Maior item", major_item_name, brl_fmt(major_value))
# show the exact percentual informado por você (fixo)
col3.metric("% do frete vs total da distribuição", "74,39%")

st.markdown("---")

# ------------------------
# Top-3 detalhado and evolution (still computed from data)
# ------------------------
st.subheader("🏆 Top 3 itens (por Total Geral)")
top3 = df.loc[~summary_row_mask].sort_values("Total Geral", ascending=False).head(3).copy()
top3_display = top3[["Linha", "Total 2017", "Total 2018", "Total Geral"]].copy()
top3_display["Total 2017 (R$)"] = top3_display["Total 2017"].apply(brl_fmt)
top3_display["Total 2018 (R$)"] = top3_display["Total 2018"].apply(brl_fmt)
top3_display["Total Geral (R$)"] = top3_display["Total Geral"].apply(brl_fmt)
st.table(top3_display[["Linha", "Total 2017 (R$)", "Total 2018 (R$)", "Total Geral (R$)"]].reset_index(drop=True))

# show evolution numbers
evo = top3[["Linha", "Total 2017", "Total 2018"]].copy()
evo["Delta (R$)"] = evo["Total 2018"] - evo["Total 2017"]
evo["Delta (%)"] = evo["Delta (R$)"] / evo["Total 2017"].replace(0, np.nan) * 100
evo["Delta (R$)"] = evo["Delta (R$)"].apply(brl_fmt)
evo["Delta (%)"] = evo["Delta (%)"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
st.markdown("**Evolução 2017 → 2018 (Top 3)**")
st.table(evo[["Linha", "Delta (R$)", "Delta (%)"]].reset_index(drop=True))

st.markdown("---")

# ------------------------
# Gráficos: participação e comparativo 2017/2018
# ------------------------
st.subheader("📊 Participação por item (Top 10)")

# Substituição: usar gráfico de BARRAS ao invés de pizza
top10 = df.loc[~summary_row_mask].sort_values("Total Geral", ascending=False).head(10).copy()
fig_part = px.bar(
    top10,
    x="Linha",
    y="Total Geral",
    title="Top 10 - Participação no Total Frete (Top 10)",
    labels={"Total Geral": "Total Geral (R$)", "Linha": "Item"},
    text=top10["Total Geral"].apply(lambda v: brl_fmt(v))
)
fig_part.update_traces(textposition="outside")
fig_part.update_layout(xaxis_tickangle=-45, uniformtext_minsize=8, uniformtext_mode='hide', margin=dict(t=50, b=150))

st.plotly_chart(fig_part, use_container_width=True)

st.subheader("📈 Comparativo 2017 x 2018 (Top 6)")
top6 = df.loc[~summary_row_mask].sort_values("Total Geral", ascending=False).head(6).copy()
melt = top6.melt(id_vars=["Linha"], value_vars=["Total 2017", "Total 2018"], var_name="Ano", value_name="Valor")
fig_bar = px.bar(melt, x="Linha", y="Valor", color="Ano", barmode="group", title="Comparativo 2017 vs 2018 (principais itens)")
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ------------------------
# Insights rápidos (automático)
# ------------------------
st.subheader("💡 Insights rápidos")
insights = [
    f"- Total Frete: **{brl_fmt(total_frete)}**. Altíssima concentração: os 3 maiores itens somam **{brl_fmt(top3['Total Geral'].sum())}** (≈{(top3['Total Geral'].sum()/total_frete*100):.1f}% do total).",
    "- Observação: existem linhas de *fretes extraordinários*, *transferências* e *pedágios* que podem ser tratadas separadamente (auditoria e políticas).",
    "- Entre 2017 e 2018 houve redução em *Frete Variável Vendas* e em *Para Vendas*, mas aumento em *Para Vendas Distribuicao Gasosa* (maior item)."
]
for s in insights:
    st.write(s)

st.markdown("---")

# ------------------------
# Plano de ação (resumido)
# ------------------------
st.subheader("🛠️ Plano de Ação (priorizado e objetivo)")

st.markdown("**Curto prazo (1–3 meses)**")
st.write("""
- Auditoria de faturas: verificar cobranças extras, pedágios e duplicidades nas faturas dos 3 maiores fluxos.  
- Negociação tática com carriers nos 3 maiores itens (volume/percentual).  
- Bloquear fretes extraordinários sem autorização e montar registro de causa.
""")

st.markdown("**Médio prazo (3–9 meses)**")
st.write("""
- Piloto de consolidação de cargas e otimização de rotas (reduzir km vazios).  
- Revisar política de transferências internas (cross-docking onde possível).  
- Segmentar contratos por tipo de rota/modal.
""")

st.markdown("**Longo prazo (9–18 meses)**")
st.write("""
- Implementar/expandir um TMS simples + painel de KPIs integrados.  
- Estudar modal-shift para trechos longos e programa de gestão de carriers (KPIs de performance).
""")

st.markdown("---")

# ------------------------
# KPIs sugeridos and download
# ------------------------
st.subheader("📈 KPIs sugeridos para monitorar")
st.write("""
- Custo de frete / pedido (R$)  
- % km vazios (empty runs)  
- Fill rate (ocupação média dos veículos)  
- Nº de fretes extraordinários por mês  
- Custo de pedágio / total frete (%)
""")

# Export CSV - filtered table (Top items)
st.markdown("---")
st.subheader("⤓ Exportar resultados (Top itens)")
csv = top10[["Linha", "Total 2017", "Total 2018", "Total Geral"]].to_csv(index=False, sep=";", encoding="utf-8-sig")
st.download_button("📥 Baixar Top 10 (CSV)", data=csv, file_name="top10_frete.csv", mime="text/csv")