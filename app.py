import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard CONOSCE", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("CONOSCE/resultado_all.csv")

    # Asegurar tipo fecha
    for col in ['fecha_convocatoria', 'fecha_buenapro', 'fecha_consentimiento_bp']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    return df

df = cargar_datos()

# -------- TITULO -------- #
col1, col2 = st.columns([3, 2])  # proporción 3:2 para que el título tenga más espacio

with col1:
    st.markdown(
    "## 📊 Dashboard Adjudicaciones",
    unsafe_allow_html=True
)

with col2:
    grafico = st.selectbox(
        "Métrica a visualizar",
        ["Convocatoria → Buena Pro", "Buena Pro → Consentimiento"]
    )


# -------- FILTROS LATERALES -------- #
with st.sidebar:
    # st.markdown("### Filtro de monto adjudicado")
    st.markdown("### 🎯 Filtros: ")

    # Filtro por monto adjudicado
    df["monto_adjudicado_item"] = pd.to_numeric(df["monto_adjudicado_item"], errors="coerce")
    rangos_millones = list(range(5_000_000, 22_000_000, 1_000_000))
    rango_seleccionado = st.select_slider(
        "Monto mínimo adjudicado",
        options=rangos_millones,
        format_func=lambda x: f"S/ {x:,.0f}"
    )

    # Filtro por objeto contractual
    
    opciones_objeto = ["All", "Obra", "Bien", "Servicio", "Consultoría de Obra"]
    seleccion_objeto = st.selectbox("Objeto Contractual", opciones_objeto)

    # Filtro por año
    try:
        years_disponibles = sorted(
            [int(y) for y in df["year"].dropna().unique()],
            reverse=True
        )
    except Exception:
        years_disponibles = []

    if years_disponibles:
        seleccion_year = st.multiselect(
            "Selecciona año(s):",
            options=years_disponibles,
            default=years_disponibles,
            help="Filtra los registros por año de adjudicación"
        )
    else:
        seleccion_year = []
        st.info("⚠️ No se encontraron años válidos.")



    st.markdown("### Otros filtros")

    # Filtro por tipo de proceso de selección
    st.markdown("### 🧾 Tipo de Proceso de Selección")
    tipos_proceso = df["tipoprocesoseleccion"].dropna().unique()
    seleccion_tipo_proceso = st.multiselect(
        "Tipo de proceso de selección",
        options=sorted(tipos_proceso),
        default=sorted(tipos_proceso)
    )


    with st.expander("📅 Rango de fechas y días", expanded=True):
        fechas = pd.to_datetime(df['fecha_convocatoria'], errors='coerce')
        fecha_min = fechas.min().date()
        fecha_max = fechas.max().date()
        rango_fecha = st.date_input("Rango de fechas de convocatoria", [fecha_min, fecha_max])

        dias_max = int(df["f_convo_buenapro"].max())
        dias_convo_buena = st.slider(
            "Días máx. entre convocatoria y buena pro",
            min_value=0,
            max_value=dias_max,
            value=dias_max  # ← inicia en el máximo
        )

        dias_max2 = int(df["f_buenapro_consentimiento"].max())
        dias_buena_consent = st.slider(
            "Días máx. entre buena pro y consentimiento",
            min_value=0,
            max_value=dias_max2,
            value=dias_max2  # ← inicia en el máximo
        )
    

# -------- FILTRADO -------- #
f1 = (df['fecha_convocatoria'].dt.date >= rango_fecha[0]) & (df['fecha_convocatoria'].dt.date <= rango_fecha[1])
f2 = df['f_convo_buenapro'] <= dias_convo_buena
f3 = df['f_buenapro_consentimiento'] <= dias_buena_consent
f4 = df["monto_adjudicado_item"] >= rango_seleccionado
f5 = df["objetocontractual"] == seleccion_objeto if seleccion_objeto != "All" else pd.Series([True] * len(df))
f6 = df["year"].isin(seleccion_year)
f7 = df["tipoprocesoseleccion"].isin(seleccion_tipo_proceso)


df_filtrado = df[f1 & f2 & f3 & f4 & f5 & f6 & f7 ]



col1, col2, col3 = st.columns(3)

with col1:
    valor = len(df_filtrado)
    st.markdown(f"<span style='font-size: 14px;'>**Procesos filtrados:** {valor:,}</span>", unsafe_allow_html=True)

with col2:
    promedio_1 = round(df_filtrado["f_convo_buenapro"].mean(), 1)
    st.markdown(f"<span style='font-size: 14px;'>**Días promedio: Convocatoria → Buena Pro:** {promedio_1}</span>", unsafe_allow_html=True)

with col3:
    promedio_2 = round(df_filtrado["f_buenapro_consentimiento"].mean(), 1)
    st.markdown(f"<span style='font-size: 14px;'>**Días promedio: Buena Pro → Consentimiento:** {promedio_2}</span>", unsafe_allow_html=True)

# -------- GRÁFICO PRINCIPAL -------- #

if grafico == "Convocatoria → Buena Pro":
    st.bar_chart(df_filtrado["f_convo_buenapro"].value_counts().sort_index())
else:
    st.bar_chart(df_filtrado["f_buenapro_consentimiento"].value_counts().sort_index())



# -------- DATOS COMPLETOS -------- #
with st.expander("🔍 Ver datos completos"):
    st.dataframe(df_filtrado, use_container_width=True)


# -------- RESULTADOS -------- #
st.subheader("📋 Datos Filtrados")
st.dataframe(df_filtrado, use_container_width=True)
