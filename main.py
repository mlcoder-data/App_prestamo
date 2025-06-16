import streamlit as st
st.set_page_config(page_title="Control de Llaves", layout="wide")  # ✅ Primera línea relacionada con Streamlit

from streamlit_option_menu import option_menu
from datetime import datetime
import sqlite3
import pandas as pd
import altair as alt
from auth import login

# Login antes de continuar
if not login():
    st.stop()

# === database.py ===

def crear_tabla():
    conn = sqlite3.connect("llaves.db") #SI SE CREA UNA NUEVA RUTA EN LA BD COLACARLA COMPLETA
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            area TEXT,
            salon TEXT,
            accion TEXT,
            fecha_hora TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            tipo TEXT,
            estado TEXT,
            salon TEXT,
            responsable TEXT,
            fecha_registro TEXT
        )
    ''')
    conn.commit()
    conn.close()

def registrar_evento(nombre, area, salon, accion, fecha_hora):
    conn = sqlite3.connect("data/llaves.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO llaves (nombre, area, salon, accion, fecha_hora) VALUES (?, ?, ?, ?, ?)",
                   (nombre, area, salon, accion, fecha_hora))
    conn.commit()
    conn.close()

def obtener_historial():
    conn = sqlite3.connect("llaves.db") 
    df = pd.read_sql_query("SELECT * FROM llaves ORDER BY fecha_hora DESC", conn)
    conn.close()
    return df

def obtener_inventario():
    conn = sqlite3.connect("llaves.db")
    df = pd.read_sql_query("SELECT * FROM inventario ORDER BY fecha_registro DESC", conn)
    conn.close()
    return df

def agregar_equipo(nombre, tipo, estado, salon, responsable, fecha_registro):
    conn = sqlite3.connect("llaves.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventario (nombre, tipo, estado, salon, responsable, fecha_registro) VALUES (?, ?, ?, ?, ?, ?)",
                   (nombre, tipo, estado, salon, responsable, fecha_registro))
    conn.commit()
    conn.close()

def llave_activa(salon):
    conn = sqlite3.connect("llaves.db")
    df = pd.read_sql_query("SELECT * FROM llaves WHERE salon = ? ORDER BY fecha_hora DESC", conn, params=(salon,))
    conn.close()

    if df.empty:
        return False  # No hay registros, la llave está disponible

    # Convertimos la fecha a datetime
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'], errors='coerce')

    # Tomamos la última acción registrada
    ultima_accion = df.iloc[0]['accion']

    # Si la última acción fue "Entregada", entonces sigue activa
    return ultima_accion == 'Entregada'

def eliminar_registro(registro_id):
    conn = sqlite3.connect("llaves.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM llaves WHERE id = ?", (registro_id,))
    conn.commit()
    conn.close()


# === Fin database.py ===
crear_tabla()

st.markdown("""
    <style>
    body {
        background-color: #F9F9F9;
    }
    .main {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    h1, h2, h3, h4 {
        color: #4F8BF9;
    }
    .stButton > button {
        border-radius: 8px;
        background-color: #4F8BF9;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #3a6edc;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #2A6E1D;'>🔑 Sistema Control de llaves Almacen</h1>
""", unsafe_allow_html=True)

with st.sidebar:
    choice = option_menu(
        menu_title="Menú Principal",
        options=["Registrar llave", "Historial", "Estadísticas", "Inventario por salón", "Llaves activas"],
        icons=["pencil-square", "clock-history", "bar-chart", "boxes", "key"]
    )

data = obtener_historial()
if not data.empty:
    data['fecha_hora'] = pd.to_datetime(data['fecha_hora'])
    data['día_semana'] = data['fecha_hora'].dt.day_name()
    data['fecha'] = data['fecha_hora'].dt.date
    data['hora'] = data['fecha_hora'].dt.hour

# Tabs para dividir visualizaciones EN EL HISTORIAL
if choice == "Estadísticas":
    st.subheader("📈 Estadísticas Generales")
    if not data.empty:
        tab1, tab2, tab3, tab4 = st.tabs(["Resumen", "Por día", "Por hora", "Top usuarios"])

        with tab1:
            st.metric("🔢 Total de registros", len(data))
            st.altair_chart(alt.Chart(data).mark_bar().encode(x='area', y='count()', tooltip=['area', 'count()']).properties(width=600))
            st.altair_chart(alt.Chart(data).mark_bar().encode(x='salon', y='count()', tooltip=['salon', 'count()']).properties(width=600))

        with tab2:
            st.markdown("### 📅 Actividad por día de la semana")
            st.altair_chart(alt.Chart(data).mark_bar().encode(x='día_semana', y='count()', tooltip=['día_semana', 'count()']).properties(width=600))
            actividad_diaria = data.groupby('fecha').size().reset_index(name='registros')
            st.markdown("### 📈 Actividad diaria")
            st.altair_chart(alt.Chart(actividad_diaria).mark_line(point=True).encode(x='fecha:T', y='registros').properties(width=600))

        with tab3:
            st.markdown("### 🕒 Horas con más actividad")
            st.altair_chart(alt.Chart(data).mark_bar().encode(x='hora:O', y='count()', tooltip=['hora', 'count()']).properties(width=600))
            st.markdown("### 📤 Entregas vs Devoluciones")
            st.altair_chart(alt.Chart(data).mark_bar().encode(x='accion', y='count()', tooltip=['accion', 'count()']).properties(width=600))

        with tab4:
            st.markdown("### 👨‍🏫 Profesores más activos")
            st.altair_chart(alt.Chart(data).mark_bar().encode(x=alt.X('nombre', sort='-y'), y='count()', tooltip=['nombre', 'count()']).properties(width=600))
            top_areas = data['area'].value_counts().head(10).reset_index()
            top_areas.columns = ['area', 'count']
            st.markdown("### 🧭 Áreas más activas")
            st.altair_chart(alt.Chart(top_areas).mark_bar().encode(x='area', y='count', tooltip=['area', 'count']).properties(width=600))
    else:
        st.info("No hay datos suficientes para mostrar estadísticas.")

data = obtener_historial()
if not data.empty:
    data['fecha_hora'] = pd.to_datetime(data['fecha_hora'])
    data['día_semana'] = data['fecha_hora'].dt.day_name()
    data['fecha'] = data['fecha_hora'].dt.date
    data['hora'] = data['fecha_hora'].dt.hour

# === Autocompletado inteligente ===
st.sidebar.markdown("### 🔍 Búsqueda Inteligente")

nombre_buscado = st.sidebar.text_input("Buscar por profesor")
salon_buscado = st.sidebar.text_input("Buscar por salón")
area_buscada = st.sidebar.text_input("Buscar por área")

resultado_filtro = data.copy()

if nombre_buscado:
    resultado_filtro = resultado_filtro[resultado_filtro['nombre'].str.contains(nombre_buscado, case=False, na=False)]
if salon_buscado:
    resultado_filtro = resultado_filtro[resultado_filtro['salon'].str.contains(salon_buscado, case=False, na=False)]
if area_buscada:
    resultado_filtro = resultado_filtro[resultado_filtro['area'].str.contains(area_buscada, case=False, na=False)]

if nombre_buscado or salon_buscado or area_buscada:
    st.sidebar.success(f"🔎 {len(resultado_filtro)} resultado(s) encontrados")
    st.dataframe(resultado_filtro)

if choice == "Llaves activas":
    st.subheader("🔒 Llaves actualmente entregadas")
    entregas = data[data['accion'] == 'Entregada']
    devoluciones = data[data['accion'] == 'Devuelta']

    entregas['id_llave'] = entregas['nombre'] + entregas['area'] + entregas['salon']
    devoluciones['id_llave'] = devoluciones['nombre'] + devoluciones['area'] + devoluciones['salon']

    activas = entregas[~entregas['id_llave'].isin(devoluciones['id_llave'])].copy()
    activas['tiempo_transcurrido'] = ((pd.Timestamp.now() - activas['fecha_hora']).dt.total_seconds() // 60).astype(int)

    profesores = ["Todos"] + sorted(activas['nombre'].unique().tolist())
    areas = ["Todos"] + sorted(activas['area'].unique().tolist())
    salones = ["Todos"] + sorted(activas['salon'].unique().tolist())

    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_prof = st.selectbox("Filtrar por profesor", profesores)
    with col2:
        filtro_area = st.selectbox("Filtrar por área", areas)
    with col3:
        filtro_salon = st.selectbox("Filtrar por salón", salones)

    if filtro_prof != "Todos":
        activas = activas[activas['nombre'] == filtro_prof]
    if filtro_area != "Todos":
        activas = activas[activas['area'] == filtro_area]
    if filtro_salon != "Todos":
        activas = activas[activas['salon'] == filtro_salon]

# == Alertas de entregas de llaves:

    if not activas.empty:
        for index, row in activas.iterrows():
            col1, col2 = st.columns([5, 1])
            tiempo = f"⏱️ {row['tiempo_transcurrido']} min"
            alerta = "🔴" if row['tiempo_transcurrido'] > 120 else "🟢"
            with col1:
                st.markdown(f"""
                    <div class='card'>
                        {alerta} <strong>{row['salon']}</strong> entregado a <strong>{row['nombre']}</strong> ({row['area']})<br>
                        ⏱️ Tiempo: <span style='color:#F44336'>{row['tiempo_transcurrido']} min</span>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Devolver", key=f"dev_{index}"):
                    registrar_evento(
                        row['nombre'], row['area'], row['salon'],
                        'Devuelta', datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    st.success(f"Llave de {row['salon']} devuelta.")
                    st.rerun()
    else:
        st.success("✅ No hay llaves prestadas actualmente.")


if choice == "Registrar llave":
    st.subheader("Registrar entrega o devolución de llave")

    nombre = st.text_input("Nombre del profesor")
    area = st.selectbox("Área", ["ADSO", "MULTIMEDIA", "REDES", "SERVICIOS TICS", "ELECTRÓNICA"])
    salon_eq = st.selectbox("Salón", ["Sala 1", "Sala 2", "Sala 3", "Sala 4", "Sala Medio Ambiental", "Sala 7", "Sala 8", "Sala 9",
                                        "Sala 316-F","Sala 303-F","Sala 304-F", "Automatica", "Sala 10", "Estudio Multimedia", "Sala 308-F",
                                          "Sala 309-F", "Sala 310-F", "Sala 410-C","Sala 305-C","Sala de Juntas","Sala 208-F"])
    accion = st.radio("Acción", ["Entregada", "Devuelta"])

    if st.button("Registrar"):
        if nombre and area and salon_eq:
            if accion == "Entregada" and llave_activa(salon_eq):
                st.error(f"La llave del salón {salon_eq} ya está prestada. Primero debe devolverse.")
            else:
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                registrar_evento(nombre, area, salon_eq, accion, fecha_hora)
                st.success(f"Registro exitoso: llave {accion.lower()} para el salón {salon_eq}")
                st.rerun()
        else:
            st.warning("Por favor, completa todos los campos")

    # === Mostrar llaves disponibles ===
    st.markdown("## 🔓 Llaves disponibles actualmente")

    # Detectar salones registrados en la base y sus estados
    todos_salones = [
        "Sala 1", "Sala 2", "Sala 3", "Sala 4", "Sala Medio Ambiental", "Sala 7", "Sala 8", "Sala 9", "sala 10",
        "Sala 303-F", "Sala 304-F", "Sala 308-F", "Sala 309-F", "Sala 310-F", "sala 316-F", "sala 208-F",
        "Sala 410-C", "Sala 305-C", "Sala de Juntas", "Estudio Multimedia", "Laboratorio Automatica"
    ]

    # Validar si la variable activas existe
    if 'activas' in locals():
        salones_prestados = activas['salon'].unique().tolist()
        salones_disponibles = sorted([s for s in todos_salones if s not in salones_prestados])
    else:
        salones_disponibles = sorted(todos_salones)

    if salones_disponibles:
        cols = st.columns(3)
        for i, salon in enumerate(salones_disponibles):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background-color: #2E7D32; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <h4 style="color:#daebdb;">🔓 {salon}</h4>
                        <p><strong>Estado:</strong> Disponible</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("✅ Actualmente no hay llaves disponibles.")



elif choice == "Inventario por salón":
    st.subheader("📦 Inventario por salón")

    inventario = obtener_inventario()
    salones = ["Todos"] + sorted(inventario['salon'].unique().tolist()) if not inventario.empty else ["Todos"]
    salon_filtro = st.selectbox("Filtrar por salón", salones)

    if salon_filtro != "Todos" and not inventario.empty:
        inventario = inventario[inventario['salon'] == salon_filtro]

    if not inventario.empty:
        st.dataframe(inventario, use_container_width=True)
    else:
        st.info("No hay equipos registrados.")

    st.markdown("---")
    st.markdown("### ➕ Agregar nuevo equipo")

    with st.form("form_equipo"):
        nombre_eq = st.text_input("Nombre del equipo")
        tipo_eq = st.selectbox("Tipo", ["Portátil", "Mouse", "Teclado", "Osciloscopio", "Herramienta", "Otro", "Computador De mesa"])
        estado_eq = st.selectbox("Estado", ["Disponible", "En uso", "Dañado", "Extraviado"])
        salon_eq = st.selectbox("Salón", ["Sala 1", "Sala 2", "Sala 3", "Sala 4", "Sala Medio Ambiental", "Sala 7", "Sala 8", "Sala 9",
                                        "Sala 316-F","Sala 303-F","Sala 304-F", "Automatica", "Sala 10", "Estudio Multimedia", "Sala 308-F",
                                        "Sala 309-F", "Sala 310-F", "Sala 410-C","Sala 305-C"])
        responsable_eq = st.text_input("Responsable (opcional)")
        submit = st.form_submit_button("Agregar equipo")

        if submit:
            if nombre_eq and tipo_eq and estado_eq and salon_eq:
                fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                agregar_equipo(nombre_eq, tipo_eq, estado_eq, salon_eq, responsable_eq, fecha_registro)
                st.success("Equipo agregado exitosamente")
                st.rerun()
            else:
                st.warning("Por favor, completa todos los campos obligatorios")
# == HISTORIAL CON PESTAÑAS "DEVUELTAS", "ENTREGADAS"

elif choice == "Historial":
    st.subheader("📋 Historial de llaves")

    es_admin = st.session_state.get("is_admin", False)

    
    def filtros_comunes(df, key_prefix="filtro"):
        profesores = ["Todos"] + sorted(df['nombre'].unique().tolist())
        salones = ["Todos"] + sorted(df['salon'].unique().tolist())
        areas = ["Todos"] + sorted(df['area'].unique().tolist())
        dias = ["Todos"] + sorted(df['día_semana'].unique().tolist())

        col1, col2, col3 = st.columns(3)
        with col1:
            f_profesor = st.selectbox("Filtrar por profesor", profesores, key=f"{key_prefix}_profesor")
        with col2:
            f_salon = st.selectbox("Filtrar por salón", salones, key=f"{key_prefix}_salon")
        with col3:
            f_area = st.selectbox("Filtrar por área", areas, key=f"{key_prefix}_area")

        col4, col5 = st.columns(2)
        with col4:
            f_dia = st.selectbox("Filtrar por día de la semana", dias, key=f"{key_prefix}_dia")
        with col5:
            f_rango = st.date_input("Filtrar por rango de fechas", [], key=f"{key_prefix}_fecha")

        if f_profesor != "Todos":
            df = df[df['nombre'] == f_profesor]
        if f_salon != "Todos":
            df = df[df['salon'] == f_salon]
        if f_area != "Todos":
            df = df[df['area'] == f_area]
        if f_dia != "Todos":
            df = df[df['día_semana'] == f_dia]
        if len(f_rango) == 2:
            inicio, fin = f_rango
            df = df[(df['fecha'] >= inicio) & (df['fecha'] <= fin)]

        return df

    tab1, tab2, tab3 = st.tabs(["🧾 Todo", "📥 Entregas", "📤 Devoluciones"])

    with tab1:
        st.markdown("### 🧾 Historial completo")
        df_filtrado = filtros_comunes(data.copy(), key_prefix="todo")
        st.dataframe(df_filtrado.drop(columns=["día_semana", "fecha", "hora"]), use_container_width=True)

        if es_admin:
            st.markdown("### 🛠️ Panel de gestión de registros")
            for idx, row in df_filtrado.iterrows():
                with st.expander(f"🔑 {row['salon']} - {row['accion']} por {row['nombre']} ({row['area']})"):
                    st.markdown(f"""
                    **🕒 Fecha y hora:** {row['fecha_hora']}  
                    **👤 Profesor:** {row['nombre']}  
                    **📍 Área:** {row['area']}  
                    **🏫 Salón:** {row['salon']}  
                    **📘 Acción:** {row['accion']}
                    """)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{row['id']}"):
                            eliminar_registro(row['id'])
                            st.success("Registro eliminado correctamente")
                            st.rerun()
                    with col2:
                        st.info("✏️ Próximamente: botón para editar registro.")

    with tab2:
        st.markdown("### 📥 Solo entregas")
        df_entregas = data[data['accion'] == "Entregada"].copy()
        df_filtrado = filtros_comunes(df_entregas, key_prefix="entregas")
        st.dataframe(df_filtrado.drop(columns=["día_semana", "fecha", "hora"]), use_container_width=True)

    with tab3:
        st.markdown("### 📤 Solo devoluciones")
        df_devoluciones = data[data['accion'] == "Devuelta"].copy()
        df_filtrado = filtros_comunes(df_devoluciones, key_prefix="devoluciones")
        st.dataframe(df_filtrado.drop(columns=["día_semana", "fecha", "hora"]), use_container_width=True)

## == APARTADO DE ESTADISTICAS

elif choice == "Estadísticas":
    st.subheader("📈 Estadísticas Generales")
    if not data.empty:
        st.metric("🔢 Total de registros", len(data))

        st.markdown("### 📊 Registros por área")
        st.altair_chart(alt.Chart(data).mark_bar().encode(
            x=alt.X('area', title='Área'),
            y=alt.Y('count()', title='Cantidad'),
            tooltip=['area', 'count()']
        ).properties(width=600))

        st.markdown("### 📊 Registros por salón")
        st.altair_chart(alt.Chart(data).mark_bar().encode(
            x=alt.X('salon', title='Salón'),
            y=alt.Y('count()', title='Cantidad'),
            tooltip=['salon', 'count()']
        ).properties(width=600))

        st.markdown("### 📅 Actividad por día de la semana")
        st.altair_chart(alt.Chart(data).mark_bar().encode(
            x=alt.X('día_semana', title='Día de la semana'),
            y=alt.Y('count()', title='Cantidad'),
            tooltip=['día_semana', 'count()']
        ).properties(width=600))

        actividad_diaria = data.groupby('fecha').size().reset_index(name='registros')
        st.markdown("### 📈 Actividad diaria del mes")
        st.altair_chart(alt.Chart(actividad_diaria).mark_line(point=True).encode(
            x=alt.X('fecha:T', title='Fecha'),
            y=alt.Y('registros', title='Cantidad')
        ).properties(width=600))

        st.markdown("### 🕒 Horas con más actividad")
        st.altair_chart(alt.Chart(data).mark_bar().encode(
            x=alt.X('hora:O', title='Hora del día'),
            y=alt.Y('count()', title='Cantidad'),
            tooltip=['hora', 'count()']
        ).properties(width=600))

        st.markdown("### 📤 Entregas vs Devoluciones")
        st.altair_chart(alt.Chart(data).mark_bar().encode(
            x=alt.X('accion', title='Acción'),
            y=alt.Y('count()', title='Cantidad'),
            tooltip=['accion', 'count()']
        ).properties(width=600))

        st.markdown("### 👨‍🏫 Profesores más activos")
        st.altair_chart(alt.Chart(data).mark_bar().encode(
            x=alt.X('nombre', sort='-y', title='Profesor'),
            y=alt.Y('count()', title='Cantidad'),
            tooltip=['nombre', 'count()']
        ).properties(width=600))

        st.markdown("### 🧭 Áreas más activas")
        top_areas = data['area'].value_counts().head(10).reset_index()
        top_areas.columns = ['area', 'count']
        st.altair_chart(alt.Chart(top_areas).mark_bar().encode(
            x=alt.X('area', title='Área'),
            y=alt.Y('count', title='Cantidad'),
            tooltip=['area', 'count']
        ).properties(width=600))
    else:
        st.info("No hay datos suficientes para mostrar estadísticas.")