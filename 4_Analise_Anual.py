# app_analise_filiais_gerencial_v2_nosidebar.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Análise Gerencial — 2017 x 2018 por Filial", layout="wide")
st.title("📈 Painel Gerencial — Comparativo Acumulado 2017 vs 2018")

# --- Pergunta / enunciado (solicitado)
st.markdown(
    "**Pergunta:** Realizar análise do acumulado anual e apresentar comparativo ano x ano, "
    "comentando sobre os principais impactos ( YTD 2017 x 2018 ) por linha e por filial;"
)

# ------------------ CONFIG ------------------
FILE_PATH = Path(
    r"C:\Users\emiva\OneDrive\Área de Trabalho\Streamlit Sushi Boulevard\Base de Dados - Teste de Gestão de Custos (2).xlsx"
)
SHEET_NAME = "Banco"

# ------------------ MATERIALIDADE (fixa, sem sidebar) ------------------
# Valores padrão mantidos: 5% e R$50.000
MAT_PCT = 5.0       # percentual mínimo de variação para sinalizar
MAT_ABS = 50000.0   # valor absoluto mínimo (R$) para sinalizar

# ------------------ UTIL ------------------
def find_col(df, keywords):
    def norm(s):
        return "".join(ch for ch in str(s).lower() if ch.isalnum())
    norm_map = {norm(c): c for c in df.columns}
    for k in keywords:
        nk = "".join(ch for ch in k.lower() if ch.isalnum())
        for n, orig in norm_map.items():
            if nk in n:
                return orig
    return None

def format_brl(x):
    try:
        x = float(x)
    except:
        return "-"
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def safe_pct(old, new):
    try:
        old = float(old)
        new = float(new)
    except:
        return np.nan
    if old == 0:
        return np.nan
    return (new - old) / abs(old) * 100

# ------------------ LOAD ------------------
if not FILE_PATH.exists():
    st.error(f"Arquivo não encontrado em:\n{FILE_PATH}\nVerifique o caminho e se o Streamlit tem acesso ao arquivo.")
    st.stop()

@st.cache_data
def load_data(path: Path, sheet: str):
    df = pd.read_excel(path, sheet_name=sheet, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

df_raw = load_data(FILE_PATH, SHEET_NAME)

# ------------------ DETECT COLUMNS ------------------
col_nome_filial = find_col(df_raw, ["Nome Filial", "nome filial", "filial", "nomefilial"])
col_apenas_dist = find_col(df_raw, ["Apenas_Distribuicao", "Apenas Distribuicao", "apenasdistribuicao", "apenas_distribuicao"])
col_tot2017 = find_col(df_raw, ["Total 2017", "Total2017", "total_2017", "2017"])
col_tot2018 = find_col(df_raw, ["Total 2018", "Total2018", "total_2018", "2018"])
col_ajuste = find_col(df_raw, ["Ajuste Conta", "AjusteConta", "Ajuste", "Rótulos", "Rótulos de Linha", "Rotulos"])

missing = []
for name, col in [
    ("Nome Filial", col_nome_filial),
    ("Apenas_Distribuicao", col_apenas_dist),
    ("Total 2017", col_tot2017),
    ("Total 2018", col_tot2018),
    ("Ajuste Conta", col_ajuste),
]:
    if col is None:
        missing.append(name)
if missing:
    st.error("Não foi possível localizar algumas colunas necessárias: " + ", ".join(missing))
    st.write("Colunas detectadas:", list(df_raw.columns))
    st.stop()

# ------------------ PREP DATA ------------------
df = df_raw[[col_nome_filial, col_apenas_dist, col_tot2017, col_tot2018, col_ajuste]].copy()
df.columns = ["Nome Filial", "Apenas_Distribuicao", "Total 2017", "Total 2018", "Ajuste Conta"]

def to_numeric_col(s):
    def conv(x):
        if pd.isna(x):
            return 0.0
        if isinstance(x, (int, float, np.number)):
            return float(x)
        x = str(x).strip()
        x = x.replace("R$", "").replace(" ", "")
        if x.count(",") > 0 and x.count(".") > 0:
            x = x.replace(".", "").replace(",", ".")
        else:
            if x.count(",") > 0 and x.count(".") == 0:
                x = x.replace(",", ".")
            if x.count(".") > 0 and x.count(",") == 0:
                x = x.replace(".", "")
        try:
            return float(x)
        except:
            try:
                return float(x.replace(",", "."))
            except:
                return 0.0
    return s.apply(conv)

df["Total 2017"] = to_numeric_col(df["Total 2017"])
df["Total 2018"] = to_numeric_col(df["Total 2018"])

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("Filtros")
options_status = sorted(df["Apenas_Distribuicao"].dropna().unique().astype(str))
status_choice = st.sidebar.selectbox("Filtrar por 'Apenas_Distribuicao'", options=["(Todos)"] + options_status, index=0)
filiais = sorted(df["Nome Filial"].dropna().unique().astype(str))
filiais_selected = st.sidebar.multiselect("Selecionar Filial(s)", options=filiais, default=filiais)

# apply filters
mask = df["Nome Filial"].astype(str).isin(filiais_selected)
if status_choice != "(Todos)":
    mask = mask & (df["Apenas_Distribuicao"].astype(str) == status_choice)
df_f = df[mask].copy()
if df_f.empty:
    st.warning("Não há registros após aplicar os filtros. Ajuste os filtros na barra lateral.")
    st.stop()

# ------------------ AGGREGATE BY FILIAL ------------------
agg_filial = df_f.groupby("Nome Filial", as_index=False)[["Total 2017", "Total 2018"]].sum()
agg_filial["Delta Absoluto"] = agg_filial["Total 2018"] - agg_filial["Total 2017"]
agg_filial["Delta %"] = agg_filial.apply(lambda r: safe_pct(r["Total 2017"], r["Total 2018"]), axis=1)
agg_filial = agg_filial.sort_values("Total 2018", ascending=False).reset_index(drop=True)

total_2017 = agg_filial["Total 2017"].sum()
total_2018 = agg_filial["Total 2018"].sum()
total_delta_abs = total_2018 - total_2017
total_delta_pct = safe_pct(total_2017, total_2018)

# prepare filial display (with Total Geral row)
display_filial = agg_filial.copy()
display_filial_form = display_filial[["Nome Filial", "Total 2017", "Total 2018", "Delta Absoluto", "Delta %"]].copy()
display_filial_form["Total 2017 (R$)"] = display_filial_form["Total 2017"].apply(format_brl)
display_filial_form["Total 2018 (R$)"] = display_filial_form["Total 2018"].apply(format_brl)
display_filial_form["Delta Absoluto (R$)"] = display_filial_form["Delta Absoluto"].apply(format_brl)
display_filial_form["Delta %"] = display_filial_form["Delta %"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
display_filial_form = display_filial_form[["Nome Filial", "Total 2017 (R$)", "Total 2018 (R$)", "Delta Absoluto (R$)", "Delta %"]]

total_row = {
    "Nome Filial": "Total Geral",
    "Total 2017 (R$)": format_brl(total_2017),
    "Total 2018 (R$)": format_brl(total_2018),
    "Delta Absoluto (R$)": format_brl(total_delta_abs),
    "Delta %": (f"{total_delta_pct:.1f}%" if pd.notna(total_delta_pct) else "—")
}
display_filial_with_total = pd.concat([display_filial_form, pd.DataFrame([total_row])], ignore_index=True)

# ------------------ AGGREGATE BY AJUSTE CONTA (Analise por Linha) ------------------
agg_ajuste = df_f.groupby("Ajuste Conta", as_index=False)[["Total 2017", "Total 2018"]].sum()
agg_ajuste["Delta Absoluto"] = agg_ajuste["Total 2018"] - agg_ajuste["Total 2017"]
agg_ajuste["Delta %"] = agg_ajuste.apply(lambda r: safe_pct(r["Total 2017"], r["Total 2018"]), axis=1)
agg_ajuste = agg_ajuste.sort_values("Total 2018", ascending=False).reset_index(drop=True)

# prepare display and add Total Geral row
display_ajuste = agg_ajuste.copy()
display_ajuste["Total 2017 (R$)"] = display_ajuste["Total 2017"].apply(format_brl)
display_ajuste["Total 2018 (R$)"] = display_ajuste["Total 2018"].apply(format_brl)
display_ajuste["Delta Absoluto (R$)"] = display_ajuste["Delta Absoluto"].apply(format_brl)
display_ajuste["Delta %"] = display_ajuste["Delta %"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
display_ajuste = display_ajuste.rename(columns={"Ajuste Conta": "Linha"})
display_ajuste = display_ajuste[["Linha", "Total 2017 (R$)", "Total 2018 (R$)", "Delta Absoluto (R$)", "Delta %"]]

# compute totals for ajuste table
total_aj_2017 = agg_ajuste["Total 2017"].sum()
total_aj_2018 = agg_ajuste["Total 2018"].sum()
total_aj_delta_abs = total_aj_2018 - total_aj_2017
total_aj_delta_pct = safe_pct(total_aj_2017, total_aj_2018)

total_row_ajuste = {
    "Linha": "Total Geral",
    "Total 2017 (R$)": format_brl(total_aj_2017),
    "Total 2018 (R$)": format_brl(total_aj_2018),
    "Delta Absoluto (R$)": format_brl(total_aj_delta_abs),
    "Delta %": (f"{total_aj_delta_pct:.1f}%" if pd.notna(total_aj_delta_pct) else "—")
}
display_ajuste_with_total = pd.concat([display_ajuste, pd.DataFrame([total_row_ajuste])], ignore_index=True)

# ------------------ EXECUTIVE SUMMARY & KPIs ------------------
st.header("Resumo Executivo")
col1, col2, col3 = st.columns([2,1,1])

with col1:
    trend_word = "aumento" if total_delta_abs > 0 else "redução" if total_delta_abs < 0 else "estabilidade"
    st.markdown(
        f"**Resumo:** O acumulado consolidado selecionado apresentou **{trend_word}** entre 2017 e 2018. "
        f"Total 2017 = **{format_brl(total_2017)}**; Total 2018 = **{format_brl(total_2018)}**."
    )
    st.markdown("Principais pontos e implicações operacionais e financeiras estão listados abaixo (drivers e recomendações).")

with col2:
    st.metric(label="Total 2018", value=format_brl(total_2018))

with col3:
    pct_display = f"{total_delta_pct:.1f}%" if pd.notna(total_delta_pct) else "—"
    st.metric(label="Variação YoY", value=pct_display, delta=None)

st.markdown("---")

# ------------------ TOP DRIVERS (materialidade aplicada) ------------------
st.subheader("Principais drivers (filiais) — materialidade aplicada")
flags = agg_filial.copy()
flags["flag_pct"] = flags["Delta %"].apply(lambda x: abs(x) >= MAT_PCT if pd.notna(x) else False)
flags["flag_abs"] = flags["Delta Absoluto"].apply(lambda x: abs(x) >= MAT_ABS)
flags["sinalizar"] = flags["flag_pct"] | flags["flag_abs"]

top_increases = flags[flags["sinalizar"] & (flags["Delta Absoluto"] > 0)].sort_values("Delta Absoluto", ascending=False).head(5)
top_decreases = flags[flags["sinalizar"] & (flags["Delta Absoluto"] < 0)].sort_values("Delta Absoluto", ascending=True).head(5)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("🔺 **Maiores aumentos (absolutos)** — (apenas variações acima da materialidade)")
    if top_increases.empty:
        st.write("Nenhum impacto material identificado para aumento.")
    else:
        for _, r in top_increases.iterrows():
            st.write(f"- **{r['Nome Filial']}** — 2017: {format_brl(r['Total 2017'])} → 2018: {format_brl(r['Total 2018'])} (∆ {format_brl(r['Delta Absoluto'])})")

with col_b:
    st.markdown("🔻 **Maiores reduções (absolutos)** — (apenas variações acima da materialidade)")
    if top_decreases.empty:
        st.write("Nenhuma redução material identificada.")
    else:
        for _, r in top_decreases.iterrows():
            st.write(f"- **{r['Nome Filial']}** — 2017: {format_brl(r['Total 2017'])} → 2018: {format_brl(r['Total 2018'])} (∆ {format_brl(r['Delta Absoluto'])})")

st.markdown("---")

# ------------------ RECOMMENDATIONS ------------------
st.subheader("Recomendações e Próximos Passos (sugeridos)")
rec_lines = []
if not agg_ajuste.empty:
    rec_lines.append("• Revisar maiores variações por categoria (ex.: Frete, Manutenção, RH).")
    rec_lines.append("• Priorizar investigação nas categorias com maior impacto absoluto em 2018.")
else:
    rec_lines.append("• Verificar granularidade por conta para entender drivers.")

if not top_increases.empty:
    rec_lines.append("• Para filiais com aumentos materiais: verificar contratos de frete, rotas e volumes, e possíveis lançamentos contábeis não recorrentes.")
if not top_decreases.empty:
    rec_lines.append("• Para filiais com quedas materiais: verificar redução de demanda, transferência de custos para outras unidades ou reclassificações contábeis.")

rec_lines.append("• Validar consistência de centro de custo e integração com ERP (amostras).")
rec_lines.append("• Se impacto concentrado em Frete, executar análise de causa: tarifa média, km rodado, mix de clientes.")
rec_lines.append("• Definir responsáveis para investigação (Ex.: Operações / Financeiro) e prazo 7–14 dias para report preliminar.")

for l in rec_lines:
    st.markdown(l)

st.markdown("---")

# ------------------ TABELAS E GRÁFICOS ------------------
st.subheader("Tabela agregada por Filial (Acumulado Anual)")
st.dataframe(display_filial_with_total.style.format(na_rep="-"), height=420)

st.subheader("Gráfico comparativo — 2017 vs 2018 (por Filial)")
import altair as alt
chart_df = agg_filial[["Nome Filial", "Total 2017", "Total 2018"]].melt(id_vars="Nome Filial", var_name="Ano", value_name="Valor")
chart = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X('Nome Filial:N', sort=agg_filial["Nome Filial"].tolist(), title='Filial'),
    y=alt.Y('Valor:Q', title='Valor (R$)'),
    color='Ano:N',
    tooltip=[alt.Tooltip('Nome Filial:N'), alt.Tooltip('Ano:N'), alt.Tooltip('Valor:Q', format=',.2f')]
).properties(height=420, width=1000).interactive()
st.altair_chart(chart, use_container_width=True)

st.markdown("---")
st.subheader("Análise por Linha")
st.dataframe(display_ajuste_with_total.style.format(na_rep="-"), height=320)

# ------------------ ACTIONABLE SUMMARY BY FILIAL ------------------
st.subheader("Resumo de Ações por Filial (sugestão rápida)")
for _, r in agg_filial.iterrows():
    flag_pct = (pd.notna(r["Delta %"]) and abs(r["Delta %"]) >= MAT_PCT)
    flag_abs = (abs(r["Delta Absoluto"]) >= MAT_ABS)
    if flag_pct or flag_abs:
        direction = "Aumento" if r["Delta Absoluto"] > 0 else "Redução"
        st.markdown(f"- **{r['Nome Filial']}** — {direction} material. Ação: investigar lançamentos, validar volumes/contratos. (Prioridade: ALTA)")
    else:
        st.markdown(f"- **{r['Nome Filial']}** — sem variação material. Ação: monitorar (Prioridade: BAIXA)")

# ------------------ EXPORT ------------------
st.subheader("Exportar / Baixar resultados")
export_filial = agg_filial.copy()
export_filial["Total 2017"] = export_filial["Total 2017"].round(2)
export_filial["Total 2018"] = export_filial["Total 2018"].round(2)
csv_filial = export_filial.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar CSV - Agregado por Filial", data=csv_filial, file_name="analise_filial_agregado_gerencial_v2_nosidebar.csv", mime="text/csv")

export_ajuste = agg_ajuste.copy()
export_ajuste["Total 2017"] = export_ajuste["Total 2017"].round(2)
export_ajuste["Total 2018"] = export_ajuste["Total 2018"].round(2)
csv_ajuste = export_ajuste.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar CSV - Agregado por Linha", data=csv_ajuste, file_name="analise_linha_agregado_gerencial_v2_nosidebar.csv", mime="text/csv")
