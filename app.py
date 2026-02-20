import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- ESTÉTICA BONITA Y LIMPIA ---
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3, p, span, label { color: #111111 !important; }
    .stButton>button {
        background-color: #007A33;
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #005c26; }
    .stProgress > div > div > div > div { background-color: #007A33; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
try:
    url_via_secrets = st.secrets["MONGODB_URL"]
    client = MongoClient(url_via_secrets)
    db = client['almacen_tifos']
    coleccion = db['pinturas']
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- DICCIONARIO DE COLORES EUROTEX ---
eurotex_colors = {
    "BLANCO": "#FFFFFF",
    "NEGRO": "#000000",
    "VERDE ANDALUCIA": "#007A33",
    "VERDE OSCURO": "#004d1a",
}

def obtener_color_hex(codigo):
    codigo_limpio = str(codigo).strip().upper()
    return eurotex_colors.get(codigo_limpio, "#CCCCCC")

# --- CABECERA ---
st.title("🎨 Almacén de Pintura")

# --- FORMULARIO PARA AÑADIR ---
with st.expander("➕ Añadir nueva pintura al stock", expanded=False):
    with st.form("nuevo_bote", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la pintura")
            codigo = st.text_input("Código Eurotex")
        with col2:
            mezclada = st.checkbox("¿Mezclada con agua?")
            porcentaje = st.slider("Cantidad restante (%)", 0, 100, 100, step=5)
        
        if st.form_submit_button("Guardar en Inventario"):
            if nombre and codigo:
                color_hex = obtener_color_hex(codigo)
                coleccion.insert_one({
                    "nombre": nombre,
                    "codigo": codigo,
                    "color_hex": color_hex,
                    "mezclada": mezclada,
                    "porcentaje": porcentaje
                })
                st.success("¡Añadido al almacén!")
                st.rerun()
            else:
                st.warning("Ponle nombre y código, churra.")

# --- OBTENER TODOS LOS DATOS DE LA BASE DE DATOS ---
datos_brutos = list(coleccion.find())

# --- BUSCADOR Y FILTROS ---
st.markdown("---")
st.subheader("🔍 Buscar y Filtrar")

# Tres columnas para que en el móvil se apilen bien solas
col_busq, col_ord, col_filtro = st.columns([2, 2, 2])

with col_busq:
    busqueda = st.text_input("Buscar por nombre o ref...", "").lower()
with col_ord:
    orden = st.selectbox("Ordenar por", ["Predeterminado", "Nombre (A-Z)", "Cantidad (Mayor a menor)", "Cantidad (Menor a mayor)"])
with col_filtro:
    filtro_mezcla = st.selectbox("Estado", ["Mostrar Todas", "Solo Puras 🔥", "Solo Mezcladas 💧"])

# Aplicar lógica de filtros y búsqueda
datos_filtrados = []
for item in datos_brutos:
    nom_item = item.get("nombre", "").lower()
    cod_item = item.get("codigo", "").lower()
    es_mezclada = item.get("mezclada", False)
    
    # Filtro de texto (Buscador)
    if busqueda and (busqueda not in nom_item and busqueda not in cod_item):
        continue
    
    # Filtro de mezcla
    if filtro_mezcla == "Solo Puras 🔥" and es_mezclada:
        continue
    if filtro_mezcla == "Solo Mezcladas 💧" and not es_mezclada:
        continue
        
    datos_filtrados.append(item)

# Aplicar lógica de ordenación
if orden == "Nombre (A-Z)":
    datos_filtrados = sorted(datos_filtrados, key=lambda x: x.get("nombre", "").lower())
elif orden == "Cantidad (Mayor a menor)":
    datos_filtrados = sorted(datos_filtrados, key=lambda x: x.get("porcentaje", 0), reverse=True)
elif orden == "Cantidad (Menor a mayor)":
    datos_filtrados = sorted(datos_filtrados, key=lambda x: x.get("porcentaje", 0))

st.markdown("---")
st.subheader(f"📦 Stock Actual ({len(datos_filtrados)} botes)")

# --- MOSTRAR LISTA DE STOCK ---
if datos_filtrados:
    for item in datos_filtrados:
        col_color, col_info, col_estado = st.columns([1, 3, 2])
        
        with col_color:
            color = item.get('color_hex', '#CCCCCC')
            st.markdown(
                f"<div style='width: 45px; height: 45px; background-color: {color}; border-radius: 50%; border: 2px solid #ccc; margin-top: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'></div>", 
                unsafe_allow_html=True
            )
            
        with col_info:
            st.markdown(f"**{item.get('nombre', 'Sin nombre')}**")
            st.caption(f"Ref: {item.get('codigo', 'N/A')} | {'💧 Mezclada' if item.get('mezclada') else '🔥 Pura'}")
                
        with col_estado:
            porcentaje_actual = item.get('porcentaje', 0)
            st.write(f"Queda: **{porcentaje_actual}%**")
            st.progress(porcentaje_actual / 100.0)
            
        # Pestañas de Edición (¡Ahora funcionan incluso con la lista filtrada!)
        with st.expander(f"⚙️ Opciones de '{item.get('nombre')}'"):
            tab_editar, tab_borrar = st.tabs(["✏️ Editar", "🗑️ Borrar"])
            
            with tab_editar:
                with st.form(key=f"edit_form_{item['_id']}"):
                    new_nom = st.text_input("Nombre", value=item.get("nombre"))
                    new_cod = st.text_input("Código Eurotex", value=item.get("codigo"))
                    new_mezcla = st.checkbox("Mezclada con agua", value=item.get("mezclada"))
                    new_porc = st.slider("Porcentaje", 0, 100, item.get("porcentaje"), step=5)
                    
                    if st.form_submit_button("Guardar Cambios"):
                        nuevo_color = obtener_color_hex(new_cod)
                        coleccion.update_one(
                            {"_id": ObjectId(item["_id"])},
                            {"$set": {
                                "nombre": new_nom, 
                                "codigo": new_cod, 
                                "color_hex": nuevo_color,
                                "mezclada": new_mezcla, 
                                "porcentaje": new_porc
                            }}
                        )
                        st.rerun()
            
            with tab_borrar:
                st.warning("⚠️ ¿Seguro que quieres eliminar este bote?")
                if st.button("Sí, borrar bote", key=f"del_{item['_id']}"):
                    coleccion.delete_one({"_id": ObjectId(item["_id"])})
                    st.rerun()
                    
        st.markdown("---")
else:
    if busqueda or filtro_mezcla != "Mostrar Todas":
        st.info("No se han encontrado botes con esos filtros. 🤷‍♂️")
    else:
        st.info("El almacén está vacío. ¡Dale a añadir pintura!")

