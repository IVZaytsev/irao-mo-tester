# irao-mo-tester
 Python-скрипт для проверки работоспособности считывающего устройства системы АИС "Мобильный обходчик".

## Описание
 Скрипт позволяет повторно записать NFC-метки маршрутов обхода в случае их повреждения или утраты. 
 
<img src="https://windowsonly.net/wp-content/uploads/2014/03/Windows-Only-Logo-New-800px.png" width="400">

## Требования
 * Операционная система: Microsoft Windows 10
 * Считыватель NFC-меток PN532, подключенный через USB-TTL переходник
 * Выгруженный архив с обходами АИС "Мобильный Обходчик" формата **[Обходы_XX-XX-XXXX_XX-XX-XX-XXX]-outpack.zip**
 * Стандартные библиотеки Python 3.9:
   * json
   * zipfile
   * subprocess
   * http.server

## Используемые программы
 * Библиотека [LibUSB](https://github.com/libusb/libusb) [v1.0.24];
 * Приложение **nfc-mfultralight.exe** из пакета [LibNFC](https://github.com/nfc-tools/libnfc) [v1.8.0]. Были сделаны изменения:
    * Изменен путь к файлу конфигурации *libnfc.conf*
    * Убраны лишние подтверждения при записи образа NFC-метки

## Подготовка к работе
1. [Скачайте](https://github.com/IVZaytsev/irao-mo-tester/archive/refs/heads/main.zip) и разархивируйте скрипт.
2. С переносного устройства АИС "Мобильный обходчик" получите offline-архив для ручной загрузки на сервер:
    1. Пройдите требуемые маршруты
    2. Отключите устройство от мобильного Интернета
    3. Нажмите "Выгрузка данных" и дождитесь предложения об offline-загрузке
    4. С помощью USB-кабеля сохраните архив формата **[Обходы_XX-XX-XXXX_XX-XX-XX-XXX]-outpack.zip**
    5. Скопируйте архив с обходами в папку со скриптом */run.py*
3. Подготовьте устройство чтения-записи NFC-меток (PN532):
    1. Сам модуль PN532 без лишней пайки можно приобрести на AliExpress ([Здесь](https://aliexpress.ru/item/33015068066.html) или [Здесь](https://aliexpress.ru/item/1005001683334749.html)). Либо можно взять вариант для подключения с помощью HighSpeed UART (HSU) через переходник USB-TTL ([Здесь](https://aliexpress.ru/item/32798124562.html)).
    2. Подключите купленный\собранный прибор к ПК и установите нужные драйвера (лежат в папке */drivers*)
    3. Откройте Диспетчер устройств Windows и убедитесь, что PN532 есть в списке последовательных портов (COM3, COM4, COM5 и т.д.)
	<p align="center"><img src="https://github.com/IVZaytsev/irao-mo-tester/blob/main/readme/pn532.png?raw=true" alt="Модуль чтения NFC-меток PN532"/></p>
	
3. Запустите скрипт /run.py и убедитесь, что ваш архив был найден, а обходы загружены

<p align="center"><img src="https://github.com/IVZaytsev/irao-mo-tester/blob/main/readme/mo-tester-1.png?raw=true" alt="Корректная работа скрипта"/></p>

4. Перейдите по адресу [http://127.0.0.1:8080/](http://127.0.0.1:8080/):

<p align="center"><img src="https://github.com/IVZaytsev/irao-mo-tester/blob/main/readme/mo-tester-2.png?raw=true" alt="Веб-интерфейс"/></p>

5. Приложите пустую NFC-метку к устройству и на открывшейся странице нажмите кнопку '**Отправить**'

Если всё сделано правильно, вы получите копию нужной NFC-метки.
