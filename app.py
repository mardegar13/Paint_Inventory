import streamlit as st
from pymongo import MongoClient

# --- CONFIGURACIÓN DE ESTÉTICA VERDE Y BLANCA ---
st.markdown("""
    <style>
    /* Fondo de la aplicación blanco */
    .stApp {
        background-color: #FFFFFF;
    }
    /* Títulos y textos principales en verde oscuro */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #007A33 !important; 
    }
    /* Estilo de los botones (Fondo verde, texto blanco) */
    .stButton>button {
        background-color: #007A33;
        color: #FFFFFF !important;
        border: 1px solid #007A33;
    }
    /* Color de la barra de progreso en verde */
    .stProgress > div > div > div > div {
        background-color: #007A33;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
try:
    url_via_secrets = st.secrets["MONGODB_URL"]
    client = MongoClient(url_via_secrets)
    db = client['almacen_tifos']
    coleccion = db['pinturas']
except Exception as e:
    st.error(f"Error de conexion: {e}")

# --- DICCIONARIO DE COLORES EUROTEX ---
# Aquí es donde relacionamos el código de la tienda con el color real.
# Deberás añadir aquí los códigos exactos que soléis comprar.
eurotex_colors = {
    "BLANCO": "#FFFFFF",
    "NEGRO": "#000000",
    "VERDE ANDALUCIA": "#007A33",
    "VERDE OSCURO": "#004d1a",
    # Añade tus códigos de Eurotex así: "CODIGO_EUROTEX": "#Hexadecimal",
}

def obtener_color_hex(codigo):
    # Limpiamos el texto y lo ponemos en mayúsculas para evitar errores al teclear
    codigo_limpio = str(codigo).strip().upper()
    # Si encuentra el código, devuelve el color. Si no, devuelve un gris por defecto.
    return eurotex_colors.get(codigo_limpio, "#CCCCCC")

# --- INTERFAZ DE USUARIO ---
st.title("Inventario de Pinturas")

with st.form("nuevo_bote"):
    st.subheader("Añadir nuevo bote")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre de la pintura")
        codigo = st.text_input("Codigo Eurotex")
    with col2:
        mezclada = st.checkbox("Mezclada con agua")
        # El selector de color manual ha desaparecido
        
    porcentaje = st.slider("Cantidad restante (%)", min_value=0, max_value=100, value=100, step=5)
    
    enviar = st.form_submit_button("Guardar Pintura")

    if enviar and nombre and codigo:
        # Aquí el programa busca automáticamente el color basado en el código
        color_hex = obtener_color_hex(codigo)
        
        nuevo_bote = {
            "nombre": nombre,
            "codigo": codigo,
            "color_hex": color_hex,
            "mezclada": mezclada,
            "porcentaje": porcentaje
        }
        coleccion.insert_one(nuevo_bote)
        st.success(f"Pintura guardada correctamente.")

st.markdown("---")
st.subheader("Stock Actual")
datos = list(coleccion.find())

if datos:
    for item in datos:
        col_color, col_info, col_estado = st.columns([1, 3, 2])
        
        with col_color:
            color = item.get('color_hex', '#CCCCCC')
            # Círculo de color dinámico
            st.markdown(
                f"<div style='width: 50px; height: 50px; background-color: {color}; border-radius: 50%; border: 2px solid #007A33; margin-top: 10px;'></div>", 
                unsafe_allow_html=True
            )
            
        with col_info:
            st.markdown(f"**{item.get('nombre', 'Sin nombre')}**")
            st.caption(f"Codigo Eurotex: {item.get('codigo', 'N/A')}")
            if item.get('mezclada'):
                st.caption("Mezclada con agua")
            else:
                st.caption("Pura")
                
        with col_estado:
            porcentaje_actual = item.get('porcentaje', 0)
            st.write(f"Queda: **{porcentaje_actual}%**")
            st.progress(porcentaje_actual / 100.0)
            
        st.markdown("---")
else:
    st.info("El almacen esta vacio.")
