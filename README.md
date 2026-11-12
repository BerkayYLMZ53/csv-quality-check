# CSV Quality Check

CSV dosyasını bir içe aktarma işleminden önce kontrol eder. Başlık sorunlarını, alan sayısı uymayan kayıtları ve sütunlardaki boş hücreleri gösterir. Dosyayı satır satır okur ve yalnızca rapor üretir.

## Kullanım

Python 3.10 veya üzeri yeterlidir. Komutları depo kökünde çalıştır.

```sh
python csv_quality_check.py examples/orders.csv
python csv_quality_check.py examples/orders.csv --json
python csv_quality_check.py tablo.csv --delimiter ';' --encoding cp1254 --fail-on-issues
```

Örnek dosyada dört kayıt, bir eksik alanlı kayıt ve geçerli kayıtlarda `quantity` sütununda bir boş hücre bulunur. Rapor, alan sayısı hatalı ilk 10 kaydın fiziksel satır aralığını gösterir. Çok satırlı tırnaklı alanlar tek kayıt olarak okunur.

Varsayılan ayraç virgül, kodlama UTF-8’dir. UTF-8 BOM varsa okunurken çıkarılır. Sekme ayracı için `--delimiter '\t'` kullan. Boş veya sadece boşluk içeren hücreler sayılır. Boş hücre sayımı alan sayısı doğru olan kayıtlarla sınırlıdır. Başlıklar tam metinleriyle karşılaştırılır.

`--fail-on-issues` ile tekrarlanan ya da boş başlık veya alan sayısı hatası çıkış kodu `1` verir. Okuma ve CSV sözdizimi hatalarında çıkış kodu `2` kullanılır.

## Testler

```sh
python -m unittest discover -s tests -v
```
