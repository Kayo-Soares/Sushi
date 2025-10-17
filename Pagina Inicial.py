import streamlit as st

# -------------------------------------------------------------
# CONFIGURAÇÃO INICIAL DO APP
# -------------------------------------------------------------
st.set_page_config(
    page_title="Estudo de Custos – Área de Distribuição",
    page_icon="📊",
    layout="wide",
)

# -------------------------------------------------------------
# CABEÇALHO
# -------------------------------------------------------------
st.title("📊 Estudo de Custos – Área de Distribuição")
st.markdown("### 📅 Período analisado: **2017 x 2018 (jan–mai)**")
st.markdown("---")

# -------------------------------------------------------------
# SEÇÃO: APRESENTAÇÃO DO CASE
# -------------------------------------------------------------
st.header("🎯 Objetivo do Estudo")

st.markdown("""
O presente estudo tem como objetivo **analisar a estrutura de custos da Área de Distribuição**,
identificando padrões, tendências e oportunidades de melhoria no desempenho financeiro
das filiais.

A partir da **base consolidada de custos** da empresa, foram realizadas diversas análises envolvendo:

- 📦 **Custos Totais por Filial**  
- 🚚 **Custos de Frete (Grupo 84)**  
- 👷 **Custos de RH e Manutenção (Grupos 81 e 83)**  
- 📈 **Evolução mensal e comparativos anuais (YTD 2017 x 2018)**  
- 🏆 **Ranking de eficiência das filiais**  
- 🧠 **Identificação dos principais problemas de custos e plano de ação**
""")

st.markdown("---")

# -------------------------------------------------------------
# SEÇÃO: METODOLOGIA
# -------------------------------------------------------------
st.header("🧩 Metodologia de Análise")

st.markdown("""
As análises foram realizadas a partir da **aba principal “Banco” da planilha de gestão de custos**, 
que consolida todas as informações por **Centro de Custo**, **Filial**, **Conta Contábil** e **Grupo**.

1️⃣ **Filtragem de Centros de Custo**  
   Foram consideradas as unidades de **Distribuição** (CC 29, 31, 33 e 35), conforme escopo do estudo.

2️⃣ **Cálculo do Custo Total e Custo de Frete**  
   O Custo Total representa a soma de todos os grupos de contas.  
   O Custo de Frete considera apenas as contas do grupo **84**.

3️⃣ **Consolidação da Unidade de São Paulo**  
   As filiais **28 (Industrial)** e **80 (Medicinal)** foram somadas, 
   resultando em **São Paulo (Consolidado)** para fins comparativos.

4️⃣ **Comparativos e Indicadores**  
   Foram gerados rankings, representatividades e variações anuais (YTD 2017 x 2018),
   identificando as filiais mais e menos eficientes.

5️⃣ **Síntese Executiva e Plano de Ação**  
   Ao final, foram destacados os **principais problemas de custos** e
   proposto um **plano de ação** para equalização e redução dos gastos.
""")

st.markdown("---")

# -------------------------------------------------------------
# SEÇÃO: RESULTADOS GERAIS
# -------------------------------------------------------------
st.header("📋 Estrutura do Dashboard")

st.markdown("""
O dashboard interativo desenvolvido em **Python + Streamlit** está dividido em seções,
correspondentes a cada uma das perguntas do estudo:

1️⃣ **Ranking de Custos por Filial**  
2️⃣ **Representatividade da Área de Distribuição**  
3️⃣ **Evolução e Tendências Mensais**  
4️⃣ **Comparativo YTD 2017 x 2018**  
5️⃣ **Eficiência das Filiais**  
6️⃣ **Conclusão e Plano de Ação**

Cada seção utiliza dados da mesma base principal e traz insights gerenciais
para apoiar decisões estratégicas da área de Distribuição.
""")

st.info("""
💡 Dica: use a barra lateral do app para navegar entre as seções do estudo.
""")

# -------------------------------------------------------------
# RODAPÉ
# -------------------------------------------------------------
st.markdown("---")
st.caption("Desenvolvido em Python + Streamlit | Kayo Soares")