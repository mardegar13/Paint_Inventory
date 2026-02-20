import streamlit as st
from pymongo import MongoClient

# 1. Conexión a MongoDB (Usando los Secrets que ya configuraste)
try:
    url_via_secrets = st.secrets["MONGODB_URL"]
    client = MongoClient(url_via_secrets)
    db = client['almacen_tifos']
    coleccion = db['pinturas']
except Exception as e:
    st.error(f"Error de conexión: {e}")

st.title("🎨 Inventario de Tifos Pro")

# 2. Formulario para añadir nueva pintura
with st.form("nuevo_bote"):
    st.subheader("Añadir nuevo bote")
    
    # Dividimos en dos columnas para que quede más bonito
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre (Ej: Rojo Fuego)")
        codigo = st.text_input("Código/Referencia (Ej: Montana RV-3020)")
    with col2:
        # ¡Magia! Un selector visual que nos da el código Hexadecimal para pintar la pantalla
        color_hex = st.color_picker("Selecciona el color exacto", "#FF0000")
        mezclada = st.checkbox("¿Mezclada con agua? 💧")
        
    # Un deslizador para poner el porcentaje a ojo
    porcentaje = st.slider("Cantidad restante (%)", min_value=0, max_value=100, value=100, step=5)
    
    enviar = st.form_submit_button("Guardar Pintura")

    if enviar and nombre:
        # Preparamos el "paquete" de datos para MongoDB
        nuevo_bote = {
            "nombre": nombre,
            "codigo": codigo,
            "color_hex": color_hex, # Guardamos el color visual
            "mezclada": mezclada,
            "porcentaje": porcentaje
        }
        coleccion.insert_one(nuevo_bote)
        st.success(f"¡{nombre} guardado correctamente!")

# 3. Visualización del Inventario (Lo que querías que quedara "guapo")
st.divider()
st.subheader("📦 Stock Actual")
datos = list(coleccion.find())

if datos:
    for item in datos:
        # Creamos 3 columnas: Color, Info y Estado
        col_color, col_info, col_estado = st.columns([1, 3, 2])
        
        with col_color:
            # Dibujamos un círculo con el color exacto usando un poco de HTML
            st.markdown(
                f"<div style='width: 50px; height: 50px; background-color: {item.get('color_hex', '#FFFFFF')}; border-radius: 50%; border: 2px solid #ccc;'></div>", 
                unsafe_allow_html=True
            )
            
        with col_info:
            st.markdown(f"**{item.get('nombre', 'Sin nombre')}**")
            st.caption(f"Código: {item.get('codigo', 'N/A')}")
            if item.get('mezclada'):
                st.caption("💧 Mezclada con agua")
            else:
                st.caption("🔥 Pura")
                
        with col_estado:
            porcentaje_actual = item.get('porcentaje', 0)
            st.write(f"Queda: **{porcentaje_actual}%**")
            # Barra de progreso visual según el porcentaje
            st.progress(porcentaje_actual / 100.0)
            
        st.divider() # Línea separadora entre botes
else:
    st.info("El almacén está vacío. ¡Añade el primer bote!")

