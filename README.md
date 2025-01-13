# Halı Stok Uygulaması

## Genel Bakış
Bu uygulama, Python ve PyQt5 ile geliştirilmiş kapsamlı bir halı mağazası yönetim sistemidir. Halı envanterini yönetmek için sezgisel bir arayüz sunar ve halı kayıtlarını ekleme, görüntüleme, arama ve silme özelliklerini içerir.

## Özellikler
- Detaylı bilgilerle yeni halı kayıtları ekleme
- Mevcut halı miktarlarını otomatik güncelleme
- Tüm halı kayıtlarını tablo formatında görüntüleme
- Barkod ile halı arama
- Çoklu seçim ve halı kayıtlarını silme
- Halı alanını metrekare cinsinden otomatik hesaplama
- Sayfalar arası kolay gezinme

## Gereksinimler
- Python 3.x
- PyQt5
- sqlite3 (Python standart kütüphanesinde mevcuttur)

## Kurulum
1. Sisteminizde Python 3.x'in kurulu olduğundan emin olun
2. Gerekli PyQt5 kütüphanesini yükleyin:
```bash
pip install PyQt5
```

## Veritabanı Yapısı
Uygulama aşağıdaki alanları içeren SQLite veritabanını (carpets.db) kullanır:
- BARKOD
- KALİTE
- DESEN
- EN(CM)
- BOY(CM)
- RENK
- ADET
- TÜR
- EBAT (M2) (otomatik hesaplanır)

## Kullanım

### Ana Sayfa
- Ana sayfa arama işlevi ve gezinme düğmelerini gösterir
- Belirli halıları hızlıca bulmak için barkod aramasını kullanın
- Halı yönetim arayüzüne erişmek için "HALI YÖNETİMİ" düğmesine tıklayın

### Halı Yönetimi
- Giriş alanlarına halı detaylarını girin
- Alanlar arasında hızlıca geçiş yapmak için Enter tuşunu kullanın
- Yeni halı eklemek veya mevcut miktarı güncellemek için "HALI EKLE" düğmesine tıklayın
- Tüm kayıtları görüntülemek için "HALILARI GÖSTER" düğmesine tıklayın
- Birden fazla kayıt seçin ve silmek için "SEÇİLENLERİ SİL" düğmesine tıklayın
- Ana sayfaya dönmek için "ANA SAYFA" düğmesine tıklayın

### Veri Girişi İpuçları
1. Kayıt eklemeden önce tüm alanlar doldurulmalıdır
2. En ve boy santimetre cinsinden girilmelidir
3. Aynı özelliklere sahip mevcut halılar için miktar otomatik olarak mevcut kayda eklenecektir
4. Metrekare cinsinden alan en, boy ve adet kullanılarak otomatik hesaplanır

## Özellik Detayları

### Otomatik Miktar Güncelleme
- Aynı özelliklere (barkod, kalite, desen, boyutlar, renk ve tür) sahip bir halı eklendiğinde, sistem otomatik olarak yeni bir kayıt oluşturmak yerine miktarı günceller

### Alan Hesaplama
- Sistem toplam alanı metrekare cinsinden aşağıdaki formülü kullanarak otomatik hesaplar:
  - Alan = (En × Boy × Adet) / 10000
- Sonuç yukarı yuvarlanır

### Arama İşlevi
- Kısmi barkod araması desteklenir
- Sonuçlar özel bir tabloda gösterilir
- Arama sonuçları salt okunurdur

## Hata Yönetimi
- Uygulama aşağıdaki durumlar için kapsamlı hata yönetimi içerir:
  - Veritabanı işlemleri
  - Geçersiz veri girişi
  - Silme işlemleri
- Sorun oluştuğunda kullanıcı dostu hata mesajları gösterilir

## Gezinme
- "ANA SAYFA" ve "HALI YÖNETİMİ" düğmeleri ile sayfalar arası kolay gezinme
- Açık düğme etiketleri ve işlevselliği ile sezgisel arayüz

## Veri Güvenliği
- Tüm kayıtlar yerel SQLite veritabanında saklanır
- Salt okunur tablolar yanlışlıkla veri değişikliğini önler
- Silme onayı iletişim kutusu yanlışlıkla kayıt silinmesini önler****
