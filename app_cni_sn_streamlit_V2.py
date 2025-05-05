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
        "Bureau de vote": ""
    }

    try:
        for line in text_lines:
            upper_line = line.upper()
            if "CODE PAYS" in upper_line:
                infos["Code pays"] = line.split(":")[-1].strip()
            elif "NUMERO ELECTEUR" in upper_line:
                infos["Numéro électeur"] = line.split(":")[-1].strip()
            elif "REGION" in upper_line:
                infos["Région"] = line.split(":")[-1].strip()
            elif "DEPARTEMENT" in upper_line:
                infos["Département"] = line.split(":")[-1].strip()
            elif "COMMUNE" in upper_line:
                infos["Commune"] = line.split(":")[-1].strip()
            elif "LIEU DE VOTE" in upper_line:
                infos["Lieu de vote"] = line.split(":")[-1].strip()
            elif "BUREAU DE VOTE" in upper_line:
                infos["Bureau de vote"] = line.split(":")[-1].strip()
            elif "NIN" in upper_line:
                infos["NIN"] = line.split()[-1].strip()
    except Exception as e:
        infos["Erreur"] = str(e)

    return infos

# ------------------------------
# 🎬 Interface principale Streamlit
# ------------------------------
st.set_page_config(page_title="Lecture CNI Sénégal", layout="centered")
st.title("📄 Lecture intelligente de CNI sénégalaise")

st.sidebar.title("📌 Choisissez la face de la CNI")
mode = st.sidebar.radio("Sélectionnez une face", ["Recto", "Verso"])

uploaded_file = st.file_uploader("📤 Téléversez une image de la CNI", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Image téléversée", use_column_width=True)

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
    st.write(result)
