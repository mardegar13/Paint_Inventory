import streamlit as st
from pymongo import MongoClient

# 1. Configuración de la conexión
# RECUERDA: Cambia <password> por tu contraseña real y pon tu dirección

url_via_secrets = st.secrets["MONGODB_URL"]

try:
    client = MongoClient(url_via_secrets)
    db = client['almacen_tifos']  # Crea una base de datos llamada 'almacen_tifos'
    coleccion = db['pinturas']    # Crea una tabla llamada 'pinturas'
except Exception as e:
    st.error(f"Error de conexión: {e}")

st.title("🎨 Gestión de Pinturas - Tifos")

# 2. Formulario para añadir pintura
with st.form("nuevo_bote"):
    color = st.text_input("Color del bote:")
    litros = st.number_input("Cantidad (Litros):", min_value=0.0, step=0.5)
    enviar = st.form_submit_button("Guardar en la Nube")

    if enviar and color:
        # Insertar en MongoDB
        nuevo_bote = {"color": color, "litros": litros}
        coleccion.insert_one(nuevo_bote)
        st.success(f"¡{color} guardado correctamente!")

# 3. Visualización del Inventario
st.subheader("Inventario Actual")
datos = list(coleccion.find())

if datos:
    for item in datos:
        st.write(f"🖌️ **{item['color']}**: {item['litros']} Litros")
else:

    st.info("El almacén está vacío. ¡Añade el primer bote!")
