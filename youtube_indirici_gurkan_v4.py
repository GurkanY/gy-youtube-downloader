import customtkinter as ctk
import yt_dlp
import os
import sys
import time
import json
import threading
from tkinter import filedialog
from PIL import Image, ImageTk
import hashlib # Yeni eklendi: Token hashing için

# -------------------------------------------------------------------------------------
# Bu kod Gürkan Yılmaz tarafından geliştirilmiştir.
# Tüm hakları saklıdır.
# Geliştirici İletişim: gurkanyilmaz.k@gmail.com (İsteğe bağlı, kendi e-posta adresinizi yazabilirsiniz)
# Son Güncelleme: 3 Haziran 2025
# -------------------------------------------------------------------------------------

# Renk Paleti Tanımları
# Temaya göre değişecek renkler için fonksiyonlar veya dictionaries kullanalım
def get_colors():
    if ctk.get_appearance_mode() == "Dark":
        return {
            "PRIMARY_BLUE": "#2196F3",  # Parlak Mavi (Aksiyon butonları, vurgular)
            "DARK_GREY": "#424242",     # Koyu Gri (Kartlar, paneller)
            "NAVY_GREY": "#263238",     # Koyu Lacivert Gri (Genel arka plan)
            "VIBRANT_PINK": "#FF4081",  # Canlı Pembe (Buton ikonları, vurgu)
            "LIGHT_GREY": "#E0E0E0",    # Açık Gri (Metin)
            "TEXT_COLOR_DISABLED": "gray" # Devre dışı metin rengi
        }
    else: # Light Mode
        return {
            "PRIMARY_BLUE": "#1976D2",  # Koyu Mavi (Aksiyon butonları, vurgular)
            "DARK_GREY": "#F5F5F5",     # Açık Gri (Kartlar, paneller)
            "NAVY_GREY": "#FFFFFF",     # Beyaz (Genel arka plan)
            "VIBRANT_PINK": "#E91E63",  # Koyu Pembe (Buton ikonları, vurgu)
            "LIGHT_GREY": "#212121",    # Koyu Gri (Metin)
            "TEXT_COLOR_DISABLED": "#9E9E9E" # Devre dışı metin rengi
        }

DOWNLOAD_HISTORY_FILE = "download_history.json"
TOKEN_FILE = "tokens.txt" # Token listesini içeren dosya
CONFIG_FILE = "config.json" # Yeni: Uygulama ayarlarını ve kalıcı token'ı saklamak için
APP_VERSION = "2.6.2" # Sürüm numarasını güncelledik (Alttaki Bilgi ve Yeni Özellikler)

# CustomTkinter varsayılan görünüm ayarları
ctk.set_appearance_mode("Dark")  # Uygulama temasını varsayılan olarak Koyu yapalım
ctk.set_default_color_theme("blue") # Varsayılan renk temasını mavi olarak ayarlar

class YoutubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Token doğrulamasını uygulamanın en başında yap
        # İlk olarak kayıtlı bir token olup olmadığını kontrol et
        if not self.check_persistent_token():
            # Kayıtlı token yoksa veya geçersizse, token diyalogunu göster
            token_status, entered_hashed_token = self.show_token_dialog()
            if token_status == "success":
                self.save_persistent_token(entered_hashed_token) # Başarılıysa token'ı kaydet
            else:
                self.destroy() # Uygulamayı kapat
                sys.exit("Token doğrulama başarısız veya iptal edildi. Uygulama kapatıldı.")

        self.title(f"Gürkan Yılmaz YouTube İndirici v{APP_VERSION}")
        self.minsize(900, 750) # Minimum boyut belirleyelim

        # Ana pencere arka plan rengini ayarla - get_colors() ile dinamik hale getirdik
        self.configure(fg_color=get_colors()["NAVY_GREY"])

        # Grid layout için sütun ve satır ağırlıklarını yapılandır
        # Ana pencerenin boyutlandırmasını tamamen yönetelim
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Ana çerçeve tüm pencereyi kaplasın
        self.grid_rowconfigure(1, weight=0) # Alt bilgi çerçevesi için

        # Ana çerçeve oluşturma (genel arka plan renginde)
        self.main_frame = ctk.CTkFrame(self, fg_color=get_colors()["NAVY_GREY"], corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1) # İçindeki tek sütun
        # Ana çerçeve içindeki satırların ağırlıklarını ayarlayalım
        self.main_frame.grid_rowconfigure(0, weight=0) # Header sabit kalsın
        self.main_frame.grid_rowconfigure(1, weight=1) # Content frame genişlesin

        # Durum Mesajı Kutusu (En başta oluşturulmalı ki log_status çağrıları çalışsın)
        self.status_textbox = ctk.CTkTextbox(self.main_frame, height=150, wrap="word", font=ctk.CTkFont(size=13),
                                             fg_color=get_colors()["NAVY_GREY"], text_color=get_colors()["LIGHT_GREY"],
                                             corner_radius=10, border_width=2, border_color=get_colors()["PRIMARY_BLUE"])
        self.status_textbox.insert("end", "Program hazır. URL yapıştırın ve indirme türünü seçin.")
        self.status_textbox.configure(state="disabled")

        # **IMPORTANT**: Define methods BEFORE calling setup_widgets if they are referenced
        # This is already the case, but explicit binding might help a very specific tkinter quirk.
        # This line is primarily for demonstration; your original code structure should be fine.
        self.update_quality_options_bound = self.update_quality_options


        self.setup_widgets()

        # Alt Bilgi Çerçevesi (Footer)
        self.footer_frame = ctk.CTkFrame(self, fg_color=get_colors()["NAVY_GREY"], height=40, corner_radius=0)
        self.footer_frame.grid(row=1, column=0, sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1)
        
        self.powered_by_label = ctk.CTkLabel(self.footer_frame, text=f"Powered By GurkanY | Sürüm: {APP_VERSION}",
                                             font=ctk.CTkFont(size=12), text_color=get_colors()["LIGHT_GREY"])
        self.powered_by_label.grid(row=0, column=0, pady=5, sticky="e", padx=20)


        # Geçmişi yükle
        self.history = self.load_history()

    # --- Token Sistemi Metodları ---
    def load_tokens(self, file_path=TOKEN_FILE):
        """Token'ları dosyadan yükler ve hash'ler."""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                # Her satırı oku, boşlukları temizle ve hashle
                return [hashlib.sha256(line.strip().encode('utf-8')).hexdigest() for line in f if line.strip()]
        return []

    def verify_token(self, entered_token, valid_token_hashes):
        """Girilen token'ı doğrular."""
        entered_token_hash = hashlib.sha256(entered_token.strip().encode('utf-8')).hexdigest()
        return entered_token_hash in valid_token_hashes

    def generate_token(self, data):
        """Veriden bir token üretir (SHA256 hash). Bu sadece token üretmek için bir yardımcı fonksiyondur."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def load_config(self):
        """Yapılandırma dosyasını yükler."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.log_status("Uyarı: Yapılandırma dosyası bozuk veya geçersiz. Yeni bir dosya oluşturulacak.")
                return {}
        return {}

    def save_config(self, config_data):
        """Yapılandırma dosyasını kaydeder."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

    def check_persistent_token(self):
        """Kalıcı olarak kaydedilmiş token'ı kontrol eder."""
        config = self.load_config()
        persisted_hashed_token = config.get("hashed_token")
        
        if persisted_hashed_token:
            valid_token_hashes = self.load_tokens()
            # Kaydedilen hash'in geçerli token'lar arasında olup olmadığını kontrol et
            if persisted_hashed_token in valid_token_hashes:
                self.log_status("Kayıtlı lisans anahtarı başarıyla doğrulandı. Uygulama başlatılıyor.")
                return True
            else:
                self.log_status("Kayıtlı lisans anahtarı geçersiz veya süresi dolmuş. Lütfen yeni bir anahtar girin.")
                return False
        return False

    def save_persistent_token(self, hashed_token):
        """Başarılı token'ı yapılandırma dosyasına kaydeder."""
        config = self.load_config()
        config["hashed_token"] = hashed_token
        self.save_config(config)
        self.log_status("Lisans anahtarı kaydedildi.")

    def show_token_dialog(self):
        """Token girişi için bir CustomTkinter diyalog penceresi gösterir."""
        colors = get_colors()

        dialog = ctk.CTkToplevel(self)
        dialog.title("Lisans Doğrulama")
        dialog.geometry("400x200")
        dialog.transient(self) # Ana pencerenin üzerinde kalmasını sağlar
        dialog.grab_set() # Ana pencereyi etkileşim dışı bırakır

        dialog.configure(fg_color=colors["NAVY_GREY"])
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure((0,1,2,3), weight=1)

        ctk.CTkLabel(dialog, text="Lütfen Lisans Anahtarınızı Girin:", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["LIGHT_GREY"]).pack(pady=10)
        license_entry = ctk.CTkEntry(dialog, width=300, height=40, font=ctk.CTkFont(size=14),
                                     fg_color=colors["DARK_GREY"], text_color=colors["LIGHT_GREY"],
                                     border_color=colors["PRIMARY_BLUE"], corner_radius=10, border_width=2)
        license_entry.pack(pady=5)

        result_var = ctk.StringVar() # Sonucu saklamak için
        result_var.set("pending") # Varsayılan durum
        entered_hashed_token = None # Başarılı token'ın hash'ini tutacak

        status_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="red")
        status_label.pack(pady=5)

        def verify_and_close():
            nonlocal entered_hashed_token # Dış kapsamdaki değişkeni değiştirmek için
            entered_key = license_entry.get().strip()
            valid_token_hashes = self.load_tokens()
            if self.verify_token(entered_key, valid_token_hashes):
                entered_hashed_token = hashlib.sha256(entered_key.encode('utf-8')).hexdigest()
                result_var.set("success")
                dialog.destroy()
            else:
                result_var.set("failure")
                status_label.configure(text="Geçersiz Lisans Anahtarı!")
                # İsterseniz burada deneme hakkı, bekletme vb. ekleyebilirsiniz.

        verify_button = ctk.CTkButton(dialog, text="Doğrula", command=verify_and_close, font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], corner_radius=10, height=40)
        verify_button.pack(pady=10)

        # Pencere kapatma protokolünü ayarla (kullanıcı çarpıya basarsa)
        dialog.protocol("WM_DELETE_WINDOW", lambda: result_var.set("closed") or dialog.destroy())

        self.wait_window(dialog) # Diyalog kapanana kadar ana uygulamayı beklet
        return result_var.get(), entered_hashed_token
    # --- Token Sistemi Metodları Sonu ---


    def setup_widgets(self):
        colors = get_colors() # Mevcut tema renklerini al

        # Logo ve Başlık Alanı
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["NAVY_GREY"])
        self.header_frame.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0) # Tema butonu için

        # LOGO YÜKLEME
        self.app_logo = None
        icon_path_ico = os.path.join(os.path.dirname(__file__), "my_app_icon.ico")
        icon_path_png = os.path.join(os.path.dirname(__file__), "my_app_icon.png")

        try:
            if os.path.exists(icon_path_ico):
                original_image = Image.open(icon_path_ico)
                resized_image = original_image.resize((100, 100), Image.LANCZOS)
                self.app_logo = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(100, 100))
                self.log_status("my_app_icon.ico başarıyla yüklendi.")
            elif os.path.exists(icon_path_png):
                self.app_logo = ctk.CTkImage(light_image=Image.open(icon_path_png),
                                             dark_image=Image.open(icon_path_png),
                                             size=(100, 100))
                self.log_status("my_app_icon.png başarıyla yüklendi.")
            else:
                self.log_status("Uyarı: 'my_app_icon.ico' veya 'my_app_icon.png' bulunamadı. Varsayılan metin logosu kullanılacak.")
        except Exception as e:
            self.log_status(f"Hata: İkon yüklenirken bir sorun oluştu: {e}. Varsayılan metin logosu kullanılacak.")
            self.app_logo = None

        if self.app_logo:
            self.logo_display_label = ctk.CTkLabel(self.header_frame, image=self.app_logo, text="")
            self.logo_display_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 5), sticky="n") # Ortaya hizala
        else:
            self.logo_label = ctk.CTkLabel(self.header_frame, text="⬇️▶️", font=ctk.CTkFont(size=60, weight="bold"), text_color=colors["PRIMARY_BLUE"])
            self.logo_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 5), sticky="n")

        # signature_label kaldırıldı veya başka bir yere taşındı
        # self.signature_label = ctk.CTkLabel(self.header_frame, text=f"Hazırlayan: Gürkan YILMAZ | Sürüm: {APP_VERSION}", font=ctk.CTkFont(size=15), text_color=colors["LIGHT_GREY"])
        # self.signature_label.grid(row=1, column=0, padx=(0, 0), pady=(0, 20), sticky="n")

        # Tema Değiştirme Butonu
        self.theme_mode_button = ctk.CTkButton(self.header_frame, text="💡 Tema Değiştir", command=self.change_appearance_mode, font=ctk.CTkFont(size=13, weight="bold"),
                                                fg_color=colors["DARK_GREY"], hover_color=colors["PRIMARY_BLUE"], corner_radius=8, height=35)
        self.theme_mode_button.grid(row=0, column=1, padx=(0, 20), pady=(10, 0), sticky="ne")


        # Ana İçerik Çerçevesi (Koyu Gri Panel - Kart görünümü)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["DARK_GREY"], corner_radius=18)
        self.content_frame.grid(row=1, column=0, padx=40, pady=(0, 40), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1) # İçindeki tek sütun
        # Content frame içindeki satırların ağırlıklarını ayarlayalım
        self.content_frame.grid_rowconfigure(0, weight=0) # URL
        self.content_frame.grid_rowconfigure(1, weight=0) # Download Type
        self.content_frame.grid_rowconfigure(2, weight=0) # Quality Options
        self.content_frame.grid_rowconfigure(3, weight=0) # Output Folder
        self.content_frame.grid_rowconfigure(4, weight=0) # Action Buttons
        self.content_frame.grid_rowconfigure(5, weight=0) # Progress
        self.content_frame.grid_rowconfigure(6, weight=0) # Status Label
        self.content_frame.grid_rowconfigure(7, weight=1) # Status Textbox genişlesin
        self.content_frame.grid_rowconfigure(8, weight=0) # FFmpeg Warning

        # URL Girişi Bölümü
        self.url_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.url_section_frame.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        self.url_section_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.url_section_frame, text="YouTube URL'si:", font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["LIGHT_GREY"]).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.url_entry = ctk.CTkEntry(self.url_section_frame, height=45, placeholder_text="Video veya Playlist URL'sini buraya yapıştırın", font=ctk.CTkFont(size=15),
                                      fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"], corner_radius=10, border_width=2)
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15))


        # İndirme Türü Seçimi Bölümü
        self.download_type_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.download_type_section_frame.grid(row=1, column=0, padx=30, pady=(15, 20), sticky="ew")
        self.download_type_section_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(self.download_type_section_frame, text="İndirme Türü:", font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["LIGHT_GREY"]).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.download_type_var = ctk.StringVar(value="mp4") # Varsayılan: MP4
        self.mp4_radio = ctk.CTkRadioButton(self.download_type_section_frame, text="MP4 Video", variable=self.download_type_var, value="mp4", font=ctk.CTkFont(size=14), text_color=colors["LIGHT_GREY"], fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], border_width_checked=4, border_width_unchecked=2, corner_radius=10, command=self.update_quality_options_bound)
        self.mp4_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.mp3_radio = ctk.CTkRadioButton(self.download_type_section_frame, text="MP3 Ses", variable=self.download_type_var, value="mp3", font=ctk.CTkFont(size=14), text_color=colors["LIGHT_GREY"], fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], border_width_checked=4, border_width_unchecked=2, corner_radius=10, command=self.update_quality_options_bound)
        self.mp3_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.playlist_mp3_radio = ctk.CTkRadioButton(self.download_type_section_frame, text="Playlist MP3", variable=self.download_type_var, value="playlist_mp3", font=ctk.CTkFont(size=14), text_color=colors["LIGHT_GREY"], fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], border_width_checked=4, border_width_unchecked=2, corner_radius=10, command=self.update_quality_options_bound)
        self.playlist_mp3_radio.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Kalite Seçenekleri Bölümü (Yeni)
        self.quality_options_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.quality_options_frame.grid(row=2, column=0, padx=30, pady=(10, 15), sticky="ew")
        self.quality_options_frame.grid_columnconfigure(0, weight=1)
        self.quality_options_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.quality_options_frame, text="Kalite Seçenekleri:", font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["LIGHT_GREY"]).grid(row=0, column=0, sticky="w", pady=(0, 8), columnspan=2)

        # Video Kalitesi ComboBox
        self.video_quality_label = ctk.CTkLabel(self.quality_options_frame, text="Video Çözünürlüğü:", font=ctk.CTkFont(size=14), text_color=colors["LIGHT_GREY"])
        self.video_quality_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.video_quality_combobox = ctk.CTkComboBox(self.quality_options_frame, values=["Auto"], font=ctk.CTkFont(size=13),
                                                      fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"], corner_radius=8, height=35)
        self.video_quality_combobox.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.video_quality_combobox.set("Auto") # Varsayılan
        self.video_quality_combobox.configure(state="disabled") # Başlangıçta devre dışı

        # Ses Kalitesi ComboBox
        self.audio_quality_label = ctk.CTkLabel(self.quality_options_frame, text="MP3 Bitrate:", font=ctk.CTkFont(size=14), text_color=colors["LIGHT_GREY"])
        self.audio_quality_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.audio_quality_combobox = ctk.CTkComboBox(self.quality_options_frame, values=["320kbps", "256kbps", "192kbps", "128kbps"], font=ctk.CTkFont(size=13),
                                                      fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"], corner_radius=8, height=35)
        self.audio_quality_combobox.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.audio_quality_combobox.set("320kbps") # Varsayılan
        self.audio_quality_combobox.configure(state="disabled") # Başlangıçta devre dışı


        # Çıktı Klasörü Seçimi Bölümü (row 3'e kaydı)
        self.output_folder_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.output_folder_section_frame.grid(row=3, column=0, padx=30, pady=(15, 20), sticky="ew")
        self.output_folder_section_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.output_folder_section_frame, text="Kaydedilecek Klasör:", font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["LIGHT_GREY"]).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.output_folder_entry = ctk.CTkEntry(self.output_folder_section_frame, height=45, placeholder_text="Varsayılan: indirilen_icerikler", font=ctk.CTkFont(size=14),
                                                fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"], corner_radius=10, border_width=2)
        self.output_folder_entry.grid(row=1, column=0, sticky="ew", padx=(0, 15))
        self.output_folder_entry.insert(0, os.path.abspath("indirilen_icerikler"))

        self.browse_button = ctk.CTkButton(self.output_folder_section_frame, text="Klasör Seç", command=self.browse_folder, font=ctk.CTkFont(size=14, weight="bold"),
                                           fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], corner_radius=10, height=45)
        self.browse_button.grid(row=1, column=1, sticky="e")

        # Aksiyon Butonları Bölümü (row 4'e kaydı)
        self.action_buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_buttons_frame.grid(row=4, column=0, padx=30, pady=(20, 25), sticky="ew")
        self.action_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.download_button = ctk.CTkButton(self.action_buttons_frame, text="⬇️ İndir", command=self.start_download_thread, font=ctk.CTkFont(size=17, weight="bold"), height=50,
                                             fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], corner_radius=12)
        self.download_button.grid(row=0, column=0, padx=(0, 15), pady=0, sticky="ew")

        self.bulk_download_button = ctk.CTkButton(self.action_buttons_frame, text="📋 Toplu İndir", command=self.start_bulk_download_thread, font=ctk.CTkFont(size=17, weight="bold"), height=50,
                                                  fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], corner_radius=12)
        self.bulk_download_button.grid(row=0, column=1, padx=15, pady=0, sticky="ew")

        self.history_button = ctk.CTkButton(self.action_buttons_frame, text="🕒 Geçmiş", command=self.show_history_window, font=ctk.CTkFont(size=17, weight="bold"), height=50,
                                            fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], corner_radius=12)
        self.history_button.grid(row=0, column=2, padx=(15, 0), pady=0, sticky="ew")

        # İlerleme Çubuğu ve Kontrol Butonu Bölümü (row 5'e kaydı)
        self.progress_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.progress_section_frame.grid(row=5, column=0, padx=30, pady=(15, 20), sticky="ew")
        self.progress_section_frame.grid_columnconfigure(0, weight=1)
        self.progress_section_frame.grid_columnconfigure(1, weight=0)

        self.progress_text_label = ctk.CTkLabel(self.progress_section_frame, text="İndirme İlerlemesi: %0", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["LIGHT_GREY"])
        self.progress_text_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self.progress_section_frame, orientation="horizontal", progress_color=colors["PRIMARY_BLUE"], height=20, corner_radius=10)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=(0, 15))

        self.control_button = ctk.CTkButton(self.progress_section_frame, text="⏸️", font=ctk.CTkFont(size=24, weight="bold"), width=50, height=50, corner_radius=999,
                                            fg_color="transparent", text_color=colors["VIBRANT_PINK"], hover_color=colors["DARK_GREY"], border_width=3, border_color=colors["VIBRANT_PINK"],
                                            command=self.toggle_download_pause)
        self.control_button.grid(row=0, column=1, rowspan=2, sticky="e")
        self.control_button.configure(state="disabled")

        # Durum Mesajı Kutusu (row 6'ya kaydı)
        self.status_label = ctk.CTkLabel(self.content_frame, text="Durum Mesajları:", font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["LIGHT_GREY"])
        self.status_label.grid(row=6, column=0, padx=30, pady=(20, 10), sticky="w")
        # self.status_textbox zaten __init__ içinde oluşturuldu, şimdi grid'e yerleştiriyoruz
        self.status_textbox.grid(row=7, column=0, padx=30, pady=(0, 20), sticky="nsew")

        # FFmpeg Uyarısı (row 8'e kaydı)
        self.ffmpeg_warning_label = ctk.CTkLabel(self.content_frame, text="ℹ️ MP3/Video dönüştürme için FFmpeg gereklidir ve PATH'inize eklenmelidir!", font=ctk.CTkFont(size=13, weight="bold"), text_color="orange")
        self.ffmpeg_warning_label.grid(row=8, column=0, padx=30, pady=(0, 30), sticky="ew")

        self.is_download_paused = False # İndirme duraklatma durumu

        # Başlangıçta kalite seçeneklerini güncelle
        self.update_quality_options()


    def change_appearance_mode(self):
        """Uygulama temasını Açık/Koyu arasında değiştirir ve özel renkleri günceller."""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_mode_button.configure(text="🌙 Tema Değiştir")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_mode_button.configure(text="💡 Tema Değiştir")

        # Widget'ların renklerini güncelleyelim
        self.update_widget_colors()

    def update_widget_colors(self):
        """Tüm widget'ların renklerini mevcut temaya göre günceller."""
        colors = get_colors()

        # Ana pencere ve ana çerçeve
        self.configure(fg_color=colors["NAVY_GREY"])
        self.main_frame.configure(fg_color=colors["NAVY_GREY"])
        self.footer_frame.configure(fg_color=colors["NAVY_GREY"]) # Footer rengini de güncelle
        self.powered_by_label.configure(text_color=colors["LIGHT_GREY"]) # Footer text rengini güncelle

        # Header ve logo
        self.header_frame.configure(fg_color=colors["NAVY_GREY"])
        if hasattr(self, 'logo_label'): # Metin logo kullanılıyorsa
            self.logo_label.configure(text_color=colors["PRIMARY_BLUE"])
        self.theme_mode_button.configure(fg_color=colors["DARK_GREY"], hover_color=colors["PRIMARY_BLUE"])

        # İçerik çerçevesi
        self.content_frame.configure(fg_color=colors["DARK_GREY"])

        # URL bölümü
        self.url_section_frame.configure(fg_color="transparent")
        # CTkLabel'ların .children ile erişimi için güvenlik kontrolü ekleyelim
        if '!ctklabel' in self.url_section_frame.children:
            self.url_section_frame.children['!ctklabel'].configure(text_color=colors["LIGHT_GREY"]) # URL Label
        self.url_entry.configure(fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"])

        # İndirme türü bölümü
        self.download_type_section_frame.configure(fg_color="transparent")
        if '!ctklabel' in self.download_type_section_frame.children:
            self.download_type_section_frame.children['!ctklabel'].configure(text_color=colors["LIGHT_GREY"]) # İndirme Türü Label
        self.mp4_radio.configure(text_color=colors["LIGHT_GREY"], fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])
        self.mp3_radio.configure(text_color=colors["LIGHT_GREY"], fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])
        self.playlist_mp3_radio.configure(text_color=colors["LIGHT_GREY"], fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])

        # Kalite seçenekleri bölümü
        self.quality_options_frame.configure(fg_color="transparent")
        if '!ctklabel' in self.quality_options_frame.children:
            self.quality_options_frame.children['!ctklabel'].configure(text_color=colors["LIGHT_GREY"]) # Kalite Seçenekleri Label
        self.video_quality_combobox.configure(fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"])
        self.audio_quality_combobox.configure(fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"])
        self.update_quality_options() # Renkleri doğru atamak için tekrar çağır

        # Çıktı klasörü bölümü
        self.output_folder_section_frame.configure(fg_color="transparent")
        if '!ctklabel' in self.output_folder_section_frame.children:
            self.output_folder_section_frame.children['!ctklabel'].configure(text_color=colors["LIGHT_GREY"]) # Kaydedilecek Klasör Label
        self.output_folder_entry.configure(fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"])
        self.browse_button.configure(fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])

        # Aksiyon butonları
        self.action_buttons_frame.configure(fg_color="transparent")
        self.download_button.configure(fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])
        self.bulk_download_button.configure(fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])
        self.history_button.configure(fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"])

        # İlerleme bölümü
        self.progress_section_frame.configure(fg_color="transparent")
        self.progress_text_label.configure(text_color=colors["LIGHT_GREY"])
        self.progress_bar.configure(progress_color=colors["PRIMARY_BLUE"])
        self.control_button.configure(text_color=colors["VIBRANT_PINK"], hover_color=colors["DARK_GREY"], border_color=colors["VIBRANT_PINK"])

        # Durum mesajları ve FFmpeg uyarısı
        self.status_label.configure(text_color=colors["LIGHT_GREY"])
        self.status_textbox.configure(fg_color=colors["NAVY_GREY"], text_color=colors["LIGHT_GREY"], border_color=colors["PRIMARY_BLUE"])


    def browse_folder(self):
        """Kullanıcının klasör seçmesini sağlar."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_entry.delete(0, ctk.END)
            self.output_folder_entry.insert(0, folder_selected)

    def log_status(self, message):
        """Durum kutusuna mesaj yazar ve en alta kaydırır."""
        if hasattr(self, 'status_textbox') and self.status_textbox:
            self.status_textbox.configure(state="normal")
            self.status_textbox.insert("end", "\n" + message)
            self.status_textbox.see("end")
            self.status_textbox.configure(state="disabled")
        else:
            print(message)


    def load_history(self):
        """İndirme geçmişini dosyadan yükler."""
        if os.path.exists(DOWNLOAD_HISTORY_FILE):
            try:
                with open(DOWNLOAD_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.log_status("Hata: İndirme geçmişi dosyası bozuk. Yeni bir geçmiş dosyası oluşturulacak.")
                return []
        return []

    def save_history(self):
        """İndirme geçmişini dosyaya kaydeder."""
        with open(DOWNLOAD_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def add_to_history(self, url, download_type, output_folder, title="Bilinmeyen Başlık"):
        """İndirilen öğeyi geçmişe ekler."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "url": url,
            "type": download_type,
            "output_folder": output_folder,
            "title": title,
            "timestamp": timestamp
        })
        self.save_history()

    def toggle_download_pause(self):
        """İndirme işlemini duraklatır/devam ettirir."""
        self.is_download_paused = not self.is_download_paused
        if self.is_download_paused:
            self.control_button.configure(text="▶️")
            self.log_status("İndirme duraklatıldı (UI temsili). Gerçek duraklatma için indirme iptal edilmeli.")
        else:
            self.control_button.configure(text="⏸️")
            self.log_status("İndirme devam ettiriliyor (UI temsili).")

    def start_download_thread(self):
        """UI'ı dondurmadan indirme işlemini ayrı bir thread'de başlatır."""
        url = self.url_entry.get().strip()
        download_type = self.download_type_var.get()
        output_folder = self.output_folder_entry.get().strip()
        video_quality = self.video_quality_combobox.get()
        audio_quality = self.audio_quality_combobox.get()


        if not url:
            self.log_status("Hata: Lütfen bir YouTube URL'si girin.")
            return
        if not output_folder:
            self.log_status("Hata: Lütfen bir çıktı klasörü seçin veya varsayılanı kullanın.")
            return

        self.log_status("İndirme başlatılıyor...")
        self.progress_bar.set(0)
        self.progress_text_label.configure(text="İndirme İlerlemesi: %0")
        self.control_button.configure(state="normal")
        self.control_button.configure(text="⏸️")

        self._set_ui_state("disabled")

        download_thread = threading.Thread(target=self._perform_download, args=(url, download_type, output_folder, video_quality, audio_quality))
        download_thread.start()

    def _perform_download(self, url, download_type, output_folder, video_quality, audio_quality, is_from_history=False):
        """Gerçek indirme mantığı."""
        try:
            absolute_output_path = os.path.abspath(output_folder)
            if not os.path.exists(absolute_output_path):
                os.makedirs(absolute_output_path)
                self.log_status(f"Hedef klasör oluşturuldu: {absolute_output_path}")

            ydl_opts = {
                'outtmpl': os.path.join(absolute_output_path, '%(title)s.%(ext)s'),
                'ignoreerrors': True,
                'progress_hooks': [self.download_progress_hook],
                'quiet': True,
                'no_warnings': True,
                'external_downloader_args': ['-loglevel', 'error'],
            }

            video_title = "Bilinmeyen Başlık"
            try:
                with yt_dlp.YoutubeDL({'skip_download': True, 'quiet': True, 'no_warnings': True}) as info_ydl:
                    info = info_ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'Bilinmeyen Başlık')
                    if 'entries' in info:
                        if info.get('title'):
                            video_title = f"Playlist: {info['title']}"
                        elif info.get('entries') and info['entries'][0].get('title'):
                            video_title = f"Playlist: {info['entries'][0]['title']} (ve fazlası)"
            except Exception as e:
                self.log_status(f"Uyarı: Video başlığı alınamadı (URL kontrol edin): {e}")

            if download_type == "mp4":
                # Video kalitesini uygula
                if video_quality == "Auto":
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                else:
                    # 'mp4[height<=1080]' gibi format stringleri kullanılabilir
                    # Basitlik için sadece çözünürlük bazında format seçimi
                    ydl_opts['format'] = f'bestvideo[height<={video_quality.replace("p", "")}]+bestaudio/best[height<={video_quality.replace("p", "")}]'
                self.log_status(f"'{url}' adresindeki video indirilmeye başlanıyor (MP4 formatında, {video_quality} kalitede)...")
            elif download_type == "mp3" or download_type == "playlist_mp3":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality.replace("kbps", ""), # '320' gibi değer
                }]
                if download_type == "playlist_mp3":
                    ydl_opts['yes_playlist'] = True
                self.log_status(f"'{url}' adresindeki içerik indirilmeye başlanıyor (MP3 formatında, {audio_quality} kalitede)...")
            else:
                self.log_status("Geçersiz indirme türü.")
                return

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.log_status(f"✅ İndirme işlemi başarıyla tamamlandı! Dosya(lar) '{absolute_output_path}' klasörüne kaydedildi.")
            if not is_from_history:
                self.add_to_history(url, download_type, absolute_output_path, video_title)

        except yt_dlp.utils.DownloadError as de:
            self.log_status(f"⚠️ İndirme Hatası: {de}")
            self.log_status("Lütfen URL'nin doğru ve erişilebilir olduğundan emin olun.")
        except Exception as e:
            self.log_status(f"❌ Genel Hata oluştu: {e}")
            self.log_status(f"URL: {url}")
            self.log_status("İndirme işlemi sırasında bir sorun yaşandı. Lütfen aşağıdaki kontrolleri yapın:")
            self.log_status("  1. Girdiğiniz URL'nin **doğru ve erişilebilir** olduğundan emin olun.")
            self.log_status("  2. İnternet bağlantınızı kontrol edin.")
            self.log_status("  3. **FFmpeg'in yüklü ve sistem PATH'ine ekli olduğundan** emin olun.")
            self.log_status("  4. `yt-dlp` kütüphanesinin güncel olduğundan emin olun.")
        finally:
            self._set_ui_state("normal")
            self.progress_bar.set(0)
            self.progress_text_label.configure(text="İndirme İlerlemesi: %0")
            self.control_button.configure(state="disabled")


    def download_progress_hook(self, d):
        """yt-dlp'den gelen indirme ilerlemesini UI'ya yansıtır."""
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', 'N/A')
            e_str = d.get('_eta_str', 'N/A')
            s_str = d.get('_speed_str', 'N/A')
            
            progress_percent = 0
            if d.get('total_bytes') and d.get('downloaded_bytes'):
                progress_percent = d['downloaded_bytes'] / d['total_bytes']
            elif d.get('total_bytes_estimate') and d.get('downloaded_bytes'):
                progress_percent = d['downloaded_bytes'] / d['total_bytes_estimate']
            
            self.progress_bar.set(progress_percent)
            self.progress_text_label.configure(text=f"İndirme İlerlemesi: {p_str}")
            
            self.log_status(f"⏳ İndiriliyor: {p_str} | {e_str} kalan | {s_str} hızında")
        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.progress_text_label.configure(text="İndirme İlerlemesi: %100 Tamamlandı!")
            self.log_status("🚀 İndirme tamamlandı, dönüştürme kontrol ediliyor...")
        elif d['status'] == 'error':
            self.log_status(f"❌ İndirme sırasında hata: {d.get('error', 'Bilinmeyen hata')}")


    def start_bulk_download_thread(self):
        """Toplu indirme işlemini ayrı bir thread'de başlatır."""
        output_folder = self.output_folder_entry.get().strip()
        if not output_folder:
            self.log_status("Hata: Lütfen bir çıktı klasörü seçin veya varsayılanı kullanın.")
            return

        file_path = filedialog.askopenfilename(
            title="URL'leri içeren .txt dosyasını seçin",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            self.log_status("TXT dosyası seçilmedi. Toplu indirme iptal edildi.")
            return

        self.log_status(f"'{file_path}' dosyasındaki URL'ler okunuyor...")
        urls_to_download = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and (url.startswith("http://") or url.startswith("https://")):
                        urls_to_download.append(url)
        except Exception as e:
            self.log_status(f"Hata: Dosya okunurken bir sorun oluştu: {e}")
            return

        if not urls_to_download:
            self.log_status("Seçilen dosyada indirilecek geçerli URL bulunamadı.")
            return

        self.show_bulk_download_type_dialog(urls_to_download, output_folder)


    def show_bulk_download_type_dialog(self, urls, output_folder):
        """Toplu indirme türü seçimi için CustomTkinter InputDialog kullanır."""
        dialog = ctk.CTkInputDialog(text="Toplu indirme türünü seçin:\n1: MP3\n2: MP4 Video\n(İptal için boş bırakın)", title="Toplu İndirme Türü")
        choice = dialog.get_input()

        if choice == '1':
            download_type = "mp3"
        elif choice == '2':
            download_type = "mp4"
        elif choice is None or choice == "":
            self.log_status("Toplu indirme türü seçimi iptal edildi.")
            return
        else:
            self.log_status("Geçersiz toplu indirme türü seçimi. Lütfen '1' veya '2' girin.")
            return

        self._set_ui_state("disabled")

        bulk_thread = threading.Thread(target=self._perform_bulk_download, args=(urls, download_type, output_folder))
        bulk_thread.start()


    def _perform_bulk_download(self, urls, download_type, output_folder):
        """Toplu indirme mantığı."""
        try:
            self.log_status(f"\n批量 indirme başlatılıyor ({download_type.upper()} formatında). Hedef: {os.path.abspath(output_folder)}")
            for i, url in enumerate(urls):
                self.log_status(f"\n--- URL {i+1}/{len(urls)} İndiriliyor: {url} ---")
                # Toplu indirmede kalite seçeneği yok, varsayılanları kullan
                self._perform_download(url, download_type, output_folder, "Auto", "320kbps", is_from_history=False)
                time.sleep(0.5)

            self.log_status("✅ Toplu indirme işlemi tamamlandı!")
        except Exception as e:
            self.log_status(f"❌ Toplu indirme sırasında bir hata oluştu: {e}")
        finally:
            self._set_ui_state("normal")
            self.progress_bar.set(0)
            self.progress_text_label.configure(text="İndirme İlerlemesi: %0")
            self.control_button.configure(state="disabled")

    def show_history_window(self):
        """İndirme geçmişini gösteren yeni bir pencere açar."""
        colors = get_colors() # Mevcut tema renklerini al

        history_window = ctk.CTkToplevel(self)
        history_window.title("İndirme Geçmişi")
        history_window.geometry("750x650")
        history_window.transient(self)
        history_window.grab_set()

        history_window.configure(fg_color=colors["NAVY_GREY"])

        history_window.grid_columnconfigure(0, weight=1)
        history_window.grid_rowconfigure(0, weight=1)
        history_window.grid_rowconfigure(1, weight=0)

        history_frame = ctk.CTkScrollableFrame(history_window, width=700, height=500, corner_radius=15, fg_color=colors["DARK_GREY"])
        history_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        history_frame.grid_columnconfigure(0, weight=1)

        self.history = self.load_history()

        if not self.history:
            ctk.CTkLabel(history_frame, text="İndirme geçmişi boş. Henüz bir indirme yapmadınız.", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["LIGHT_GREY"]).pack(pady=20)
            self.clear_history_button = ctk.CTkButton(history_window, text="Geçmişi Temizle", command=self.clear_download_history, font=ctk.CTkFont(size=14, weight="bold"),
                                               fg_color="red", hover_color="#FF0000", corner_radius=10, state="disabled")
            self.clear_history_button.grid(row=1, column=0, pady=(0, 20))
            return

        ctk.CTkLabel(history_frame, text="Geçmişteki İndirmeler:", font=ctk.CTkFont(size=20, weight="bold"), text_color=colors["LIGHT_GREY"]).pack(pady=(0, 15))

        for i, item in enumerate(reversed(self.history)):
            frame = ctk.CTkFrame(history_frame, corner_radius=10, fg_color=colors["NAVY_GREY"])
            frame.pack(fill="x", padx=10, pady=7)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=0)

            ctk.CTkLabel(frame, text=f"{len(self.history) - i}. Başlık: {item.get('title', 'Bilinmeyen Başlık')}", font=ctk.CTkFont(weight="bold", size=14), text_color=colors["LIGHT_GREY"], anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=2)
            ctk.CTkLabel(frame, text=f"URL: {item['url']}", font=ctk.CTkFont(size=12), text_color=colors["LIGHT_GREY"], anchor="w", wraplength=500).grid(row=1, column=0, sticky="ew", padx=10, pady=1)
            ctk.CTkLabel(frame, text=f"Tür: {item['type'].replace('_', ' ').title()}", font=ctk.CTkFont(size=12), text_color=colors["LIGHT_GREY"], anchor="w").grid(row=2, column=0, sticky="ew", padx=10, pady=1)
            ctk.CTkLabel(frame, text=f"Klasör: {item['output_folder']}", font=ctk.CTkFont(size=12), text_color=colors["LIGHT_GREY"], anchor="w", wraplength=500).grid(row=3, column=0, sticky="ew", padx=10, pady=1)
            ctk.CTkLabel(frame, text=f"Tarih: {item['timestamp']}", font=ctk.CTkFont(size=12), text_color=colors["LIGHT_GREY"], anchor="w").grid(row=4, column=0, sticky="ew", padx=10, pady=2)

            re_download_button = ctk.CTkButton(frame, text="Tekrar İndir", font=ctk.CTkFont(size=13, weight="bold"), height=35,
                                               fg_color=colors["PRIMARY_BLUE"], hover_color=colors["VIBRANT_PINK"], corner_radius=8,
                                               command=lambda url=item['url'], dtype=item['type'], folder=item['output_folder'], hw=history_window: self.re_download_from_history(url, dtype, folder, hw))
            re_download_button.grid(row=0, column=1, rowspan=5, padx=10, pady=5, sticky="nsew")

        self.clear_history_button = ctk.CTkButton(history_window, text="Geçmişi Temizle", command=lambda: self.clear_download_history(history_window), font=ctk.CTkFont(size=14, weight="bold"),
                                               fg_color="red", hover_color="#FF0000", corner_radius=10)
        self.clear_history_button.grid(row=1, column=0, pady=(15, 20))


        history_window.protocol("WM_DELETE_WINDOW", lambda: self.on_history_window_close(history_window))

    def on_history_window_close(self, history_window):
        history_window.destroy()
        self.grab_release()

    def clear_download_history(self, history_window=None):
        """İndirme geçmişini temizler."""
        confirm_dialog = ctk.CTkInputDialog(text="Geçmişi temizlemek istediğinizden emin misiniz? (Evet/Hayır)", title="Geçmişi Temizle Onayı")
        response = confirm_dialog.get_input()
        if response and response.lower() == "evet":
            self.history = []
            self.save_history()
            self.log_status("İndirme geçmişi temizlendi.")
            if history_window:
                history_window.destroy()
                self.grab_release()
        else:
            self.log_status("Geçmiş temizleme işlemi iptal edildi.")


    def re_download_from_history(self, url, download_type, output_folder, history_window):
        """Geçmişten seçilen öğeyi tekrar indirir."""
        self.log_status(f"Geçmişten tekrar indirme başlatılıyor: {url}")
        history_window.destroy()
        self.grab_release()

        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, ctk.END)
        self.url_entry.insert(0, url)
        # self.url_entry.configure(state="readonly") # Kullanıcının tekrar indirme URL'sini değiştirmesine izin verelim

        self.output_folder_entry.configure(state="normal")
        self.output_folder_entry.delete(0, ctk.END)
        self.output_folder_entry.insert(0, output_folder)
        # self.output_folder_entry.configure(state="readonly") # Klasörü de değiştirmesine izin verelim

        self.download_type_var.set(download_type)
        self.update_quality_options() # Doğru kalite seçeneklerini yeniden yükle

        video_quality = self.video_quality_combobox.get() # Güncellenmiş combobox değerini al
        audio_quality = self.audio_quality_combobox.get() # Güncellenmiş combobox değerini al

        # UI'ı normal hale getir ve tekrar indirme thread'ini başlat
        self._set_ui_state("normal")
        self.start_download_thread()


    def _set_ui_state(self, state):
        """UI elementlerinin durumunu ayarlar (normal/disabled)."""
        self.download_button.configure(state=state)
        self.bulk_download_button.configure(state=state)
        self.history_button.configure(state=state)
        self.url_entry.configure(state=state)
        self.output_folder_entry.configure(state=state)
        self.browse_button.configure(state=state)
        self.mp4_radio.configure(state=state)
        self.mp3_radio.configure(state=state)
        self.playlist_mp3_radio.configure(state=state)
        self.video_quality_combobox.configure(state=state) # Kalite combobox'ları
        self.audio_quality_combobox.configure(state=state) # Kalite combobox'ları

        self.update_quality_options() # Kalite seçeneklerinin durumu dinamik olarak yönetilsin

        if state == "disabled":
            self.control_button.configure(state="normal")
        else:
            self.control_button.configure(state="disabled")

    def update_quality_options(self):
        """Seçilen indirme türüne göre kalite seçeneklerini günceller ve etkinleştirir/devre dışı bırakır."""
        selected_type = self.download_type_var.get()
        colors = get_colors() # Mevcut tema renklerini al

        # Tüm kalite seçeneklerini başlangıçta devre dışı bırak
        self.video_quality_combobox.configure(state="disabled")
        self.audio_quality_combobox.configure(state="disabled")
        self.video_quality_label.configure(text_color=colors["TEXT_COLOR_DISABLED"]) # Devre dışı rengi
        self.audio_quality_label.configure(text_color=colors["TEXT_COLOR_DISABLED"]) # Devre dışı rengi


        if selected_type == "mp4":
            self.video_quality_combobox.configure(state="normal")
            self.video_quality_label.configure(text_color=colors["LIGHT_GREY"])
            self.video_quality_combobox.set("Auto") # Varsayılan
            self.video_quality_combobox.configure(values=["Auto", "1080p", "720p", "480p", "360p"]) # Örnek değerler
        elif selected_type == "mp3":
            self.audio_quality_combobox.configure(state="normal")
            self.audio_quality_label.configure(text_color=colors["LIGHT_GREY"])
            self.audio_quality_combobox.set("320kbps") # Varsayılan
            self.audio_quality_combobox.configure(values=["320kbps", "256kbps", "192kbps", "128kbps"])
        elif selected_type == "playlist_mp3":
            self.audio_quality_combobox.configure(state="normal")
            self.audio_quality_label.configure(text_color=colors["LIGHT_GREY"])
            self.audio_quality_combobox.set("320kbps") # Varsayılan
            self.audio_quality_combobox.configure(values=["320kbps", "256kbps", "192kbps", "128kbps"])
            # Playlist indirmelerde video kalitesi seçeneği mantıksız, devre dışı kalmalı
            self.video_quality_combobox.configure(state="disabled")
            self.video_quality_label.configure(text_color=colors["TEXT_COLOR_DISABLED"])


# Uygulamayı çalıştır
if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()
