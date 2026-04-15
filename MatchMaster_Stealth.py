import streamlit as st
import random
import uuid
import io
import os
import zipfile
from PIL import Image
import piexif
from datetime import datetime, timedelta
import tempfile
from moviepy.editor import VideoFileClip, vfx

st.set_page_config(page_title="MatchMaster Stealth Bulk", page_icon="🚀")

st.title("🚀 MatchMaster Stealth : Photo & Vidéo")
st.write("Sélectionne tes médias et génère des versions uniques en masse pour tes comptes.")

# --- CONFIGURATION ---
uploaded_files = st.file_uploader("Sélectionne tes fichiers (JPG, PNG, MP4, MOV)", 
                                  type=["jpg", "jpeg", "png", "mp4", "mov", "avi"], 
                                  accept_multiple_files=True)
nb_copies = st.number_input("Nombre de copies uniques PAR média", min_value=1, max_value=50, value=10)

if uploaded_files and st.button("🔥 Lancer la génération massive"):
    total_items = len(uploaded_files) * nb_copies
    st.info(f"Préparation de {total_items} médias uniques...")
    
    zip_buffer = io.BytesIO()
    iphones = ["iPhone 13", "iPhone 14 Pro", "iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra"]
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        progress_bar = st.progress(0)
        counter = 0
        
        for original_file in uploaded_files:
            file_ext = os.path.splitext(original_file.name)[1].lower()
            base_name = os.path.splitext(original_file.name)[0]

            for i in range(1, nb_copies + 1):
                # --- TRAITEMENT PHOTO ---
                if file_ext in [".jpg", ".jpeg", ".png"]:
                    img_originale = Image.open(original_file).convert("RGB")
                    zoom = random.uniform(1.0, 1.01)
                    w, h = img_originale.size
                    img_final = img_originale.resize((int(w*zoom), int(h*zoom)), Image.Resampling.LANCZOS)
                    img_final = img_final.crop(((w*zoom-w)//2, (h*zoom-h)//2, (w*zoom+w)//2, (h*zoom+h)//2))

                    # Métadonnées
                    date_photo = datetime.now() - timedelta(days=random.randint(1, 90))
                    str_date = date_photo.strftime("%Y:%m:%d %H:%M:%S")
                    exif_dict = {"0th": {piexif.ImageIFD.Make: "Apple", piexif.ImageIFD.Model: random.choice(iphones), piexif.ImageIFD.DateTime: str_date},
                                 "Exif": {piexif.ExifIFD.DateTimeOriginal: str_date, piexif.ExifIFD.ImageUniqueID: str(uuid.uuid4())}}
                    exif_bytes = piexif.dump(exif_dict)

                    img_byte_arr = io.BytesIO()
                    img_final.save(img_byte_arr, format='JPEG', quality=98, exif=exif_bytes)
                    img_byte_arr.write(os.urandom(random.randint(50, 150))) # Change le Hash
                    zip_file.writestr(f"{base_name}_v{i:03d}.jpg", img_byte_arr.getvalue())

                # --- TRAITEMENT VIDÉO ---
                elif file_ext in [".mp4", ".mov", ".avi"]:
                    # On utilise un fichier temporaire pour MoviePy
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_input:
                        tmp_input.write(original_file.getvalue())
                        tmp_input_path = tmp_input.name

                    clip = VideoFileClip(tmp_input_path)
                    
                    # Léger zoom pour changer les pixels
                    zoom_factor = random.uniform(1.01, 1.03)
                    new_w, new_h = int(clip.w * zoom_factor), int(clip.h * zoom_factor)
                    # On redimensionne et on recoupe au centre
                    clip_resized = clip.resize(newsize=(new_w, new_h))
                    clip_final = clip_resized.crop(x_center=new_w/2, y_center=new_h/2, width=clip.w, height=clip.h)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_output:
                        tmp_output_path = tmp_output.name
                        # On baisse un peu le bitrate pour aller plus vite et changer le fichier
                        clip_final.write_videofile(tmp_output_path, codec="libx264", audio_codec="aac", bitrate="2000k", logger=None)
                    
                    with open(tmp_output_path, "rb") as f:
                        video_data = bytearray(f.read())
                        video_data.extend(os.urandom(random.randint(100, 300))) # Change le Hash
                        zip_file.writestr(f"{base_name}_v{i:03d}.mp4", bytes(video_data))
                    
                    # Nettoyage
                    clip.close()
                    os.unlink(tmp_input_path)
                    os.unlink(tmp_output_path)

                counter += 1
                progress_bar.progress(counter / total_items)

    st.success(f"✅ Terminé ! {total_items} fichiers traités.")
    st.download_button(label="📥 Télécharger le Pack Media (.zip)", 
                       data=zip_buffer.getvalue(), 
                       file_name=f"pack_stealth_{datetime.now().strftime('%d_%m')}.zip", 
                       mime="application/zip")
