import streamlit as st
import pandas as pd
import numpy as np
import pvlib
from pvlib import irradiance
from pvlib.location import Location

# -----------------------------------------------------------------------
# CONFIGURACIÓN INTERFAZ

st.set_page_config(
    page_title="Simulador Solar",
    page_icon="☀️",
    layout="wide"
)

st.markdown("""
<style>

/* Fondo general */
.stApp {
    background-color: #F8FAFC;
}

/* Texto general */
html, body, p, span, div, label {
    color: #111827 !important;
}

/* Títulos */
h1, h2, h3, h4, h5 {
    color: #111827 !important;
}

/* Inputs */
input {
    color: #111827 !important;
    background-color: white !important;
}

/* Number inputs */
[data-baseweb="input"] {
    background-color: white !important;
}

[data-baseweb="input"] input {
    color: #111827 !important;
}

/* Selectbox */
[data-baseweb="select"] {
    background-color: white !important;
}

[data-baseweb="select"] * {
    color: #111827 !important;
}

/* Menús desplegables */
ul {
    background-color: white !important;
}

li {
    background-color: white !important;
    color: #111827 !important;
}

/* Tabs */
button[role="tab"] {
    color: #111827 !important;
    background-color: #E2E8F0 !important;
    border-radius: 8px;
}

button[role="tab"][aria-selected="true"] {
    background-color: #0EA5E9 !important;
    color: white !important;
}

/* Expanders */
.streamlit-expanderHeader {
    color: #111827 !important;
    background-color: #F1F5F9 !important;
}

/* Tarjetas */
.cajita {
    background-color: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #E2E8F0;
    color: #111827;
    box-shadow: 0 4px 14px rgba(15,23,42,0.06);
}

.tarjeta {
    background-color: white;
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 14px rgba(15,23,42,0.06);
}

/* Texto tarjetas */
.valor {
    font-size: 28px;
    font-weight: bold;
    color: #0EA5E9;
}

.texto {
    color: #111827;
}

/* Botones */
.stButton button {
    background-color: #0EA5E9;
    color: white;
    border-radius: 12px;
    font-weight: bold;
    border: none;
}

.stButton button:hover {
    background-color: #0284C7;
    color: white;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    background-color: white !important;
    color: #111827 !important;
}

/* Sidebar por si vuelve a aparecer */
[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
}

/* Dropdown abierto */
div[role="listbox"] {
    background-color: white !important;
}

div[role="option"] {
    color: #111827 !important;
    background-color: white !important;
}

</style>
""", unsafe_allow_html=True)

st.title("☀️ Simulador de Generación Solar Fotovoltaica")

st.markdown("""
<div class="cajita">
Este simulador estima la energía generada por un sistema fotovoltaico y la compara
con una demanda eléctrica aproximada. En modo básico solo se piden los datos principales;
los parámetros técnicos se pueden ajustar en la sección avanzada.
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# CIUDADES

ciudades = {
    "Monterrey": [25.6866, -100.3161, 512, "America/Monterrey"],
    "CDMX": [19.4326, -99.1332, 2240, "America/Mexico_City"],
    "Guadalajara": [20.6597, -103.3496, 1566, "America/Mexico_City"],
    "Querétaro": [20.5888, -100.3899, 1820, "America/Mexico_City"],
    "Mérida": [20.9674, -89.5926, 10, "America/Merida"],
    "Tijuana": [32.5149, -117.0382, 20, "America/Tijuana"],
    "Cancún": [21.1619, -86.8515, 10, "America/Cancun"]
}

# -----------------------------------------------------------------------
# CONDICIONES INICIALES

st.subheader("Condiciones iniciales")

tab1, tab2, tab3 = st.tabs([
    "📍 Ubicación",
    "🔋 Sistema y demanda",
    "📅 Fechas"
])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        modo_ubicacion = st.selectbox(
            "Forma de elegir ubicación",
            ["Ciudad predefinida", "Ubicación personalizada"]
        )

    with col2:
        if modo_ubicacion == "Ciudad predefinida":
            ciudad = st.selectbox("Ciudad", list(ciudades.keys()))
            latitud, longitud, altitud, zona_horaria = ciudades[ciudad]
        else:
            ciudad = st.text_input("Nombre de la ubicación", "Ubicación personalizada")

    if modo_ubicacion == "Ubicación personalizada":
        col3, col4, col5, col6 = st.columns(4)

        with col3:
            latitud = st.number_input("Latitud", value=25.6866, format="%.6f")

        with col4:
            longitud = st.number_input("Longitud", value=-100.3161, format="%.6f")

        with col5:
            altitud = st.number_input("Altitud (m)", value=512)

        with col6:
            zona_horaria = st.selectbox(
                "Zona horaria",
                [
                    "America/Monterrey",
                    "America/Mexico_City",
                    "America/Tijuana",
                    "America/Cancun",
                    "America/Merida"
                ]
            )

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        numero_paneles = st.slider("Número de paneles", 1, 1000, 200)

    with col2:
        kw_max = st.number_input("Demanda máxima estimada (kW)", value=50.0)

    with col3:
        tipo_consumo = st.selectbox(
            "Tipo de consumo",
            ["Industrial continuo", "Comercial", "Residencial"]
        )

with tab3:
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input("Fecha inicial", value=pd.to_datetime("2025-01-01"))

    with col2:
        end_date = st.date_input("Fecha final", value=pd.to_datetime("2025-12-31"))

    with col3:
        dia_plot = st.date_input("Día a graficar", value=pd.to_datetime("2025-01-15"))

# -----------------------------------------------------------------------
# VALORES AUTOMÁTICOS

area_panel_unitaria = 2.583
kw_panel_unitario = 0.6
eficiencia = 0.22
perdidas = 0.20
inclinacion = min(max(abs(latitud), 10), 35)
orientacion = 180.0
mult_no_verano = 0.8

if tipo_consumo == "Industrial continuo":
    kw_min = kw_max * 0.40
    mult_finde = 0.5

elif tipo_consumo == "Comercial":
    kw_min = kw_max * 0.15
    mult_finde = 0.7

else:
    kw_min = kw_max * 0.10
    mult_finde = 0.9

# -----------------------------------------------------------------------
# AJUSTES AVANZADOS

with st.expander("⚙️ Ajustes avanzados del modelo"):

    st.markdown("""
    Aquí se pueden modificar supuestos técnicos del sistema.  
    """)

    st.markdown("### Panel solar")

    col1, col2, col3 = st.columns(3)

    with col1:
        area_panel_unitaria = st.number_input(
            "Área por panel (m²)",
            value=area_panel_unitaria,
            help="Área física aproximada de cada panel solar."
        )

    with col2:
        kw_panel_unitario = st.number_input(
            "Potencia nominal por panel (kW)",
            value=kw_panel_unitario,
            help="Potencia máxima teórica de cada panel. 0.6 kW equivale a 600 W."
        )

    with col3:
        eficiencia = st.slider(
            "Eficiencia del panel",
            0.01,
            0.40,
            eficiencia,
            help="Porcentaje de irradiancia que el panel convierte en electricidad."
        )

    st.markdown("### Instalación")

    col4, col5, col6 = st.columns(3)

    with col4:
        perdidas = st.slider(
            "Pérdidas del sistema",
            0.0,
            0.50,
            perdidas,
            help="Pérdidas por inversor, temperatura, cables, suciedad u otros factores."
        )

    with col5:
        inclinacion = st.slider(
            "Inclinación del panel (°)",
            0.0,
            90.0,
            float(inclinacion),
            help="Ángulo del panel respecto al suelo."
        )

    with col6:
        orientacion = st.slider(
            "Orientación / azimut (°)",
            0.0,
            360.0,
            orientacion,
            help="180° apunta al sur, normalmente recomendado en México."
        )

    st.markdown("### Demanda")

    col7, col8, col9 = st.columns(3)

    with col7:
        kw_min = st.number_input(
            "Demanda mínima (kW)",
            value=float(kw_min),
            help="Carga mínima aproximada de la planta o instalación."
        )

    with col8:
        mult_finde = st.slider(
            "Consumo en fin de semana",
            0.0,
            1.5,
            float(mult_finde),
            help="Reduce o aumenta la demanda durante sábados y domingos."
        )

    with col9:
        mult_no_verano = st.slider(
            "Consumo fuera de verano",
            0.0,
            1.5,
            float(mult_no_verano),
            help="Ajusta la demanda en meses fuera de mayo a octubre."
        )

# -----------------------------------------------------------------------
# FUNCIÓN PRINCIPAL

def simular_sistema():
    ubicacion = Location(
        latitud,
        longitud,
        zona_horaria,
        altitud,
        ciudad
    )

    area_panel_total = area_panel_unitaria * numero_paneles
    kw_panel_max = kw_panel_unitario * numero_paneles

    tiempos = pd.date_range(
        start=str(start_date),
        end=str(end_date),
        freq="15min",
        tz=ubicacion.tz
    )

    posicion_sol = ubicacion.get_solarposition(tiempos)

    zenit = posicion_sol["apparent_zenith"]
    azimut = posicion_sol["azimuth"]

    cd = pvlib.clearsky.ineichen(
        zenit,
        airmass_absolute=1.5,
        linke_turbidity=3,
        altitude=altitud
    )

    ghi = cd["ghi"]
    dhi = cd["dhi"]
    dni = cd["dni"]

    dni_extra = irradiance.get_extra_radiation(tiempos)

    irradiancia = irradiance.get_total_irradiance(
        surface_tilt=inclinacion,
        surface_azimuth=orientacion,
        dni=dni,
        ghi=ghi,
        dhi=dhi,
        dni_extra=dni_extra,
        solar_zenith=zenit,
        solar_azimuth=azimut
    )

    irradiancia_total = irradiancia["poa_global"]
    irradiancia_difusa = irradiancia["poa_diffuse"]

    potencia_panel = irradiancia_total * area_panel_total * eficiencia / 1000
    potencia_panel_difusa = irradiancia_difusa * area_panel_total * eficiencia / 1000

    potencia_total = potencia_panel * (1 - perdidas)
    potencia_total = np.clip(potencia_total, 0, kw_panel_max)

    hora_float = tiempos.hour.values + tiempos.minute.values / 60.0

    horas_clave = [
        0, 4, 5, 6, 7, 8, 9, 11,
        13, 14, 15, 16, 17, 18, 19, 20, 24
    ]

    perfil_norm = [
        0, 0, 0.05, 0.4, 0.8, 0.95, 1.0, 0.9,
        0.75, 0.75, 0.95, 1.0, 0.85, 0.4, 0.1, 0, 0
    ]

    plantilla_base = np.interp(
        hora_float,
        horas_clave,
        perfil_norm
    )

    es_verano = tiempos.month.isin([5, 6, 7, 8, 9, 10])
    mult_vera = np.where(es_verano, 1.0, mult_no_verano)

    es_finde = tiempos.weekday >= 5
    mult_fin = np.where(es_finde, mult_finde, 1.0)

    plantilla_final = plantilla_base * mult_vera * mult_fin

    demanda = kw_min + (kw_max - kw_min) * plantilla_final
    demanda_restante = np.maximum(0, demanda - potencia_total)

    df_anual = pd.DataFrame({
        "ghi": ghi,
        "dni": dni,
        "dhi": dhi,
        "potencia_total": potencia_total,
        "potencia_panel": potencia_panel,
        "potencia_panel_difusa": potencia_panel_difusa,
        "demanda": demanda,
        "demanda_restante": demanda_restante
    }, index=tiempos)

    df_dia = df_anual.loc[str(dia_plot)]

    horas = (
        pd.to_datetime(str(end_date))
        - pd.to_datetime(str(start_date))
    ) / pd.Timedelta(hours=1)

    total_energia_generada = df_anual["potencia_total"].sum() * (15 / 60)
    total_energia_consumida = df_anual["demanda"].sum() * (15 / 60)

    factor_planta_demanda = total_energia_consumida / (kw_max * horas)
    factor_planta_solar = total_energia_generada / (kw_panel_max * horas)

    cobertura_solar = total_energia_generada / total_energia_consumida

    resumen = {
        "energia_generada": float(total_energia_generada),
        "energia_consumida": float(total_energia_consumida),
        "factor_demanda": float(factor_planta_demanda),
        "factor_solar": float(factor_planta_solar),
        "cobertura_solar": float(cobertura_solar),
        "area_total": float(area_panel_total),
        "potencia_instalada": float(kw_panel_max)
    }

    return df_anual, df_dia, resumen

# -----------------------------------------------------------------------
# RESULTADOS

col_b1, col_b2, col_b3 = st.columns([1, 1, 1])

with col_b2:
    ejecutar = st.button(
        "Ejecutar simulación",
        use_container_width=True
    )

if ejecutar:

    df_anual, df_dia, resumen = simular_sistema()

    st.subheader("Resumen del sistema")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="tarjeta">
                <div class="texto">Energía generada</div>
                <div class="valor">{resumen['energia_generada']:,.0f} kWh</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="tarjeta">
                <div class="texto">Energía consumida</div>
                <div class="valor">{resumen['energia_consumida']:,.0f} kWh</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="tarjeta">
                <div class="texto">Factor solar</div>
                <div class="valor">{resumen['factor_solar']:.2%}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="tarjeta">
                <div class="texto">Cobertura solar</div>
                <div class="valor">{resumen['cobertura_solar']:.2%}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Datos usados en la simulación")

    col_d1, col_d2, col_d3 = st.columns(3)

    with col_d1:
        st.write("Ubicación:", ciudad)
        st.write("Latitud:", latitud)
        st.write("Longitud:", longitud)

    with col_d2:
        st.write("Paneles:", numero_paneles)
        st.write("Área total:", f"{resumen['area_total']:,.2f} m²")
        st.write("Potencia instalada:", f"{resumen['potencia_instalada']:,.2f} kW")

    with col_d3:
        st.write("Inclinación:", f"{inclinacion:.2f}°")
        st.write("Orientación:", f"{orientacion:.2f}°")
        st.write("Pérdidas:", f"{perdidas:.0%}")

    st.subheader("Mapa de ubicación")

    mapa = pd.DataFrame({
        "lat": [latitud],
        "lon": [longitud]
    })

    st.map(mapa)

    st.subheader("Demanda vs Generación Solar")
    st.line_chart(df_dia[["demanda", "potencia_total"]])

    st.subheader("Irradiancia Solar")
    st.line_chart(df_dia[["ghi", "dni", "dhi"]])

    st.subheader("Potencia del Panel")
    st.line_chart(df_dia[["potencia_panel", "potencia_panel_difusa"]])

    with st.expander("Tabla anual"):
        st.dataframe(df_anual)

    csv = df_anual.to_csv().encode("utf-8")

    st.download_button(
        label="Descargar datos en CSV",
        data=csv,
        file_name="simulacion_solar.csv",
        mime="text/csv"
    )

else:
    st.info("Configura los datos de la parte superior y presiona Ejecutar simulación.")

# prueba github