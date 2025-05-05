import streamlit as st
import easyocr
import tempfile
import os
from PIL import Image

# ------------------------------
# ⚙️ Fonction d'extraction intelligente des infos CNI recto
# ------------------------------
def extract_infos(text_lines):
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
        # Mapping fixe basé sur la position des lignes OCR de la CNI
        if len(text_lines) > 17:
            infos["Prénom"] = text_lines[7].strip()
            infos["Nom"] = text_lines[8].strip()
            infos["Date de naissance"] = text_lines[9].strip()
            infos["Taille"] = text_lines[10].strip()
            infos["Centre d’enregistrement"] = text_lines[11].strip()
            infos["Date de délivrance"] = text_lines[13].strip()
            infos["Date d’expiration"] = text_lines[14].strip()
            infos["Adresse"] = text_lines[17].strip()

            # Numéro de carte (ligne 6 directement)
            infos["Numéro de carte"] = text_lines[6].strip()

    except Exception as e:
        infos["Erreur"] = str(e)

    return infos

# ------------------------------
# 🎬 Interface principale Streamlit
# ------------------------------
st.set_page_config(page_title="Lecture CNI Sénégal", layout="centered")
st.title("📄 Lecture intelligente de CNI sénégalaise - Recto")

uploaded_file = st.file_uploader("📤 Téléversez une image (CNI recto)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 🖼️ Affichage de l'image téléversée
    image = Image.open(uploaded_file).convert("RGB")  # Convertir pour éviter les erreurs JPEG
    st.image(image, caption="Image téléversée", use_column_width=True)

    # 💾 Sauvegarde temporaire de l'image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        tmp_path = tmp_file.name

    # 🔎 Lecture OCR
    reader = easyocr.Reader(['fr', 'en'])
    result = reader.readtext(tmp_path, detail=0, paragraph=False)

    # 🧹 Suppression du fichier temporaire
    os.remove(tmp_path)

    # 📤 Extraction intelligente des informations clés
    extracted_data = extract_infos(result)

    # ✅ Résultat structuré
    st.success("Informations extraites avec succès !")
    st.json(extracted_data)

    # 📋 Données brutes OCR pour vérification
    st.subheader("📋 Données brutes OCR")
    st.write(result)
