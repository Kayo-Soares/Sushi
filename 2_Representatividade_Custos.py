# app_representatividade.py
import streamlit as st
import pandas as pd
import re
from pathlib import Path

st.set_page_config(page_title="Representatividade - Custos", layout="wide")

# --------------- CONFIG ----------------
FILE_PATH = Path(
    r"C:\Users\emiva\OneDrive\Área de Trabalho\Streamlit Sushi Boulevard\Base de Dados - Teste de Gestão de Custos (2).xlsx"
)
SHEET_NAME = "Banco"

if not FILE_PATH.exists():
    st.error(f"Arquivo não encontrado em:\n{FILE_PATH}\nVerifique o caminho e se o Streamlit tem acesso ao arquivo.")
    st.stop()

# --------------- HELPERS ----------------
def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", "".join(ch for ch in str(s).lower().strip()))

def find_col(df: pd.DataFrame, keys):
    """Encontra a primeira coluna cujo nome normalizado contenha algum dos keys."""
    norm_map = {norm(c): c for c in df.columns}
    for k in keys:
        for n, orig in norm_map.items():
            if k in n:
                return orig
    return None

def read_sheet(path: Path, sheet: str) -> pd.DataFrame:
    """Lê planilha e promove header se primeira linha estiver vazia."""
    df0 = pd.read_excel(path, sheet_name=sheet, header=0, engine="openpyxl")
    if len(df0) > 0 and all((pd.isna(x) or (isinstance(x, str) and x.strip() == "")) for x in df0.iloc[0]):
        return pd.read_excel(path, sheet_name=sheet, header=1, engine="openpyxl")
    return df0

def to_num(series: pd.Series) -> pd.Series:
    """Converte séries que podem conter R$, pontos de milhar e vírgula decimal para float."""
    s = series.astype(str).fillna("").str.strip().replace(r"^\s*$", "", regex=True)
    s = s.str.replace(r"[Rr]\$\s*", "", regex=True).str.replace(r"[^\d,.\-]", "", regex=True)
    def conv(x):
        if x == "" or pd.isna(x):
            return pd.NA
        if x.count(",") > 0 and x.count(".") == 0:
            x = x.replace(".", "").replace(",", ".")
        elif x.count(".") > 1:
            x = x.replace(".", "")
        try:
            return float(x)
        except:
            return pd.NA
    return s.map(conv)

def format_brl(x) -> str:
    """Formata número para R$ 1.234.567,89 (pt-BR)."""
    try:
        x = float(x)
    except:
        return ""
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s

def is_distribution_value(v) -> bool:
    """Detecta se o campo 'Apenas_Distribuicao' indica distribuição."""
    if pd.isna(v):
        return False
    if isinstance(v, (int, float)):
        return bool(v == 1 or v is True)
    s = str(v).strip().lower()
    if s in ("1", "true", "t", "sim", "s", "yes", "y", "x"):
        return True
    if "distrib" in s:
        return True
    return False

# --------------- LAYOUT ----------------
st.title("📊 Representatividade — Distribuição vs Empresa")
st.markdown(
    "**Pergunta:** Analisar a representatividade do CUSTO TOTAL da área de Distribuição no custo TOTAL da empresa "
    "e também da CONTA DE FRETE versus o custo TOTAL da empresa e custos de frete de todas as áreas."
)
st.write("---")

st.subheader("Análise por CUSTO TOTAL da área de Distribuição no custo TOTAL da empresa)")
# --------------- LEITURA E LIMPEZA ----------------
df = read_sheet(FILE_PATH, SHEET_NAME)
if df is None or df.shape[0] == 0:
    st.error("A aba 'Banco' está vazia ou não pôde ser carregada.")
    st.stop()

# remover linhas iniciais vazias e normalizar nomes de colunas
while df.shape[0] > 0 and df.iloc[0].isna().all():
    df = df.iloc[1:].reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]

# localizar colunas relevantes
col_valores = find_col(df, ["valores", "valor", "total", "monto"])
col_apenas_dist = find_col(df, ["apenas_distribuicao", "apenas frete", "apenas_frete", "distribuicao", "apenas"])
col_conta = find_col(df, ["conta contábil", "conta_contabil", "conta", "conta_conta"])
col_ajuste = find_col(df, ["ajuste conta", "ajuste_conta", "ajuste", "ajuste_conta"])

if col_valores is None:
    st.error("Não foi possível localizar a coluna de 'Valores' na aba. Verifique o nome da coluna e tente novamente.")
    st.stop()

# converter valores
df["Valores"] = to_num(df[col_valores])

# detectar linhas que são apenas distribuição
if col_apenas_dist is not None:
    df["__is_distribution__"] = df[col_apenas_dist].apply(is_distribution_value)
else:
    df["__is_distribution__"] = False

# detectar frete pela coluna de conta se estiver disponível
if col_conta is not None:
    def extract_code(v):
        if pd.isna(v):
            return None
        m = re.match(r"^\s*(\d{1,4})\b", str(v).strip())
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        if str(v).strip().isdigit():
            return int(str(v).strip())
        return None
    df["_conta_code_"] = df[col_conta].apply(extract_code)
    df["__is_frete__"] = df["_conta_code_"].apply(lambda x: pd.notna(x) and str(x).startswith("84"))
else:
    df["__is_frete__"] = False

# --------------- CÁLCULOS GERAIS ----------------
total_empresa = float(df["Valores"].sum(skipna=True) or 0.0)
total_distribuicao = float(df.loc[df["__is_distribution__"], "Valores"].sum(skipna=True) or 0.0)
total_outras = total_empresa - total_distribuicao

# total frete (opcional)
total_frete = float(df.loc[df["__is_frete__"], "Valores"].sum(skipna=True) or 0.0)

# frete da distribuição (linhas que são frete e distribuição)
frete_em_distribuicao = float(
    df.loc[(df["__is_frete__"]) & (df["__is_distribution__"]), "Valores"].sum(skipna=True) or 0.0
)

def pct_str(val, base):
    if base == 0:
        return "0,00%"
    p = (val / base) * 100
    return f"{p:.2f}".replace(".", ",") + "%"

# --------------- TABELA PRINCIPAL ----------------
out_main = pd.DataFrame(
    {
        "Valores": [format_brl(total_distribuicao), format_brl(total_outras), format_brl(total_empresa)],
        "% Representação": [
            pct_str(total_distribuicao, total_empresa),
            pct_str(total_outras, total_empresa),
            "100,00%",
        ],
    },
    index=["Distribuição", "Outras Áreas", "Total Geral"],
)

st.table(out_main)

# --------------- ANÁLISE POR 'Ajuste Conta' ----------------
st.markdown("---")
st.subheader("Análise por Ajuste Conta (RH - Frete - Manutenção)")
if col_ajuste is None:
    st.info("Coluna de 'Ajuste Conta' não encontrada — não foi possível montar a tabela por Ajuste Conta.")
else:
    # Agrupa por valores da coluna de ajuste e soma
    rows = []
    for name, sub in df.groupby(col_ajuste):
        vals = float(sub["Valores"].sum(skipna=True) or 0.0)
        dist = float(sub.loc[sub["__is_distribution__"], "Valores"].sum(skipna=True) or 0.0)
        outras = vals - dist
        rows.append((name if pd.notna(name) else "Sem Ajuste", dist, outras, vals))

    ajuste_df = pd.DataFrame(rows, columns=[col_ajuste, "Distribuição", "Outras Areas", "Total"])

    # Ordenação preferencial se existir
    preferred_order = ["Frete", "Manutenção", "RH"]
    # mapeia lower->original
    present = {str(x).strip().lower(): x for x in ajuste_df[col_ajuste].tolist()}
    ordered = []
    for p in preferred_order:
        key = p.strip().lower()
        if key in present:
            ordered.append(present[key])
    # acrescenta o resto na ordem original
    for v in ajuste_df[col_ajuste].tolist():
        if v not in ordered:
            ordered.append(v)

    ajuste_df = ajuste_df.set_index(col_ajuste).reindex(ordered)  # reindex pode introduzir NaN para ausentes
    ajuste_df = ajuste_df.fillna(0.0)

    # formatar para exibição
    display_ajuste = pd.DataFrame(
        {
            "Distribuição": ajuste_df["Distribuição"].apply(format_brl),
            "Outras Areas": ajuste_df["Outras Areas"].apply(format_brl),
            "Total Geral": ajuste_df["Total"].apply(format_brl),
        },
        index=ajuste_df.index,
    )

    # linha Total Geral (soma)
    total_row = pd.DataFrame(
        {
            "Distribuição": [format_brl(ajuste_df["Distribuição"].sum())],
            "Outras Areas": [format_brl(ajuste_df["Outras Areas"].sum())],
            "Total Geral": [format_brl(ajuste_df["Total"].sum())],
        },
        index=["Total Geral"],
    )
    display_ajuste = pd.concat([display_ajuste, total_row])

    st.table(display_ajuste)

    # ----------------- MÉTRICAS ADICIONAIS (REQUERIDAS) -----------------
    st.markdown("---")
    st.subheader("Métricas de Frete — Distribuição")
    # 1) Representatividade do FRETE da Distribuição no CUSTO TOTAL da empresa
    pct_frete_distribuicao_no_empresa = pct_str(frete_em_distribuicao, total_empresa)
    # 2) Representatividade do FRETE da Distribuição nos FRETES de todas as áreas
    pct_frete_distribuicao_sobre_fretes = pct_str(frete_em_distribuicao, total_frete) if total_frete != 0 else "0,00%"

    # exibição em duas colunas
    col1, col2 = st.columns([8,2])
    col1.write("Representatividade do **FRETE da Distribuição** no **CUSTO TOTAL da empresa**:")
    col2.markdown(f"**{pct_frete_distribuicao_no_empresa}**")

    col1.write("Representatividade do **FRETE da Distribuição** nos **FRETES de todas as áreas**:")
    col2.markdown(f"**{pct_frete_distribuicao_sobre_fretes}**")