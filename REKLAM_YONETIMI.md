# Made in İzmir — Reklam Yönetimi Kılavuzu

Bu belge, platformdaki reklam alanlarını, her alanın boyutlarını ve reklamların admin paneli üzerinden nasıl yönetileceğini açıklamaktadır.

---

## İçindekiler

1. [Reklam Sistemi Nasıl Çalışır?](#1-reklam-sistemi-nasıl-çalışır)
2. [Reklam Alanları (Slotlar)](#2-reklam-alanları-slotlar)
3. [Admin Paneline Erişim](#3-admin-paneline-erişim)
4. [Reklam Slotları Yönetimi](#4-reklam-slotları-yönetimi)
5. [Reklamlar Yönetimi](#5-reklamlar-yönetimi)
6. [Yeni Reklam Ekleme — Adım Adım](#6-yeni-reklam-ekleme--adım-adım)
7. [Mevcut Reklamı Düzenleme](#7-mevcut-reklamı-düzenleme)
8. [Reklam Duraklatma ve Yeniden Yayına Alma](#8-reklam-duraklatma-ve-yeniden-yayına-alma)
9. [Reklam Silme](#9-reklam-silme)
10. [Fiyat Güncelleme](#10-fiyat-güncelleme)
11. [Birden Fazla Reklamveren Aynı Alana Reklam Verirse](#11-birden-fazla-reklamveren-aynı-alana-reklam-verirse)
12. [Reklam Görseli Hazırlama Rehberi](#12-reklam-görseli-hazırlama-rehberi)
13. [Sık Sorulan Sorular](#13-sık-sorulan-sorular)

---

## 1. Reklam Sistemi Nasıl Çalışır?

Platform, sayfaların belirli noktalarına yerleştirilmiş **reklam slotları** içermektedir. Her slotun kendine ait boyutu, tipi (yatay banner veya ürün grid kartı) ve fiyatlandırması vardır.

Bir reklamın yayınlanması için şu iki koşulun sağlanması gerekir:

- **Aktif** işaretli olmalıdır.
- Bugünün tarihi, reklamın **Başlangıç Tarihi** ile **Bitiş Tarihi** arasında olmalıdır.

Görsel yüklenmezse, ilgili reklam alanında otomatik olarak bir yer tutucu görüntü gösterilir:
> *"Buraya reklam verebilirsiniz. Reklam boyutu 970 × 90 px."*

---

## 2. Reklam Alanları (Slotlar)

Platformda toplam **7 reklam alanı** mevcuttur. Her alan için boyut, konum ve açıklama aşağıda listelenmiştir.

---

### 🏠 Ana Sayfa

#### Alan 1 — Hero Altı Banner

| Özellik | Değer |
|---------|-------|
| **Boyut** | 970 × 90 px |
| **Tip** | Yatay Banner |
| **Konum** | Ana sayfanın hero (giriş) bölümünde, "Platformu Keşfedin" ve "Bize Ulaşın" butonlarının hemen altında |
| **Görünürlük** | Platforma giriş yapan ve yapmayan tüm ziyaretçiler |

**Görsel Konum:**
```
┌──────────────────────────────────────────────────┐
│  [Hero Başlık & Alt Başlık]                      │
│  [Platformu Keşfedin]  [Bize Ulaşın]  ← Butonlar│
│  ┌────────────────── 970 × 90 px ──────────────┐ │
│  │              REKLAM ALANI                   │ │
│  └─────────────────────────────────────────────┘ │
│  ↓ ↓ ↓  (Aşağı kaydırma göstergesi)             │
└──────────────────────────────────────────────────┘
```

---

### 📦 Ürünler Sayfası (`/products/`)

#### Alan 2 — Üst Banner

| Özellik | Değer |
|---------|-------|
| **Boyut** | 970 × 90 px |
| **Tip** | Yatay Banner |
| **Konum** | Sayfa üstündeki hero bölümünün hemen altında, filtre çubuğunun üstünde |
| **Görünürlük** | Platforma giriş yapan ve yapmayan tüm ziyaretçiler |

**Görsel Konum:**
```
┌──────────────────────────────────────────────────┐
│  [Hero: Ürün Kataloğu başlığı ve istatistikler] │
├──────────────────────────────────────────────────┤
│  ┌────────────────── 970 × 90 px ──────────────┐ │
│  │              REKLAM ALANI                   │ │
│  └─────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤
│  [Sektör ▾]  [Etiket ▾]  [Temizle]   X ürün     │  ← Filtre çubuğu
├──────────────────────────────────────────────────┤
│  [Ürün] [Ürün] [Ürün] [Ürün] [Ürün] [Ürün]     │
│  [Ürün] [Ürün] [Ürün] [Ürün] [Ürün] [Ürün]     │
└──────────────────────────────────────────────────┘
```

#### Alan 3 — Ürün Grid Kartı

| Özellik | Değer |
|---------|-------|
| **Boyut** | 280 × 380 px |
| **Tip** | Grid Kartı (ürün kartı görünümünde) |
| **Konum** | Ürün gridinde her 6. ürünün ardından, ürün kartıyla aynı boyutta |
| **Görünürlük** | Platforma giriş yapan ve yapmayan tüm ziyaretçiler |
| **Reklam kartındaki buton** | "Ziyaret Et" (hedef URL'ye yönlendirir) |
| **Grid aralığı** | Her **6** üründen sonra 1 reklam (admin panelinden değiştirilebilir) |

> **Not:** Reklam kartı, diğer ürün kartlarıyla aynı görünümde tasarlanmıştır. Sol üst köşede küçük bir **"Reklam"** etiketi bulunur.

**Görsel Konum:**
```
┌────────┐ ┌────────┐ ┌────────┐
│ Ürün 1 │ │ Ürün 2 │ │ Ürün 3 │
└────────┘ └────────┘ └────────┘
┌────────┐ ┌────────┐ ┌────────┐
│ Ürün 4 │ │ Ürün 5 │ │ Ürün 6 │
└────────┘ └────────┘ └────────┘
┌──────────────────────────────┐
│ 🏷 Reklam                    │  ← 280 × 380 px, reklam kartı
│ [Görsel]                     │
│ Başlık                       │
│ [Ziyaret Et]                 │
└──────────────────────────────┘
┌────────┐ ┌────────┐ ┌────────┐
│ Ürün 7 │ ...                  │
```

---

### 🔍 Ürün Detay Sayfası (`/products/<id>/`)

#### Alan 4 — Ürün Detay Üst Banner

| Özellik | Değer |
|---------|-------|
| **Boyut** | 970 × 90 px |
| **Tip** | Yatay Banner |
| **Konum** | Ürün detay kartının hemen üstünde |
| **Görünürlük** | Yalnızca giriş yapmış kullanıcılar (alıcılar ve üreticiler) |

#### Alan 5 — Ürün Detay Alt Banner

| Özellik | Değer |
|---------|-------|
| **Boyut** | 970 × 90 px |
| **Tip** | Yatay Banner |
| **Konum** | Ürün bilgileri bölümünün hemen altında, iletişim formu ve diğer ürünler bölümünün üstünde |
| **Görünürlük** | Yalnızca giriş yapmış kullanıcılar |

**Görsel Konum:**
```
┌──────────────────────────────────────────────────┐
│  ┌────────────────── 970 × 90 px ──────────────┐ │
│  │              REKLAM ALANI (ÜST)             │ │
│  └─────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤
│  [Ürün Fotoğrafları]  │  [Ürün Bilgileri]        │
│                       │  Üretici, Sektör,         │
│                       │  Açıklama, Etiketler      │
├──────────────────────────────────────────────────┤
│  ┌────────────────── 970 × 90 px ──────────────┐ │
│  │              REKLAM ALANI (ALT)             │ │
│  └─────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤
│  [Üreticiyle İletişim Formu]                     │
│  [Üreticinin Diğer Ürünleri]                     │
└──────────────────────────────────────────────────┘
```

---

### 👤 Alıcı Paneli (`/dashboard/buyer/`)

#### Alan 6 — Hızlı Bağlantılar Altı Banner

| Özellik | Değer |
|---------|-------|
| **Boyut** | 970 × 90 px |
| **Tip** | Yatay Banner |
| **Konum** | "Hızlı Bağlantılar" bölümünün (Profil, Fuar Takvimi butonlarının) hemen altında |
| **Görünürlük** | Yalnızca giriş yapmış alıcılar |

#### Alan 7 — Alıcı Paneli Grid Kartı

| Özellik | Değer |
|---------|-------|
| **Boyut** | 280 × 380 px |
| **Tip** | Grid Kartı (ürün kartı görünümünde) |
| **Konum** | Alıcı panelindeki ürün gridinde her 6. ürünün ardından |
| **Görünürlük** | Yalnızca giriş yapmış alıcılar |
| **Reklam kartındaki buton** | "Ziyaret Et" |
| **Grid aralığı** | Her **6** üründen sonra 1 reklam (admin panelinden değiştirilebilir) |

---

## 3. Admin Paneline Erişim

Admin paneline tarayıcınızdan şu adres üzerinden ulaşabilirsiniz:

```
https://madeinizmir.com/admin/
```

Giriş yaptıktan sonra sol menüde **"REKLAMLAR"** başlığı altında iki bölüm görürsünüz:

```
REKLAMLAR
  ├── Reklam Slotları   ← Reklam alanlarının ayarları ve fiyatları
  └── Reklamlar         ← Tüm reklam kayıtları, ekleme ve düzenleme
```

> ℹ️ Admin paneline yalnızca yetkili sistem yöneticileri erişebilir.

---

## 4. Reklam Slotları Yönetimi

**Adres:** `/admin/ads/adslot/`

Reklam slotları, sitedeki sabit reklam konumlarını tanımlar. 7 slot sistem tarafından önceden oluşturulmuştur. **Slot eklemek veya silmek teknik müdahale gerektirir;** bu bölümden yalnızca mevcut slotların fiyat ve ayarları düzenlenir.

### 4.1 Slot Listesi

Sayfayı açtığınızda tüm slotlar tablo halinde listelenir:

```
Ad                          Slug                        Boyutlar      Tip           Aktif  Günlük  Aylık   Kur
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
Alıcı Paneli Grid Kartı     buyer_dashboard_grid_card   280 × 380 px  Grid Kartı    ✓      —       —       TRY
Alıcı Paneli Yatay          buyer_dashboard_horizontal  970 × 90 px   Yatay Banner  ✓      —       —       TRY
Ana Sayfa Hero Altı         home_hero_horizontal        970 × 90 px   Yatay Banner  ✓      —       —       TRY
Ürün Detay Alt              product_detail_bottom       970 × 90 px   Yatay Banner  ✓      —       —       TRY
Ürün Detay Üst              product_detail_top          970 × 90 px   Yatay Banner  ✓      —       —       TRY
Ürünler Grid Kartı          products_grid_card          280 × 380 px  Grid Kartı    ✓      —       —       TRY
Ürünler Sayfası Üst         products_top_horizontal     970 × 90 px   Yatay Banner  ✓      —       —       TRY
```

### 4.2 Slot Fiyatlarını Güncelleme

1. Güncellemek istediğiniz slotun adına tıklayın.
2. Açılan sayfada **"Fiyatlandırma"** bölümüne inin.
3. Aşağıdaki alanları doldurun:

   | Alan | Açıklama | Örnek |
   |------|----------|-------|
   | **Günlük Fiyat** | 1 günlük yayın ücreti | `500.00` |
   | **Haftalık Fiyat** | 7 günlük yayın ücreti | `3000.00` |
   | **Aylık Fiyat** | 30 günlük yayın ücreti | `10000.00` |
   | **Para Birimi** | 3 harfli kur kodu | `TRY` |

4. Sayfanın altındaki **"Kaydet"** butonuna basın.

> 💡 Fiyatlandırma alanları yalnızca admin kullanımı içindir; sitede ziyaretçilere gösterilmez. Reklamverenlere teklif hazırlarken referans olarak kullanınız.

### 4.3 Grid Aralığını Değiştirme

Grid kartı tipindeki slotlarda (Ürünler Grid Kartı ve Alıcı Paneli Grid Kartı) reklamın kaç üründen sonra görüneceğini değiştirebilirsiniz:

1. İlgili slota tıklayın.
2. **"Grid Ayarları"** bölümüne inin (varsayılan olarak kapalıdır, başlığa tıklayarak açın).
3. **"Grid Aralığı"** değerini değiştirin.
   - `6` → Her 6 üründen sonra 1 reklam *(varsayılan)*
   - `4` → Her 4 üründen sonra 1 reklam
   - `10` → Her 10 üründen sonra 1 reklam
4. **"Kaydet"** butonuna basın.

### 4.4 Bir Reklam Alanını Tamamen Kapatma

Belirli bir reklam alanını geçici olarak devre dışı bırakmak istiyorsanız:

1. İlgili slota tıklayın.
2. **"Temel Bilgiler"** bölümünde **"Aktif"** kutucuğunun işaretini kaldırın.
3. **"Kaydet"** butonuna basın.

Bu işlemin ardından o alana ait tüm reklamlar — aktif olsalar bile — sitede görünmez hale gelir.

> ⚠️ **Slug ve boyut alanlarını kesinlikle değiştirmeyin.** Bu değerler sistemin şablonlarıyla doğrudan bağlantılıdır.

---

## 5. Reklamlar Yönetimi

**Adres:** `/admin/ads/ad/`

Tüm reklam kayıtlarının listelendiği, yeni reklam eklenip mevcut reklamların düzenlendiği ana bölüm.

### 5.1 Reklam Listesi

```
Reklamveren          Slot                        Başl. Tarihi  Bitiş Tarihi  Sıra  Aktif  Durum          Önizleme
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Reklam Alanı         Ana Sayfa Hero Altı         01.01.2024    31.12.2099    0     ✓      ✓ Yayında       CSS placeholder
ABC Tekstil          Ürünler Sayfası Üst         01.05.2025    31.05.2025    0     ✓      ✓ Yayında       [görsel önizleme]
XYZ Mobilya          Ürünler Sayfası Üst         01.05.2025    31.05.2025    1     ✓      ✓ Yayında       [görsel önizleme]
Eski Reklam          Alıcı Paneli Yatay          01.01.2025    28.02.2025    0     ✓      ✗ Yayında değil [görsel önizleme]
```

**Sütun açıklamaları:**

| Sütun | Açıklama |
|-------|----------|
| **Reklamveren** | Reklamı veren firma/kişi adı |
| **Slot** | Reklamın görüneceği alan |
| **Başl. Tarihi** | Yayın başlangıç tarihi |
| **Bitiş Tarihi** | Yayın bitiş tarihi |
| **Sıra** | Aynı slotta birden fazla reklam olduğunda gösterim önceliği (küçük = önce) |
| **Aktif** | Elle açık/kapalı durumu |
| **Durum** | Tarih ve aktiflik kontrolünün birleşik sonucu |
| **Önizleme** | Yüklenen görselin küçük önizlemesi veya "CSS placeholder" notu |

### 5.2 Filtreleme ve Arama

Liste sayfasının sağ kenar çubuğunda şu filtreler bulunur:

- **Slota göre:** Yalnızca belirli bir alandaki reklamları görüntüleyin
- **Aktif durumuna göre:** Yalnızca aktif veya pasif reklamları listeleyin
- **Başlangıç tarihine göre:** Belirli bir dönemde başlayan reklamları filtreleyin

Liste başlığındaki **"Reklamveren"** veya **"Başlık"** alanına göre arama da yapabilirsiniz.

---

## 6. Yeni Reklam Ekleme — Adım Adım

1. `/admin/ads/ad/` sayfasında sağ üst köşedeki **"Reklam Ekle +"** butonuna tıklayın.

2. Açılan formda aşağıdaki alanları doldurun:

   **Reklam Bilgileri bölümü:**

   | Alan | Açıklama | Zorunlu mu? |
   |------|----------|-------------|
   | **Slot** | Açılır listeden reklamın gösterileceği alanı seçin | ✅ Evet |
   | **Reklamveren** | Firma veya kişi adı (dahili kayıt için) | ✅ Evet |
   | **Başlık / Alt Metin** | Görselin `alt` metni; erişilebilirlik ve SEO için kullanılır | ❌ Hayır |
   | **Hedef URL** | Reklama tıklandığında açılacak adres (örn. `https://www.firma.com`) | ✅ Evet |

   **Görsel bölümü:**

   | Alan | Açıklama | Zorunlu mu? |
   |------|----------|-------------|
   | **Görsel** | Reklam görseli — boyutlar için Bölüm 12'ye bakın | ❌ Hayır* |

   > *Görsel yüklenmezse o alana otomatik olarak altın kenarlıklı CSS yer tutucu gösterilir.

   **Yayın Dönemi bölümü:**

   | Alan | Açıklama | Zorunlu mu? |
   |------|----------|-------------|
   | **Başlangıç Tarihi** | Reklamın yayına gireceği tarih (örn. `2025-06-01`) | ✅ Evet |
   | **Bitiş Tarihi** | Reklamın otomatik olarak kalkacağı tarih (örn. `2025-06-30`) | ✅ Evet |

   **Yayın Ayarları bölümü:**

   | Alan | Açıklama | Zorunlu mu? |
   |------|----------|-------------|
   | **Sıralama** | Aynı slotta birden fazla reklam varsa öncelik sırası (`0` = en önce) | ✅ Evet |
   | **Aktif** | İşaretlenirse reklam yayına girer; işaretsizse tarihlere bakılmaksızın yayınlanmaz | ✅ Evet |

3. Formu doldurduktan sonra sayfanın altında üç kaydetme seçeneği bulunur:

   | Buton | Ne yapar? |
   |-------|-----------|
   | **Kaydet ve başka ekle** | Kaydeder, boş yeni form açılır |
   | **Kaydet ve düzenlemeye devam et** | Kaydeder, aynı sayfada kalmaya devam eder |
   | **Kaydet** | Kaydeder ve listeye döner |

4. Reklam kaydedildikten sonra, eğer tarih aralığı bugünü kapsıyorsa ve "Aktif" işaretliyse **hemen yayına girer.**

---

## 7. Mevcut Reklamı Düzenleme

1. `/admin/ads/ad/` listesinde düzenlemek istediğiniz reklamın **Reklamveren** adına tıklayın.
2. Açılan formda istediğiniz alanı değiştirin.
3. **"Kaydet"** butonuna basın.

**Sık yapılan düzenlemeler:**

| İşlem | Hangi alanı değiştirirsiniz? |
|-------|------------------------------|
| Bitiş tarihini uzatmak | **Bitiş Tarihi** |
| Görseli güncellemek | **Görsel** → "Değiştir" seçeneğini kullanın |
| Hedef URL'yi değiştirmek | **Hedef URL** |
| Öncelik sırasını değiştirmek | **Sıralama** |
| Reklamı geçici durdurmak | **Aktif** kutucuğunun işaretini kaldırın |

---

## 8. Reklam Duraklatma ve Yeniden Yayına Alma

### Duraklatma (Geçici Kapatma)

Bir reklamı kalıcı olarak silmeden geçici olarak durdurmak için:

1. Reklamın düzenleme sayfasını açın.
2. **"Yayın Ayarları"** bölümünde **"Aktif"** kutucuğunun **işaretini kaldırın.**
3. **"Kaydet"** butonuna basın.

Reklam siteden hemen kalkar ancak kayıt silinmez.

### Toplu Duraklatma

Birden fazla reklamı aynı anda durdurmak için:

1. `/admin/ads/ad/` listesinde her reklamın solundaki **onay kutucuğunu** işaretleyin.
2. Listenin altındaki **"Seçilen reklamlar için işlem"** açılır menüsünden — *(bu özellik ilerleyen güncellemelerle eklenebilir; tek tek işlem en güvenli yöntemdir)* — ilgili işlemi seçin.

### Yeniden Yayına Alma

1. Reklamın düzenleme sayfasını açın.
2. **"Aktif"** kutucuğunu **yeniden işaretleyin.**
3. Bitiş tarihinin hâlâ geçerli olduğunu kontrol edin; gerekirse uzatın.
4. **"Kaydet"** butonuna basın.

---

## 9. Reklam Silme

> ⚠️ Silme işlemi **geri alınamaz.** Reklamı ileride tekrar kullanmayı düşünüyorsanız silmek yerine **"Aktif"** kutucuğunun işaretini kaldırmanız önerilir.

### Tek Reklam Silme

1. Reklamın düzenleme sayfasını açın.
2. Sayfanın sol alt köşesindeki kırmızı **"Sil"** butonuna tıklayın.
3. Açılan onay ekranında **"Evet, eminim"** butonuna basın.

### Listeden Silme

1. `/admin/ads/ad/` listesinde reklamın yanındaki onay kutucuğunu işaretleyin.
2. Sayfanın altındaki işlem açılır menüsünden **"Seçilen reklamları sil"** seçeneğini seçin.
3. **"Uygula"** butonuna tıklayın ve onaylayın.

---

## 10. Fiyat Güncelleme

Reklam alanı fiyatları, **Reklam Slotları** bölümünden her slot için ayrı ayrı yönetilir.

### Adımlar:

1. `/admin/ads/adslot/` sayfasına gidin.
2. Fiyatını güncellemek istediğiniz slotun adına tıklayın.
3. Sayfanın altındaki **"Fiyatlandırma"** bölümüne inin.
4. İlgili fiyat alanlarını güncelleyin:

   ```
   Günlük Fiyat  [ 500.00  ] TRY
   Haftalık Fiyat[ 3000.00 ] TRY
   Aylık Fiyat   [10000.00 ] TRY
   Para Birimi   [ TRY     ]
   ```

5. **"Kaydet"** butonuna basın.

### Tüm Slot Fiyatlarına Hızlı Bakış

`/admin/ads/adslot/` liste sayfasında **Günlük Fiyat**, **Aylık Fiyat** ve **Para Birimi** sütunları doğrudan görünür. Fiyat girilmemiş alanlar `—` olarak gösterilir.

---

## 11. Birden Fazla Reklamveren Aynı Alana Reklam Verirse

Aynı reklam alanına birden fazla aktif reklam eklenebilir.

### Yatay Banner Alanları için:
- Her seferinde yalnızca **en düşük sıralama numarasına** sahip reklam gösterilir.
- Örnek: Sıralama `0` olan reklam, sıralama `1` ve `2` olanlara göre önce gösterilir.
- İki reklamı eşit süreyle göstermek istiyorsanız her birini ayrı bir **tarih aralığı** ile tanımlayın (birinin bitmesi diğerinin başlaması).

### Grid Kartı Alanları için:
- Reklamlar **sırayla dönüşümlü** gösterilir.
- Örnek: 3 reklamveren varsa → 6. ürünün ardından 1. reklam, 12. ürünün ardından 2. reklam, 18. ürünün ardından 3. reklam gösterilir ve tekrar başa döner.

### Öncelik sırası değiştirme:
1. `/admin/ads/ad/` listesinden ilgili reklamı açın.
2. **"Yayın Ayarları"** bölümündeki **Sıralama** alanını değiştirin.
3. **"Kaydet"** butonuna basın.

`0` en yüksek önceliği temsil eder. Aynı sıralama numarasına sahip iki reklam varsa sistem ikisinden birini rastgele seçer; bunu önlemek için her reklamın farklı bir sıralama numarası olduğundan emin olun.

---

## 12. Reklam Görseli Hazırlama Rehberi

Her reklam alanı için önerilen görsel boyutları:

| Alan | Boyut | Dosya Formatı | Max Dosya Boyutu |
|------|-------|--------------|-----------------|
| Ana Sayfa Hero Altı | **970 × 90 px** | JPG veya PNG | 500 KB |
| Ürünler Sayfası Üst | **970 × 90 px** | JPG veya PNG | 500 KB |
| Ürün Detay Üst | **970 × 90 px** | JPG veya PNG | 500 KB |
| Ürün Detay Alt | **970 × 90 px** | JPG veya PNG | 500 KB |
| Alıcı Paneli Yatay | **970 × 90 px** | JPG veya PNG | 500 KB |
| Ürünler Grid Kartı | **280 × 380 px** | JPG veya PNG | 300 KB |
| Alıcı Paneli Grid Kartı | **280 × 380 px** | JPG veya PNG | 300 KB |

**Öneriler:**
- Görseller mümkün olduğunca belirtilen boyutlarda hazırlanmalıdır. Farklı boyuttaki görseller otomatik olarak orantılı şekilde sığdırılır ancak en iyi görüntü için tam boyut kullanılmalıdır.
- JPG formatı dosya boyutu açısından tercih edilir.
- Görsel üzerinde metin varsa, mobil cihazlarda da okunabilir olduğundan emin olunuz.
- Şeffaflık gerektiren görseller için PNG kullanınız.

---

## 13. Sık Sorulan Sorular

**S: Bir reklamı geçici olarak durdurmak istiyorum, silmem gerekir mi?**
A: Hayır. Reklamın düzenleme sayfasında **Aktif** kutucuğunun işaretini kaldırmanız yeterlidir. Reklamı daha sonra tekrar aktifleştirebilirsiniz.

---

**S: Reklam yayına girdi ama sitede göremiyorum.**
A: Şunları kontrol edin:
1. **Aktif** işaretli mi?
2. **Bugünün tarihi** başlangıç ve bitiş tarihleri arasında mı?
3. Slotun kendisi aktif mi? (Reklam Slotları bölümünden kontrol edin)
4. Tarayıcı önbelleğini temizleyip sayfayı yenileyin.

---

**S: Grid aralığını (her 6 üründen sonra) değiştirmek istiyorum.**
A: Admin panelinde **Reklam Slotları** bölümüne gidin, ilgili grid slotunu açın ve **Grid Ayarları** bölümündeki **Grid Aralığı** değerini değiştirin. Örneğin `4` girerseniz reklam her 4 üründen sonra gösterilir.

---

**S: Reklam görseli yüklemedim ama reklamı yayınlamak istiyorum.**
A: Görsel zorunlu değildir. Görsel yüklenmezse ilgili alanda otomatik olarak altın sarısı kenarlıklı bir yer tutucu banner gösterilir. Bu yer tutucu, reklamvereniniz görselini gönderene kadar "Bu alana reklam verebilirsiniz" mesajı gösterir.

---

**S: Aynı anda birden fazla alana reklam ekleyebilir miyim?**
A: Evet. Her reklam kaydı bir slota bağlıdır. Bir reklamverenin hem "Ana Sayfa Hero Altı" hem de "Ürünler Sayfası Üst" alanlarında reklamı olmasını istiyorsanız iki ayrı reklam kaydı oluşturmanız gerekir.

---

**S: Reklamın bitiş tarihi geçti. Otomatik olarak kaldırılır mı?**
A: Evet. Bitiş tarihi geçen reklamlar otomatik olarak siteden kaldırılır. Herhangi bir işlem yapmanıza gerek yoktur. Reklam admin panelinde **"✗ Yayında değil"** olarak görünmeye devam eder ve silinmez.

---

*Bu belge Made in İzmir platformuna özel hazırlanmıştır.*
