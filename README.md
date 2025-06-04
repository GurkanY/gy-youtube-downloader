# YouTube Downloader (GY YouTube Downloader) v2.6.2
GY YouTube İndirici, Python ve CustomTkinter kullanılarak geliştirilmiş, kullanıcı dostu bir masaüstü uygulamasıdır. Bu uygulama, YouTube videolarını ve çalma listelerini kolayca MP4 (video) veya MP3 (ses) formatlarında indirmenizi sağlar. Basit arayüzü sayesinde herkesin rahatlıkla kullanabileceği bir araçtır.

Özellikler
- Tekli Video İndirme: Belirli bir YouTube videosunu MP4 veya MP3 olarak indirin.
- Çalma Listesi İndirme: Tüm YouTube çalma listelerini tek seferde MP3 formatında indirin.
- Çözünürlük Seçenekleri: MP4 indirmeleri için farklı video çözünürlükleri (örn., 1080p, 720p) arasından seçim yapın.
- Ses Kalitesi Seçenekleri: MP3 indirmeleri için çeşitli bitrate'ler (örn., 320kbps, 192kbps) seçin.
- Toplu İndirme: Bir metin dosyasında listelenen birden fazla URL'yi otomatik olarak indirin.
- İndirme Geçmişi: Yapılan tüm indirmelerin kaydını tutar ve geçmişten tekrar indirme imkanı sunar.
- Kullanıcı Dostu Arayüz: Modern ve sezgisel CustomTkinter arayüzü sayesinde kolay kullanım.
- Tema Seçimi: Açık ve Koyu tema seçenekleriyle kişiselleştirilebilir görünüm.
- İlerleme Çubuğu ve Durum Mesajları: İndirme sürecini gerçek zamanlı olarak takip edin.
- Otomatik Klasör Oluşturma: Belirtilen çıktı klasörü mevcut değilse otomatik olarak oluşturur.
- Lisans Doğrulama Sistemi: Basit bir token doğrulama sistemi ile yetkisiz kullanımı kısıtlama imkanı (isteğe bağlı ve kolayca yönetilebilir).

*** Kurulum ve Çalıştırma
1- Ön Gereksinimler
Python 3.x: Sisteminizde Python 3.x'in yüklü olduğundan emin olun. Buradan indirebilirsiniz: python.org
yt-dlp ve customtkinter kütüphaneleri: Bunlar temel Python kütüphaneleridir.
FFmpeg (Çok Önemli!): FFmpeg kurulu ve sisteminizin PATH ortam değişkenine eklenmiş olmalıdır. Bu, MP3 dönüştürme ve bazı video formatlarının birleştirilmesi için hayati öneme sahiptir. FFmpeg'i buradan indirebilirsiniz: ffmpeg.org/download.html.

Adımlar
Depoyu Klonlayın veya İndirin:

Bash
git clone https://github.com/GurkanY/gy-youtube-downloader.git
cd gy-youtube-downloader

Gerekli Python Kütüphanelerini Yükleyin:

Önce bir sanal ortam oluşturmanız önerilir, ancak doğrudan da kurabilirsiniz.

Sanal ortam kullanarak (önerilir):

Bash

python -m venv venv
# Windows'ta:
.\venv\Scripts\activate
# macOS/Linux'ta:
source venv/bin/activate
pip install -r requirements.txt
Sanal ortam olmadan (genel geliştirme için daha az önerilir):

Bash

pip install customtkinter yt-dlp Pillow
(Eğer bir requirements.txt dosyası oluşturmak isterseniz, terminalde proje dizininize gidip şunu çalıştırın: pip freeze > requirements.txt)

FFmpeg Kurulumu (Önemli!)
FFmpeg'in indirildiğinden ve sisteminizin PATH'ine eklendiğinden emin olun. Bunu nasıl yapacağınızdan emin değilseniz, "add ffmpeg to path [işletim sisteminiz]" şeklinde hızlı bir arama size detaylı talimatlar sağlayacaktır.

Token Dosyası Kurulumu (İsteğe Bağlı, geliştirme/test için)
Uygulama temel bir token doğrulama sistemi içerir. Bunu kullanmayı planlıyorsanız, projenin kök dizinine tokens.txt adında bir dosya oluşturun. Bu dosyadaki her satır geçerli bir token içermelidir. Uygulama bu token'ları doğrulama için hashleyecektir.
Örnek tokens.txt:

mysecrettoken123
anotherValidToken456
(Bu dosya mevcut değilse veya boşsa, uygulamada bypass edilmediği veya başlangıçta geçerli bir token girilmediği sürece uygulamanın token doğrulaması başarısız olacaktır.)

Uygulamayı Çalıştırın:
python youtube_indirici_gurkan_v4.py

Kullanım
Uygulamayı başlatın.
YouTube video veya çalma listesi URL'sini "YouTube URL'si" alanına yapıştırın.
İstenen indirme türünü (MP4 Video, MP3 Ses, Playlist MP3) seçin.
Seçiminize göre beliren kalite seçeneklerini (MP4 için video çözünürlüğü, MP3 için ses bitrate'i) ayarlayın.
Bir çıktı klasörü seçin veya varsayılanı (indirilen_icerikler) kullanın.
İndirmeyi başlatmak için "İndir" düğmesine tıklayın.
Toplu indirmeler için "Toplu İndir" düğmesine tıklayın ve URL listenizi içeren bir .txt dosyası seçin.
Önceki indirmelerinize "Geçmiş" düğmesine tıklayarak erişin.
Geliştirme Notları
Bu proje, Python'ın CustomTkinter kütüphanesini kullanarak modern ve işlevsel bir GUI oluşturma pratiği olarak geliştirilmiştir. yt-dlp kütüphanesi, gerçek YouTube içerik indirme ve dönüştürme işlemlerini gerçekleştirir.

Lisans
Bu proje Gürkan Yılmaz tarafından geliştirilmiştir. Tüm hakları saklıdır. Ticari kullanım veya yeniden dağıtım için lütfen geliştiriciyle iletişime geçin.

Geliştirici İletişim
Gürkan Yılmaz - gurkanyilmaz.k@gmail.com
