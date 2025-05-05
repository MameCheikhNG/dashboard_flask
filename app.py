import streamlit as st
import easyocr
import tempfile
import os
from PIL import Image

# ------------------------------
# ⚙️ Fonction d'extraction intelligente des infos CNI recto
# ------------------------------
def extract_infos_recto(text_lines):
    infos = {
        "Type de carte": "Carte CEDEAO",
        "Nom": "",
        "Prénom": "",
        "Numéro de carte": "",
        "Date de naissance": "",
        "Date de délivrance": "",
        "Date d’expiration": "",
        "Sexe": "",
        "Taille": "",
        "Adresse": "",
        "Centre d’enregistrement": ""
    }

    try:
        if len(text_lines) > 17:
            infos["Prénom"] = text_lines[7].strip()
            infos["Nom"] = text_lines[8].strip()
            infos["Date de naissance"] = text_lines[9].strip()
            infos["Taille"] = text_lines[10].strip()
            infos["Centre d’enregistrement"] = text_lines[11].strip()
            infos["Date de délivrance"] = text_lines[13].strip()
            infos["Date d’expiration"] = text_lines[14].strip()
            infos["Adresse"] = text_lines[17].strip()
            infos["Numéro de carte"] = text_lines[6].strip()
    except Exception as e:
        infos["Erreur"] = str(e)

    return infos

# ------------------------------
# ⚙️ Fonction d'extraction intelligente des infos CNI verso
# ------------------------------
def extract_infos_verso(text_lines):
    infos = {
        "Code pays": "",
        "Numéro électeur": "",
        "Région": "",
        "Département": "",
        "Commune": "",
        "Lieu de vote": "",
        "NIN": "",
        "Bureau de vote": "Non disponible sur l'image"
    }

    try:
        if len(text_lines) > 15:
            infos["Code pays"] = text_lines[1].strip()
            infos["Numéro électeur"] = text_lines[3].strip()
            infos["Région"] = text_lines[6].strip()
            infos["Département"] = text_lines[7].strip()
            infos["Commune"] = text_lines[10].strip()
            infos["Lieu de vote"] = text_lines[13].strip()
            infos["NIN"] = text_lines[15].strip()
    except Exception as e:
        infos["Erreur"] = str(e)

    return infos

# ------------------------------
# 🎬 Interface principale Streamlit
# ------------------------------
st.set_page_config(page_title="Lecture CNI Sénégal", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .block-container {
        padding: 2rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background-color: #009999;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stFileUploader, .stRadio > div {
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Lecture intelligente de CNI sénégalaise")

st.sidebar.title("📌 Choisissez la face de la CNI")
mode = st.sidebar.radio("Sélectionnez une face", ["Recto", "Verso"])

upload_method = st.radio("📸 Choisissez la méthode de capture", ["Téléverser une image", "Utiliser la caméra"])

image = None
if upload_method == "Téléverser une image":
    uploaded_file = st.file_uploader("📤 Téléversez une image de la CNI", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
elif upload_method == "Utiliser la caméra":
    camera_file = st.camera_input("📷 Prenez une photo de la CNI")
    if camera_file:
        image = Image.open(camera_file).convert("RGB")

if image:
    st.image(image, caption="Image de la CNI", use_column_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        tmp_path = tmp_file.name

    reader = easyocr.Reader(['fr', 'en'])
    result = reader.readtext(tmp_path, detail=0, paragraph=False)
    os.remove(tmp_path)

    if mode == "Recto":
        extracted_data = extract_infos_recto(result)
        st.success("✅ Informations recto extraites avec succès !")
        st.json(extracted_data)
    else:
        extracted_data = extract_infos_verso(result)
        st.success("✅ Informations verso extraites avec succès !")
        st.json(extracted_data)

    st.subheader("📋 Données brutes OCR")
    st.code("\n".join(result))
