<p align="center">
	<img src="assets/logo.png"/><br>
</p>

# Toloka2Tranmission [![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

<p align="center">
<img src="https://img.shields.io/github/languages/code-size/CakesTwix/Toloka2Tranmission?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/>
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
<img src="https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white"/><br><br>
<a href="https://www.buymeacoffee.com/cakestwix"><img width="150" src="https://img.buymeacoffee.com/button-api/?text=Buy me a tea&emoji=🍵&slug=cakestwix&button_colour=FF5F5F&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00" /></a>
</p>

Консольна утиліта для докачування нових серій аніме з Toloka.
Для скачування торрент-файлів використовується selfhost рішення Jackett!

> У мене на даний момент немає бажання писати під інші торрент-трекери або щось крім аніме. Я написав суто для себе і роздав вихідний код, щоб ви могли самостійно змінити код і поширювати його далі! Слався Open Source!

Чому я зробив цей скрипт? Хочу дивитися онгоінги і не думати над постійним перейменуванням для свого медіа-сервера Jellyfin, оскільки у кожного свій "стандарт" і тільки одиниці дотримуються стандарту "S01E01", який підтримує мій медіа-сервер.
Наразі можна качати торренти, де одна директорія (Один сезон), в якому знаходяться серії

```
The Girl I Like Forgot Her Glasses (S1)
├── Episode S1E01.mkv
├── Episode S1E02.mkv
├── Episode S1E03.mkv
├── Episode S1E04.mkv
├── Episode S1E05.mkv
├── Episode S1E06.mkv
├── Episode S1E07.mkv
└── Episode S1E08.mkv
```

## Usage/Examples

* Допомога
	```bash
	python -m toloka2transmission --help
	```
* Оновити всі торренти
	```bash
	python -m toloka2transmission
	```
* Завантажити нові серії, якщо торрент оновився
	```bash
	python -m toloka2transmission -с CODENAME
	```
> Коднейм береться з titles.ini, про нього пізніше
* Отримати список чисел із рядка
	```bash
	python -m toloka2transmission -n "text1 123"
	```
> Це необхідно для того, щоб перейменувати файли в торренті для визначення номера серії в Jellyfin або Plex. Потрібно в конфігурації вказати в якому індексі міститься номер серії

> **Примітка:** У торренті береться відразу Директорія/Файл.mkv, наприклад:
Horimiya - Piece [WEBDL 1080p HEVC]/Horimiya - Piece - 01 (WEBDL 1080p HEVC AAC) Ukr DVO SUB.mkv

## Configs

* ### app.ini
	```ini
	[Transmission]
	username = Імя користувача
	password = Пароль
	port = 9091
	host = localhost
	protocol = http
	rpc = /transmission/rpc
	
	[Jackett]
	url = https://domain.com # Посилання на Jacket
	api_key = ... # API Ключ
	```
* ### titles.ini
	```ini
	[zom]
	name = Zom 100: Список справ майбутнього зомбі (05 з 12) / Zom 100: Zombie ni Naru made ni Shitai 100 no Koto (2023) WEBRip 1080p H.265 Ukr/Jap | sub Ukr
	episode_number = 7
	season_number = 1
	ext_name = .mkv
	torrent_name = Zom 100: Zombie ni Naru made ni Shitai 100 no Koto (2023)
	download_dir = /media/HDD/Jellyfin/Anime
	publishdate = 2023-08-15T00:00:00
	
	[horimia]
	name = Хорімія. Фрагменти (серії 01-08 з 12) / Horimiya: Piece (2023) WEB-DL 1080p H.265 Ukr/Jap | Sub Ukr
	episode_number = 1
	season_number = 1
	ext_name = .mkv
	torrent_name = Horimiya - The Missing Pieces
	download_dir = /media/HDD/Jellyfin/Anime
	publishdate = 2023-08-20T00:00:00

	```
	
> [zom] - Коднейм

> episode_number - Вказуємо індекс, звідки брати номер епізоду

> season_number - Просто номер сезону, не індекс

> ext_name - Формат файлу

> torrent_name - Повне ім'я торрента (директорії) в Transmission

> download_dir - Директорія, куди буде скачаний медіа

> publishdate - Системне значення, за яким визначаємо, оновився торрент за час чи ні
	
## Authors

- [@CakesTwix](https://www.github.com/CakesTwix)

## License

- [GPL-v3](https://choosealicense.com/licenses/gpl-3.0/)

