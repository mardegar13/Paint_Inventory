import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId  # <-- Nuevo: Necesario para buscar y borrar botes exactos

# --- ESTÉTICA BONITA Y LIMPIA (Letras negras, detalles verdes) ---
st.markdown("""
    <style>
    /* Letras negras y fondo claro/limpio */
    .stApp {
        background-color: #FAFAFA;
    }
    h1, h2, h3, p, span, label {
        color: #111111 !important; 
    }
    /* Estilo de los botones (Verde elegante y bordes redondeados) */
    .stButton>button {
        background-color: #007A33;
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #005c26;
    }
    /* Barra de progreso verde */
    .stProgress > div > div > div > div {
        background-color: #007A33;
    }
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
st.title("🎨 Almacén de Pinturas")

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
                st.rerun() # Recarga la página para que aparezca al instante
            else:
                st.warning("Ponle nombre y código, churra.")

st.markdown("---")
st.subheader("📦 Stock Actual")
datos = list(coleccion.find())

# --- LISTA DE STOCK CON OPCIONES DE EDITAR Y BORRAR ---
if datos:
    for item in datos:
        # Fila principal con la información
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
            
        # Panel desplegable para EDITAR y BORRAR (usando el ID único del bote)
        with st.expander(f"⚙️ Opciones de '{item.get('nombre')}'"):
            tab_editar, tab_borrar = st.tabs(["✏️ Editar", "🗑️ Borrar"])
            
            # Pestaña Editar
            with tab_editar:
                with st.form(key=f"edit_form_{item['_id']}"):
                    new_nom = st.text_input("Nombre", value=item.get("nombre"))
                    new_cod = st.text_input("Código Eurotex", value=item.get("codigo"))
                    new_mezcla = st.checkbox("Mezclada con agua", value=item.get("mezclada"))
                    new_porc = st.slider("Porcentaje", 0, 100, item.get("porcentaje"), step=5, key=f"sld_{item['_id']}")
                    
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
                        st.rerun() # Actualiza la pantalla en tiempo real
            
            # Pestaña Borrar
            with tab_borrar:
                st.warning("⚠️ ¿Seguro que quieres eliminar este bote del sistema?")
                # Clave única para el botón usando el ID del bote
                if st.button("Sí, borrar bote", key=f"del_{item['_id']}"):
                    coleccion.delete_one({"_id": ObjectId(item["_id"])})
                    st.rerun()
                    
        st.markdown("---") # Línea separadora entre botes
else:
    st.info("El almacén está vacío. ¡Dale a añadir pintura!")

