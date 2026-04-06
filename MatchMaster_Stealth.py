import streamlit as st
import random
import uuid
import io
import os
import zipfile
from PIL import Image
import piexif
from datetime import datetime, timedelta

st.set_page_config(page_title="MatchMaster Stealth Bulk", page_icon="🚀")

st.title("🚀 MatchMaster Stealth : Bulk Edition")
st.write("Sélectionne plusieurs photos et génère des versions uniques en masse.")

# --- INTERFACE DE CONFIGURATION ---
uploaded_files = st.file_uploader("Sélectionne tes photos (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
nb_copies = st.number_input("Nombre de copies uniques PAR photo", min_value=1, max_value=100, value=20)

if uploaded_files and st.button("🔥 Lancer la génération massive"):
    total_photos = len(uploaded_files) * nb_copies
    st.info(f"Préparation de {total_photos} photos uniques ({len(uploaded_files)} originales x {nb_copies} copies)...")
    
    # Création du buffer pour le fichier ZIP final
    zip_buffer = io.BytesIO()
    iphones = ["iPhone 13", "iPhone 14 Pro", "iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra", "Pixel 8 Pro"]
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        overall_progress = st.progress(0)
        counter = 0
        
        for original_file in uploaded_files:
            # On ouvre l'image originale une seule fois pour économiser le processeur du VPS
            img_originale = Image.open(original_file).convert("RGB")
            base_name = os.path.splitext(original_file.name)[0]
            
            for i in range(1, nb_copies + 1):
                # 1. Micro-zoom (Anti-IA faciale)
                zoom = random.uniform(1.0, 1.015)
                w, h = img_originale.size
                img_temp = img_originale.resize((int(w*zoom), int(h*zoom)), Image.Resampling.LANCZOS)
                img_final = img_temp.crop(((w*zoom-w)//2, (h*zoom-h)//2, (w*zoom+w)//2, (h*zoom+h)//2))

                # 2. Métadonnées uniques (Dates aléatoires sur 3 mois)
                date_photo = datetime.now() - timedelta(days=random.randint(1, 90), seconds=random.randint(0, 86400))
                str_date = date_photo.strftime("%Y:%m:%d %H:%M:%S")
                
                exif_dict = {"0th": {piexif.ImageIFD.Make: "Apple", 
                                     piexif.ImageIFD.Model: random.choice(iphones),
                                     piexif.ImageIFD.DateTime: str_date},
                             "Exif": {piexif.ExifIFD.DateTimeOriginal: str_date,
                                      piexif.ExifIFD.ImageUniqueID: str(uuid.uuid4())}}
                
                exif_bytes = piexif.dump(exif_dict)
                
                # 3. Sauvegarde en mémoire vive
                img_byte_arr = io.BytesIO()
                img_final.save(img_byte_arr, format='JPEG', quality=100, subsampling=0, exif=exif_bytes)
                
                # 4. Injection de "Junk Data" (Modification du Hash binaire)
                img_byte_arr.write(os.urandom(random.randint(50, 200)))
                
                # 5. Ajout au pack ZIP avec un nom clair
                file_name_in_zip = f"{base_name}_v{i:03d}.jpg"
                zip_file.writestr(file_name_in_zip, img_byte_arr.getvalue())
                
                # Mise à jour de la barre de progression
                counter += 1
                overall_progress.progress(counter / total_photos)

    st.success(f"✅ Terminé ! {total_photos} fichiers générés avec succès.")
    
    # Bouton de téléchargement du pack complet
    st.download_button(
        label="📥 Télécharger le Pack Bulk (.zip)",
        data=zip_buffer.getvalue(),
        file_name=f"pack_dating_{datetime.now().strftime('%d_%m')}.zip",
        mime="application/zip"
    )