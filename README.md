# ÇizgiDiyarı Scraper

ÇizgiDiyarı forumundaki sıralı liste sayfalarındaki dergi linklerini çıkartan bir program.

## Gereksinimler

- Python 3
- scrapy (`pip install Scrapy` ile yüklenebilir)
- pydispatch (`pip install pydispatch` ile yüklenebilir)

## Kullanım

Program komut satırından çalıştırılır ve gerekli parametreler verilir. Programın yardım menüsüne ulaşmak için:

```bash
python3 scrape_links.py --help
```
gerekli parametreleri gösterecektir. ÇizgiDiyarı linkleri ziyaretçilerden gizlediği için oturum açmanız gerekmektedir, program çerezlerinizi kullanacaktır.

`url` olarak "sıralı liste" sayfalarından birini veriniz. --user ve --pw parametreleri ile oturum açma bilgilerinizi veriniz. --out parametresi ile çıktı dosyasının adını belirleyebilirsiniz.

Çıktı dosyası, bulunan linkleri (Mediafire ve Mega) içerir. Bu linkleri kullanarak dergileri indirebilirsiniz.

### Örnek Kullanım

```bash
python3 scrape_links.py https://www.cizgidiyari.com/forum/k/avni-sirali-liste.35298/ kullanici_adim sifrem123 links_avni.txt
```

### Çalışma Prensibi

"Sıralı liste" konu sayfaları, genellikle ilk post'larında farklı dergi sayılarının ayrı ayrı konularına linkler içerir. Bu script, verilen sıralı liste sayfasını ziyaret eder, sırayla ilk post'taki cizgidiyari.com linklerini ziyaret eder, ve bu linklerdeki Mediafire ve Mega linklerini bir çıktı dosyasında toplar.

Bu sistemin dışına çıkan pek çok istisna olabileceği için kullanıcının istediği tüm linkleri topladığını elle kontrol etmesi önerilir.

# Rename Script
`rename_files.py` dosyası:

İndirilen dergilerin isimlerini belirli bir formata göre düzenlemeyi deneyen bir script. Kod yeterince temiz değil ve çalıştırıldığı klasörde bir dosya sistemi hasarına yol açma riski mevcut. Dikkatli kullanınız.

## Örnek Kullanım

```bash
python3 rename.py ../leman/
```

# Lisans
Projede kullanılan kaynak kodlar MIT lisansı altındadır.
Kodun paylaşılması ve ihtiyaca göre değiştirilmesi serbesttir.