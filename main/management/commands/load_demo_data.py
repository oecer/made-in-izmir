from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import ConsentText, Tenant, UserProfile
from catalog.models import Product, ProductTag, Sector
from expos.models import Expo, ExpoSignup


DEMO_PASSWORD = "demo1234"


SECTORS = [
    ("Tekstil", "Textile"),
    ("Gıda", "Food"),
    ("Makine", "Machinery"),
    ("Otomotiv", "Automotive"),
    ("Kimya", "Chemistry"),
    ("Tarım", "Agriculture"),
    ("Mobilya", "Furniture"),
    ("Seramik", "Ceramics"),
    ("Elektronik", "Electronics"),
    ("Ambalaj", "Packaging"),
]

PRODUCT_TAGS = [
    ("Organik", "Organic"),
    ("El Yapımı", "Handmade"),
    ("Yerli Üretim", "Domestic Production"),
    ("İhracata Uygun", "Export Ready"),
    ("Toptan", "Wholesale"),
    ("Perakende", "Retail"),
    ("Sürdürülebilir", "Sustainable"),
    ("Sertifikalı", "Certified"),
    ("Yeni Ürün", "New Product"),
    ("Çevre Dostu", "Eco-Friendly"),
    ("Premium", "Premium"),
    ("Ekonomik", "Economic"),
    ("Özel Tasarım", "Custom Design"),
    ("Doğal", "Natural"),
    ("Halal Sertifikalı", "Halal Certified"),
]

COMPANIES = [
    {
        "username": "ege_tekstil",
        "email": "info@egetekstil.com.tr",
        "first_name": "Ahmet",
        "last_name": "Yılmaz",
        "company_name": "Ege Tekstil A.Ş.",
        "phone_number": "+90 232 555 01 01",
        "country": "Türkiye",
        "city": "İzmir",
        "open_address": "Bornova Organize Sanayi Bölgesi, 1. Cadde No: 45, Bornova/İzmir",
        "website": "https://www.egetekstil.com.tr",
        "about_company": "1985 yılından bu yana İzmir'de tekstil üretimi yapan Ege Tekstil, pamuklu kumaş ve hazır giyim alanında Türkiye'nin önde gelen üreticilerinden biridir. Avrupa ve Orta Doğu'ya ihracat yapmaktadır.",
        "is_buyer": False,
        "is_producer": True,
        "producer_sectors": ["Tekstil"],
        "producer_quarterly_sales": Decimal("2500000.00"),
        "producer_product_count": 150,
    },
    {
        "username": "izmir_gida",
        "email": "iletisim@izmirgida.com.tr",
        "first_name": "Fatma",
        "last_name": "Demir",
        "company_name": "İzmir Gıda San. ve Tic. Ltd. Şti.",
        "phone_number": "+90 232 555 02 02",
        "country": "Türkiye",
        "city": "İzmir",
        "open_address": "Kemalpaşa Organize Sanayi Bölgesi, 3. Sokak No: 12, Kemalpaşa/İzmir",
        "website": "https://www.izmirgida.com.tr",
        "about_company": "İzmir Gıda, Ege Bölgesi'nin taze meyve ve sebzelerini işleyerek kurutulmuş meyve, reçel ve konserve ürünler üretmektedir. Organik sertifikalı ürünleriyle yurt içi ve yurt dışı pazarlarda yer almaktadır.",
        "is_buyer": False,
        "is_producer": True,
        "producer_sectors": ["Gıda", "Tarım"],
        "producer_quarterly_sales": Decimal("1800000.00"),
        "producer_product_count": 85,
    },
    {
        "username": "bornova_makine",
        "email": "satis@bornovamakine.com.tr",
        "first_name": "Mehmet",
        "last_name": "Kaya",
        "company_name": "Bornova Makine Sanayi Ltd. Şti.",
        "phone_number": "+90 232 555 03 03",
        "country": "Türkiye",
        "city": "İzmir",
        "open_address": "Atatürk Organize Sanayi Bölgesi, 7. Cadde No: 88, Çiğli/İzmir",
        "website": "https://www.bornovamakine.com.tr",
        "about_company": "Bornova Makine, endüstriyel otomasyon ve CNC tezgahları alanında 30 yılı aşkın tecrübeye sahiptir. Özellikle otomotiv ve havacılık sektörlerine yönelik hassas işleme çözümleri sunmaktadır.",
        "is_buyer": False,
        "is_producer": True,
        "producer_sectors": ["Makine", "Otomotiv"],
        "producer_quarterly_sales": Decimal("3200000.00"),
        "producer_product_count": 40,
    },
    {
        "username": "ege_ticaret",
        "email": "bilgi@egeticaret.com.tr",
        "first_name": "Ayşe",
        "last_name": "Özkan",
        "company_name": "Ege Ticaret ve Dış Tic. A.Ş.",
        "phone_number": "+90 232 555 04 04",
        "country": "Türkiye",
        "city": "İzmir",
        "open_address": "Alsancak Mah. Kıbrıs Şehitleri Cad. No: 56, Konak/İzmir",
        "website": "https://www.egeticaret.com.tr",
        "about_company": "Ege Ticaret, gıda ve tekstil sektörlerinde toptan alım yapan, ürünleri Avrupa pazarına ihraç eden bir dış ticaret firmasıdır. 15 ülkede aktif müşteri portföyüne sahiptir.",
        "is_buyer": True,
        "is_producer": False,
        "buyer_sectors": ["Gıda", "Tekstil"],
        "buyer_quarterly_volume": Decimal("4500000.00"),
    },
    {
        "username": "kuzey_market",
        "email": "tedarik@kuzeymarket.com.tr",
        "first_name": "Ali",
        "last_name": "Çelik",
        "company_name": "Kuzey Market Zinciri A.Ş.",
        "phone_number": "+90 232 555 05 05",
        "country": "Türkiye",
        "city": "İzmir",
        "open_address": "Gaziemir Mah. Sevgi Yolu Cad. No: 120, Gaziemir/İzmir",
        "website": "https://www.kuzeymarket.com.tr",
        "about_company": "Kuzey Market, Ege Bölgesi'nde 25 şubesiyle hizmet veren yerel bir süpermarket zinciridir. Yerel üreticilerden tedarik yaparak taze ve kaliteli ürünleri tüketiciye ulaştırmayı hedeflemektedir.",
        "is_buyer": True,
        "is_producer": False,
        "buyer_sectors": ["Gıda", "Ambalaj"],
        "buyer_quarterly_volume": Decimal("6000000.00"),
    },
    {
        "username": "anadolu_seramik",
        "email": "info@anadoluseramik.com.tr",
        "first_name": "Zeynep",
        "last_name": "Arslan",
        "company_name": "Anadolu Seramik ve İnşaat Malz. San. Tic. A.Ş.",
        "phone_number": "+90 232 555 06 06",
        "country": "Türkiye",
        "city": "İzmir",
        "open_address": "Torbalı Organize Sanayi Bölgesi, 2. Cadde No: 33, Torbalı/İzmir",
        "website": "https://www.anadoluseramik.com.tr",
        "about_company": "Anadolu Seramik, hem seramik karo üretimi yapan hem de hammadde tedariki için alıcı konumunda olan entegre bir firmadır. Yıllık 5 milyon metrekare üretim kapasitesine sahiptir.",
        "is_buyer": True,
        "is_producer": True,
        "buyer_sectors": ["Kimya"],
        "buyer_quarterly_volume": Decimal("1200000.00"),
        "producer_sectors": ["Seramik"],
        "producer_quarterly_sales": Decimal("3800000.00"),
        "producer_product_count": 60,
    },
]

PRODUCTS = [
    {
        "owner": "ege_tekstil",
        "title_tr": "Pamuklu Poplin Kumaş",
        "title_en": "Cotton Poplin Fabric",
        "description_tr": "Yüksek kaliteli %100 pamuklu poplin kumaş. Gömlek, elbise ve ev tekstili üretiminde kullanılabilir. 150 cm en, metrekare ağırlığı 120 gr.",
        "description_en": "High quality 100% cotton poplin fabric. Suitable for shirts, dresses and home textile production.",
        "sector": "Tekstil",
        "tags": ["Yerli Üretim", "İhracata Uygun", "Toptan", "Sertifikalı"],
    },
    {
        "owner": "ege_tekstil",
        "title_tr": "Organik Pamuk İplik",
        "title_en": "Organic Cotton Yarn",
        "description_tr": "GOTS sertifikalı organik pamuk iplik. Ne 30/1 ring iplik. Dokuma ve örme kumaş üretiminde kullanılır. Minimum sipariş 1 ton.",
        "description_en": "GOTS certified organic cotton yarn. Ne 30/1 ring yarn for weaving and knitting.",
        "sector": "Tekstil",
        "tags": ["Organik", "Sertifikalı", "Toptan", "Sürdürülebilir"],
    },
    {
        "owner": "ege_tekstil",
        "title_tr": "Kadın Keten Gömlek",
        "title_en": "Women's Linen Shirt",
        "description_tr": "Doğal keten kumaştan üretilmiş kadın gömlek. S-XL beden aralığında mevcuttur. Özel etiketleme (private label) hizmeti sunulmaktadır.",
        "description_en": "Women's shirt made from natural linen fabric. Available in S-XL sizes. Private label service offered.",
        "sector": "Tekstil",
        "tags": ["Doğal", "Özel Tasarım", "İhracata Uygun"],
    },
    {
        "owner": "izmir_gida",
        "title_tr": "Kurutulmuş İncir",
        "title_en": "Dried Figs",
        "description_tr": "İzmir'in meşhur Sarılop incirinden üretilmiş kurutulmuş incir. Katkısız, doğal kurutma yöntemiyle hazırlanmıştır. 250 gr, 500 gr ve 1 kg ambalaj seçenekleri mevcuttur.",
        "description_en": "Dried figs made from Izmir's famous Sarılop figs. Additive-free, naturally dried.",
        "sector": "Gıda",
        "tags": ["Organik", "Doğal", "İhracata Uygun", "Halal Sertifikalı"],
    },
    {
        "owner": "izmir_gida",
        "title_tr": "Ege Zeytinyağı - Naturel Sızma",
        "title_en": "Aegean Olive Oil - Extra Virgin",
        "description_tr": "Erken hasat Memecik zeytinlerinden soğuk sıkım yöntemiyle elde edilmiş naturel sızma zeytinyağı. Asitlik oranı %0.5'in altındadır. 500 ml ve 1 lt cam şişe ambalajlarda.",
        "description_en": "Extra virgin olive oil from early harvest Memecik olives, cold pressed. Acidity below 0.5%.",
        "sector": "Gıda",
        "tags": ["Organik", "Premium", "Doğal", "Sertifikalı"],
    },
    {
        "owner": "izmir_gida",
        "title_tr": "Kayısı Reçeli",
        "title_en": "Apricot Jam",
        "description_tr": "Ege kayısılarından geleneksel yöntemlerle üretilmiş ev yapımı lezzette kayısı reçeli. Koruyucu içermez. 380 gr kavanoz.",
        "description_en": "Apricot jam made from Aegean apricots using traditional methods. No preservatives.",
        "sector": "Gıda",
        "tags": ["Doğal", "El Yapımı", "Yerli Üretim"],
    },
    {
        "owner": "bornova_makine",
        "title_tr": "CNC Freze Tezgahı - BM-500",
        "title_en": "CNC Milling Machine - BM-500",
        "description_tr": "3 eksenli CNC freze tezgahı. 500x400x300 mm işleme kapasitesi. 12.000 RPM iş mili hızı. Siemens kontrol ünitesi. Otomotiv ve havacılık parçaları için ideal.",
        "description_en": "3-axis CNC milling machine. 500x400x300 mm machining capacity. 12,000 RPM spindle speed.",
        "sector": "Makine",
        "tags": ["Yerli Üretim", "Sertifikalı", "Premium"],
    },
    {
        "owner": "bornova_makine",
        "title_tr": "Endüstriyel Robot Kol - BR-200",
        "title_en": "Industrial Robot Arm - BR-200",
        "description_tr": "6 eksenli endüstriyel robot kol. 200 kg taşıma kapasitesi. Kaynak, montaj ve paletleme uygulamaları için uygundur. Yerli yazılım ile tam entegrasyon.",
        "description_en": "6-axis industrial robot arm. 200 kg payload capacity. Suitable for welding, assembly and palletizing.",
        "sector": "Makine",
        "tags": ["Yerli Üretim", "Yeni Ürün", "Premium"],
    },
    {
        "owner": "anadolu_seramik",
        "title_tr": "Porselen Yer Karosu - Mermer Desen",
        "title_en": "Porcelain Floor Tile - Marble Pattern",
        "description_tr": "60x60 cm porselen yer karosu. Mermer görünümlü, mat yüzey. Yüksek aşınma dayanımı (PEI 5). İç ve dış mekan kullanımına uygun. Minimum sipariş 100 m².",
        "description_en": "60x60 cm porcelain floor tile. Marble look, matte surface. High abrasion resistance (PEI 5).",
        "sector": "Seramik",
        "tags": ["Yerli Üretim", "Premium", "İhracata Uygun"],
    },
    {
        "owner": "anadolu_seramik",
        "title_tr": "Dekoratif Duvar Karosu - Osmanlı Motifli",
        "title_en": "Decorative Wall Tile - Ottoman Pattern",
        "description_tr": "20x20 cm el boyaması dekoratif duvar karosu. Geleneksel Osmanlı motifleri. Mutfak, banyo ve otel dekorasyonunda kullanılabilir. Özel tasarım siparişi kabul edilir.",
        "description_en": "20x20 cm hand-painted decorative wall tile. Traditional Ottoman motifs.",
        "sector": "Seramik",
        "tags": ["El Yapımı", "Özel Tasarım", "Premium"],
    },
    {
        "owner": "anadolu_seramik",
        "title_tr": "Seramik Lavabo - Modern Seri",
        "title_en": "Ceramic Washbasin - Modern Series",
        "description_tr": "Tezgah üstü seramik lavabo. Modern tasarım, antibakteriyel sır kaplama. 50x40 cm boyutlarında. Otel ve konut projeleri için toptan satış yapılmaktadır.",
        "description_en": "Countertop ceramic washbasin. Modern design, antibacterial glaze coating. 50x40 cm.",
        "sector": "Seramik",
        "tags": ["Yerli Üretim", "Toptan", "Yeni Ürün"],
    },
    {
        "owner": "izmir_gida",
        "title_tr": "Ege Kekik - Kurutulmuş",
        "title_en": "Aegean Thyme - Dried",
        "description_tr": "İzmir dağlarından toplanan doğal kekik. Kurutulmuş ve paketlenmiştir. Baharat olarak veya kekik çayı olarak tüketilebilir. 100 gr ve 250 gr paketlerde.",
        "description_en": "Natural thyme from Izmir mountains. Dried and packaged. Can be used as spice or thyme tea.",
        "sector": "Tarım",
        "tags": ["Organik", "Doğal", "Ekonomik", "Yerli Üretim"],
    },
]

EXPOS = [
    {
        "title_tr": "İzmir Enternasyonal Fuarı",
        "title_en": "Izmir International Fair",
        "description_tr": "Türkiye'nin en köklü fuar organizasyonu olan İzmir Enternasyonal Fuarı, yerli ve yabancı üreticileri alıcılarla buluşturmaktadır. Geniş ürün yelpazesiyle her sektörden firmalara açıktır.",
        "description_en": "Turkey's oldest and most prestigious fair organization, the Izmir International Fair brings together domestic and international producers with buyers.",
        "location_tr": "İzmir Fuar Alanı, Kültürpark, Konak/İzmir",
        "location_en": "Izmir Fairground, Kulturpark, Konak/Izmir",
        "days_from_now": 60,
        "duration_days": 10,
        "deadline_before": 15,
    },
    {
        "title_tr": "Ege Gıda ve İçecek Fuarı",
        "title_en": "Aegean Food and Beverage Fair",
        "description_tr": "Ege Bölgesi'nin gıda üreticilerini bir araya getiren sektörel fuar. Organik ürünler, geleneksel tatlar ve yenilikçi gıda çözümleri sergilenmektedir.",
        "description_en": "A sectoral fair bringing together food producers from the Aegean Region. Organic products, traditional flavors and innovative food solutions are exhibited.",
        "location_tr": "Fuar İzmir Kongre ve Fuar Merkezi, Gaziemir/İzmir",
        "location_en": "Fair Izmir Congress and Exhibition Center, Gaziemir/Izmir",
        "days_from_now": 90,
        "duration_days": 5,
        "deadline_before": 20,
    },
    {
        "title_tr": "İzmir Tekstil ve Moda Fuarı",
        "title_en": "Izmir Textile and Fashion Fair",
        "description_tr": "Tekstil sektörünün önde gelen firmalarının katıldığı uluslararası tekstil ve moda fuarı. Kumaş, iplik, hazır giyim ve moda aksesuarları sergilenmektedir.",
        "description_en": "International textile and fashion fair with leading textile companies. Fabric, yarn, ready-to-wear and fashion accessories are exhibited.",
        "location_tr": "İzmir Uluslararası Fuar Merkezi, Gaziemir/İzmir",
        "location_en": "Izmir International Fair Center, Gaziemir/Izmir",
        "days_from_now": 120,
        "duration_days": 4,
        "deadline_before": 30,
    },
]


class Command(BaseCommand):
    help = "Demo verilerini veritabanına yükler"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Mevcut demo verilerini silip yeniden yükler",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        if User.objects.filter(username="ege_tekstil").exists() and not options["flush"]:
            self.stdout.write(self.style.WARNING(
                "Demo veriler zaten yüklenmiş. Yeniden yüklemek için --flush kullanın."
            ))
            return

        with transaction.atomic():
            sectors = self._create_sectors()
            tags = self._create_tags()
            self._create_admin()
            users, tenants = self._create_companies(sectors)
            self._create_products(users, tenants, sectors, tags)
            expos = self._create_expos()
            self._create_expo_signups(expos, users, tenants)
            self._create_consent_text()

        self.stdout.write(self.style.SUCCESS("\nDemo veriler başarıyla yüklendi!"))
        self.stdout.write(f"  Admin girişi: admin / {DEMO_PASSWORD}")
        self.stdout.write(f"  Kullanıcı girişi: ege_tekstil / {DEMO_PASSWORD}")

    def _flush(self):
        self.stdout.write("Mevcut demo veriler siliniyor...")
        ExpoSignup.objects.all().delete()
        Expo.objects.all().delete()
        Product.objects.all().delete()
        UserProfile.objects.all().delete()
        Tenant.objects.all().delete()
        demo_usernames = [c["username"] for c in COMPANIES]
        User.objects.filter(username__in=demo_usernames + ["admin"]).delete()
        ProductTag.objects.all().delete()
        Sector.objects.all().delete()
        ConsentText.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("  Silindi."))

    def _create_sectors(self):
        self.stdout.write("Sektörler oluşturuluyor...")
        sectors = {}
        for name_tr, name_en in SECTORS:
            sector, _ = Sector.objects.get_or_create(
                name_tr=name_tr, defaults={"name_en": name_en}
            )
            sectors[name_tr] = sector
        self.stdout.write(self.style.SUCCESS(f"  {len(sectors)} sektör oluşturuldu."))
        return sectors

    def _create_tags(self):
        self.stdout.write("Ürün etiketleri oluşturuluyor...")
        tags = {}
        for name_tr, name_en in PRODUCT_TAGS:
            tag, _ = ProductTag.objects.get_or_create(
                name_tr=name_tr, defaults={"name_en": name_en}
            )
            tags[name_tr] = tag
        self.stdout.write(self.style.SUCCESS(f"  {len(tags)} etiket oluşturuldu."))
        return tags

    def _create_admin(self):
        self.stdout.write("Admin kullanıcısı oluşturuluyor...")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@madeinizmir.org",
                password=DEMO_PASSWORD,
                first_name="Admin",
                last_name="Yönetici",
            )
            self.stdout.write(self.style.SUCCESS("  Admin oluşturuldu."))
        else:
            self.stdout.write(self.style.WARNING("  Admin zaten mevcut, atlanıyor."))

    def _create_companies(self, sectors):
        self.stdout.write("Firmalar ve kullanıcılar oluşturuluyor...")
        users = {}
        tenants = {}

        for data in COMPANIES:
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=DEMO_PASSWORD,
                first_name=data["first_name"],
                last_name=data["last_name"],
            )
            users[data["username"]] = user

            tenant = Tenant.objects.create(
                owner=user,
                company_name=data["company_name"],
                phone_number=data["phone_number"],
                country=data["country"],
                city=data["city"],
                open_address=data.get("open_address", ""),
                website=data.get("website", ""),
                about_company=data.get("about_company", ""),
                is_buyer=data["is_buyer"],
                is_producer=data["is_producer"],
                buyer_quarterly_volume=data.get("buyer_quarterly_volume"),
                producer_quarterly_sales=data.get("producer_quarterly_sales"),
                producer_product_count=data.get("producer_product_count"),
            )

            if data["is_buyer"] and "buyer_sectors" in data:
                buyer_sector_objs = [sectors[s] for s in data["buyer_sectors"]]
                tenant.buyer_interested_sectors.set(buyer_sector_objs)

            if data["is_producer"] and "producer_sectors" in data:
                producer_sector_objs = [sectors[s] for s in data["producer_sectors"]]
                tenant.producer_sectors.set(producer_sector_objs)

            tenants[data["username"]] = tenant

            UserProfile.objects.create(
                user=user,
                tenant=tenant,
                tenant_role="admin",
            )

            self.stdout.write(f"    {data['company_name']}")

        self.stdout.write(self.style.SUCCESS(f"  {len(users)} firma oluşturuldu."))
        return users, tenants

    def _create_products(self, users, tenants, sectors, tags):
        self.stdout.write("Ürünler oluşturuluyor...")
        count = 0
        for data in PRODUCTS:
            user = users[data["owner"]]
            tenant = tenants[data["owner"]]
            product = Product.objects.create(
                producer=user,
                tenant=tenant,
                title_tr=data["title_tr"],
                title_en=data["title_en"],
                description_tr=data["description_tr"],
                description_en=data["description_en"],
                sector=sectors.get(data["sector"]),
                is_active=True,
            )
            tag_objs = [tags[t] for t in data["tags"]]
            product.tags.set(tag_objs)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"  {count} ürün oluşturuldu."))

    def _create_expos(self):
        self.stdout.write("Fuarlar oluşturuluyor...")
        today = date.today()
        expos = {}

        for data in EXPOS:
            start = today + timedelta(days=data["days_from_now"])
            end = start + timedelta(days=data["duration_days"])
            deadline = start - timedelta(days=data["deadline_before"])

            expo = Expo.objects.create(
                title_tr=data["title_tr"],
                title_en=data["title_en"],
                description_tr=data["description_tr"],
                description_en=data["description_en"],
                location_tr=data["location_tr"],
                location_en=data["location_en"],
                start_date=start,
                end_date=end,
                registration_deadline=deadline,
                is_active=True,
            )
            expos[data["title_tr"]] = expo

        self.stdout.write(self.style.SUCCESS(f"  {len(expos)} fuar oluşturuldu."))
        return expos

    def _create_expo_signups(self, expos, users, tenants):
        self.stdout.write("Fuar kayıtları oluşturuluyor...")
        signups = [
            ("İzmir Enternasyonal Fuarı", "ege_tekstil", 5, "Tekstil ürünlerimizi sergilemek istiyoruz."),
            ("İzmir Enternasyonal Fuarı", "anadolu_seramik", 8, "Yeni seramik koleksiyonumuzu tanıtacağız."),
            ("Ege Gıda ve İçecek Fuarı", "izmir_gida", 10, "Organik ürün yelpazemizi sunacağız."),
            ("İzmir Tekstil ve Moda Fuarı", "ege_tekstil", 12, "Yeni sezon kumaş koleksiyonumuzu sergileyeceğiz."),
        ]

        count = 0
        for expo_title, username, product_count, notes in signups:
            expo = expos.get(expo_title)
            user = users.get(username)
            tenant = tenants.get(username)
            if expo and user and tenant:
                ExpoSignup.objects.create(
                    expo=expo,
                    user=user,
                    tenant=tenant,
                    product_count=product_count,
                    uses_listed_products=False,
                    product_description=notes,
                    notes=notes,
                    status="pending",
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  {count} fuar kaydı oluşturuldu."))

    def _create_consent_text(self):
        self.stdout.write("Üyelik sözleşmesi metni oluşturuluyor...")
        ConsentText.objects.get_or_create(
            pk=1,
            defaults={
                "text_tr": (
                    "Made in İzmir platformuna üye olarak aşağıdaki koşulları kabul etmiş sayılırsınız:\n\n"
                    "1. Paylaştığınız firma ve ürün bilgilerinin doğruluğunu taahhüt edersiniz.\n"
                    "2. Platform üzerindeki bilgileriniz, potansiyel alıcı ve tedarikçilerle paylaşılabilir.\n"
                    "3. Kişisel verileriniz 6698 sayılı KVKK kapsamında korunmaktadır.\n"
                    "4. Platform yönetimi, uygunsuz içerikleri kaldırma hakkını saklı tutar.\n"
                    "5. Üyeliğiniz, platform yönetiminin onayına tabidir."
                ),
                "text_en": (
                    "By becoming a member of the Made in Izmir platform, you agree to the following terms:\n\n"
                    "1. You confirm the accuracy of the company and product information you share.\n"
                    "2. Your information on the platform may be shared with potential buyers and suppliers.\n"
                    "3. Your personal data is protected under the KVKK (Law No. 6698).\n"
                    "4. The platform management reserves the right to remove inappropriate content.\n"
                    "5. Your membership is subject to approval by the platform management."
                ),
                "version": "v1.0",
            },
        )
        self.stdout.write(self.style.SUCCESS("  Üyelik sözleşmesi oluşturuldu."))
