import os
import json
import zipfile
from subprocess import Popen, PIPE
from http.server import BaseHTTPRequestHandler, HTTPServer

os.system('color')
ROOT = os.path.dirname(os.path.realpath(__file__))
APP_ARGS = [f'{ROOT}\\nfc\\nfc-mfultralight.exe', 'w', f'{ROOT}\\card.mfd', '--full']


def modify_dump(uuid: str) -> None:
    with open(f'{ROOT}\card.mfd', 'r+b', buffering=0) as cardDump:
        cardDump.seek(0x1C)
        cardDump.write(uuid.encode('ascii'))


def nfc_write() -> None:
    with Popen(APP_ARGS, stdout=PIPE, stderr=PIPE, shell=False, cwd=f'{ROOT}\\nfc') as app:
        app.wait()
        if app.returncode == 0:
            print(f'{Font.BRIGHT_GREEN}Метка перезаписана!{Font.RESET}')
        else:
            print(f'{Font.BRIGHT_RED}Ошибка записи!{Font.RESET}')


def get_walkdowns():
    for root, dirs, files in os.walk(ROOT):
        for file in files:
            if f'outpack.zip' in file:
                if zipfile.is_zipfile(f'{ROOT}\\{file}'):
                    print(f'{Font.BRIGHT_YELLOW}Найден архив{Font.RESET}:\t\t{file}')
                    zipArchive = zipfile.ZipFile(f'{ROOT}\\{file}', 'r')
                    for zipFile in zipArchive.namelist():
                        if f'walkdowns.json' in zipFile:
                            print(f'{Font.BRIGHT_YELLOW}Найден файл{Font.RESET}:\t\t{zipFile}')
                            return zipArchive.read(zipFile)


def generate_data():
    wd = json.loads(get_walkdowns())
    if f'walkdowns' in wd:
        nfc_data = []
        print(f'{Font.BRIGHT_YELLOW}Найдено обходов{Font.RESET}:\t{len(wd["walkdowns"])}')

        for walkdown in wd['walkdowns']:
            nfc_data.append({'walkdownId': walkdown["id"], 'walkdownName': walkdown["name"], 'walkdownTime': walkdown["estimatedTime"], 'walkdownPoints': []})

        for event in wd['walkdownEvents']:
            if event['eventType'] == 7:
                eventComments = event["systemComment"].split(';')
                pointName = None
                pointId = None
                for commentLine in eventComments:
                    if f'Наименование оборудования:' in commentLine:
                        pointName = commentLine.replace(f'Оборудование выбрано с помощью метки. Наименование оборудования: ', '')
                    if f'идентификатор метки:' in commentLine:
                        pointId = commentLine.replace(f' идентификатор метки: ', '')

                for i, walkData in enumerate(nfc_data):
                    if walkData['walkdownId'] == event['walkdownId']:
                        nfc_data[i]['walkdownPoints'].append({'pointId': pointId, 'pointName': pointName})

        nfc_data = sorted(nfc_data, key=lambda k: k['walkdownName'])

        print(f'{Font.RED}{"Точек".center(8)}{Font.RESET}{Font.GREEN}{"Время".center(10)}{Font.RESET}{Font.BLUE}{"Описание маршрута".ljust(20)}{Font.RESET}')
        for wdData in nfc_data:
            print(f'{Font.BRIGHT_RED}{str(len(wdData["walkdownPoints"])).center(8)}{Font.RESET}{Font.BRIGHT_GREEN}{str(wdData["walkdownTime"]).center(10)}{Font.RESET}{Font.BRIGHT_BLUE}{wdData["walkdownName"].ljust(20)}{Font.RESET}')
        return nfc_data


def generate_page(nfc_data):
    template_index = open(f'{ROOT}/www/index.tpl', 'rb').read().decode('utf-8')
    template_table = open(f'{ROOT}/www/table.tpl', 'rb').read().decode('utf-8')
    template_point = open(f'{ROOT}/www/point.tpl', 'rb').read().decode('utf-8')

    walkdowns_html = ''
    for walkdown in nfc_data:
        temp_walkdown = template_table
        temp_walkdown = temp_walkdown.replace(f'$WALKDOWN_NAME$', f'{walkdown["walkdownName"]}')
        points_html = ''
        for i, point in enumerate(walkdown['walkdownPoints']):
            temp_point = template_point
            temp_point = temp_point.replace(f'$POINT_NUMBER$', f'{(i + 1):02d}')
            temp_point = temp_point.replace(f'$POINT_NAME$', f'{point["pointName"]}')
            temp_point = temp_point.replace(f'$POINT_ID$', f'{point["pointId"]}')
            points_html += temp_point
        temp_walkdown = temp_walkdown.replace(f'$POINT_RECORDS$', f'{points_html}')
        walkdowns_html += temp_walkdown
    template_index = template_index.replace(f'$WALKDOWN_TABLES$', f'{walkdowns_html}')
    return bytes(template_index, 'utf-8')


class Font():
    RESET = '\033[0m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    BRIGHT_BLACK = '\033[0;90m'
    BRIGHT_RED = '\033[0;91m'
    BRIGHT_GREEN = '\033[0;92m'
    BRIGHT_YELLOW = '\033[0;93m'
    BRIGHT_BLUE = '\033[0;94m'
    BRIGHT_MAGENTA = '\033[0;95m'
    BRIGHT_CYAN = '\033[0;96m'
    BRIGHT_WHITE = '\033[0;97m'


class WebServer(BaseHTTPRequestHandler):
    nfc_data = generate_data()

    def do_GET(self):
        if self.path == '/':
            filename = f'{ROOT}/www/index.html'
        else:
            filename = f'{ROOT}/www{self.path}'

        self.send_response(200)
        if filename[-4:] == '.css':
            self.send_header('Content-type', 'text/css')
        elif filename[-3:] == '.js':
            self.send_header('Content-type', 'application/javascript')
        elif filename[-4:] == '.ico':
            self.send_header('Content-type', 'image/x-icon')
        elif filename[-5:] == '.html':
            self.send_header('Content-type', 'text/html')
        self.end_headers()

        if filename[-5:] == '.html':
            try:
                self.wfile.write(generate_page(self.nfc_data))
            except ConnectionAbortedError:
                pass
        else:
            with open(filename, 'rb') as fh:
                content = fh.read()
                self.wfile.write(content)

    def do_POST(self):
        if self.headers['Content-Type'] == 'application/json':
            self.send_response(200)
            self.end_headers()
            data = self.rfile.read(int(self.headers['Content-Length']))
            point = json.loads(data)
            print(f'{Font.BRIGHT_YELLOW}Выбрана точка{Font.RESET}: {Font.BRIGHT_RED}{point["number"]}{Font.RESET} ... ', end='')
            modify_dump(point['id'])
            nfc_write()
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    #webbrowser.register('chrome', None, webbrowser.BackgroundBrowser('C://Program Files//Google//Chrome//Application//chrome.exe'))
    #webbrowser.get('chrome').open('http://localhost:8080')
    #print(f'{Font.BRIGHT_YELLOW}Перезапустите страницу браузера{Font.RESET}')
    print(f'{Font.BRIGHT_YELLOW}Откройте в браузере{Font.RESET}: http://127.0.0.1:8080/')
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, WebServer)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    main()
