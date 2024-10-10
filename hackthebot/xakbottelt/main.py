import telebot
from telebot import types
import nmap
import requests
import os
import subprocess
from TOKEN import VIRUSTOTAL_API_KEY
from TOKEN import  SHODAN_API_KEY
from TOKEN import GOOGLE_SAFE_BROWSING_API_KEY
from TOKEN import TOKEN 
import sqlite3
import threading

# Инициализация бота с вашим токеном
bot = telebot.TeleBot(TOKEN)
nm = nmap.PortScanner()
# Обработка команды /start

def get_free_proxies():
    response = requests.get('https://www.proxy-list.download/api/v1/get?type=https')
    if response.status_code == 200:
        return response.text.split('\r\n')
    else:
        return []
    
def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_to_db(user_id, username, first_name, last_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

def get_geoip_info(ip):
    try:
        response = requests.get(f'http://ipinfo.io/{ip}/json')
        data = response.json()
        if 'error' not in data:
            return data
        else:
            return None
    except Exception as e:
        return None


def perform_load_test(url, num_requests, num_threads):
    def load_test():
        for _ in range(num_requests):
            try:
                requests.get(url)
            except requests.RequestException as e:
                print(f"Request failed: {e}")

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=load_test)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    save_user_to_db(user_id, username, first_name, last_name)

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_start = types.InlineKeyboardButton("🌟 Начать", callback_data="start")
    btn_help = types.InlineKeyboardButton("❓ Помощь", callback_data="help")
    btn_scan = types.InlineKeyboardButton("🔍 Сканировать", callback_data="scan")
    btn_checkurl = types.InlineKeyboardButton("🛡️ Проверка URL", callback_data="checkurl")
    btn_geoip = types.InlineKeyboardButton("🌍 GeoIP", callback_data="geoip")
    btn_scan_vuln = types.InlineKeyboardButton("🛠️ Сканирование уязвимостей", callback_data="scan_vuln")
    btn_proxy = types.InlineKeyboardButton("Proxy", callback_data="proxy")
    btn_userinfo = types.InlineKeyboardButton("ℹ️ Информация о пользователе", callback_data="userinfo")
    btn_ddos = types.InlineKeyboardButton("🚀 Выполнить нагрузочное тестирование", callback_data="loadtest")
    markup.add(btn_start, btn_help, btn_scan, btn_checkurl, btn_geoip, btn_scan_vuln, btn_proxy, btn_userinfo,btn_ddos)
    
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать! Вот что я могу сделать для вас:\n"
        "🌟 Начать работу с ботом\n"
        "❓ Показать помощь\n"
        "🔍 Выполнить сканирование\n"
        "🛡️ Проверка URL на вирусы\n"
        "🌍 Найти человека по IP\n"
        "🛠️ Сканирование веб-сайта на уязвимости\n"
        "🔗 Получить список бесплатных прокси\n"
        "ℹ️ Получить информацию о пользователе\n"
        "🚀 Выполнить нагрузочное тестирование",
        
        reply_markup=markup
    )

# Обработка нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "start":
        bot.send_message(call.message.chat.id, "Вы начали работу с ботом.")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "❓ Показать помощь:\n"
                                               "/start - Начать работу с ботом\n"
                                               "/help - Показать это сообщение\n"
                                               "/scan - Выполнить сканирование\n"
                                               "/checkurl - Сканировать ссылки на вирусы\n"
                                               "/geoip - Найти человека по IP\n"
                                               "/scan_vuln - Сканировать веб-сайт на уязвимости\n"
                                              )
    elif call.data == "scan":
        bot.send_message(call.message.chat.id, 
                         "🔍 Отправь мне IP в таком виде для сканирования:\n"
                         "/scan 0.0.0.0")
        # Вызов функции для сканирования



    elif call.data == "userinfo":
        bot.send_message(call.message.chat.id,
                         "чтоб наити информацию о человеке напиши каманду\n"
                         "/userinfo @username")
        
    elif call.data == "checkurl":
        bot.send_message(call.message.chat.id, 
                        "🛡️ Проверка ссылки на вирусы\n"
                        "Отправь мне ссылку в таком виде:\n"
                        "/checkurl https://www.google.com/")
        # Вызов функции проверки URL
    elif call.data == "geoip":
        bot.send_message(call.message.chat.id, 
                        "🌍 Находим человека по IP\n"
                        "Отправь мне команду в таком виде:\n"
                        "/geoip 0.0.0.0")
        # Вызов функции GeoIP
    elif call.data == "scan_vuln":
        bot.send_message(call.message.chat.id, 
                        "🛠️ Запуск сканирования на уязвимости\n"
                        "Отправь мне команду в таком виде:\n"
                        "/scan_vuln https://www.google.com/")
        
    elif call.data == "proxy":
        bot.send_message(call.message.chat.id, 
                        "звпусти каманджо /proxy",)
        
    elif call.data == "loadtest":
        bot.send_message(call.message.chat.id, 
                         "🚀 Выполняем нагрузочное тестирование.\nОтправьте команду в формате:\n/perform_load_test http://example.com 10 5")
# Обработка команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Команды бота:\n"
                          "/start - Начать работу с ботом\n"
                          "/help - Показать это сообщение\n"
                          "/scan - Выполнить сканирование\n"
                          "/checkurl - сканирует силки на предмет вируса\n"
                          "/geoip - находит человека по IP\n"
                          "/scan_vuln - сканирует веб саит на уязвимость\n"
                          "/proxy - бесплание прокси")


@bot.message_handler(commands=['scan'])
def scan(message):
    video_nmap = './video/2024-08-21 06-23-32.mp4'
    
    # Отправка видео сразу после получения команды
    try:
        with open(video_nmap, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption='Пример')
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при отправке видео: {e}")

    # Обработка команды и выполнение сканирования
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите IP-адрес или домен для сканирования. Пример: /scan 192.168.0.104")
        return

    target = parts[1].strip()
    bot.reply_to(message, f"Запускаю сканирование для {target}...")

    try:
        # Выполнение сканирования
        nm.scan(hosts=target, arguments='-T4 -F')
        
        # Проверка наличия хостов и результатов
        if nm.all_hosts():
            result_message = "Результаты сканирования:\n"
            for host in nm.all_hosts():
                result_message += f"Host: {host}\n"
                result_message += f"State: {nm[host].state()}\n"
                result_message += "Ports:\n"
                if 'ports' in nm[host]:
                    for port in nm[host]['ports']:
                        result_message += f"  Port {port}: {nm[host]['ports'][port]['name']}\n"
                else:
                    result_message += "  Нет открытых портов\n"
            
            # Отправка сообщения с результатами сканирования
            if len(result_message) > 4096:
                result_message = result_message[:4096] + '... (результаты обрезаны)'
            bot.send_message(message.chat.id, result_message)
        else:
            bot.reply_to(message, "Нет результатов для сканирования.")
    
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при сканировании: {e}")


# Обработка команды /geoip
@bot.message_handler(commands=['geoip'])
def geoip_lookup(message):
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите IP-адрес для поиска. Пример: /geoip 8.8.8.8")
        return

    ip_address = parts[1].strip()
    bot.reply_to(message, f"Ищу геолокацию для {ip_address}...")

    geoip_info = get_geoip_info(ip_address)
    if geoip_info:
        result_message = (f"Информация о геолокации для {ip_address}:\n"
                          f"Страна: {geoip_info.get('country', 'N/A')}\n"
                          f"Регион: {geoip_info.get('region', 'N/A')}\n"
                          f"Город: {geoip_info.get('city', 'N/A')}\n"
                          f"Организация: {geoip_info.get('org', 'N/A')}\n"
                          f"Локация: {geoip_info.get('loc', 'N/A')}")
        bot.send_message(message.chat.id, result_message)
    else:
        bot.reply_to(message, "Не удалось получить информацию о геолокации. Пожалуйста, проверьте IP-адрес.")


def check_url_for_phishing(url):
    api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    params = {
        "key": GOOGLE_SAFE_BROWSING_API_KEY
    }
    json_data = {
        "client": {
            "clientId": "yourcompanyname",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    response = requests.post(api_url, params=params, json=json_data)
    result = response.json()

    # Если результат пустой, URL безопасен
    if not result.get('matches'):
        return "URL безопасен."
    else:
        return "Внимание! URL может быть фишинговым или опасным."

# Обработка команды /checkurl
@bot.message_handler(commands=['checkurl'])
def check_url(message):
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите URL для проверки. Пример: /checkurl http://example.com")
        return

    url = parts[1].strip()
    result = check_url_for_phishing(url)
    bot.reply_to(message, result)

@bot.message_handler(commands=['scan_vuln'])
def scan_vuln(message):
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите URL для сканирования. Пример: /scan_vuln http://example.com")
        return

    url = parts[1].strip()
    bot.reply_to(message, f"Запускаю сканирование на уязвимости для {url}...")

    try:
        # Запуск Nikto через subprocess
        result = subprocess.run(['nikto', '-h', url], capture_output=True, text=True)
        if result.returncode == 0:
            bot.reply_to(message.chat.id, f"Результаты сканирования:\n{result.stdout}")
        else:
            bot.reply_to(message.chat.id, f"Произошла ошибка при сканировании: {result.stderr}")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['proxy'])
def send_proxy_list(message):
    proxies = get_free_proxies()
    if proxies:
        proxy_message = "Вот список бесплатных прокси:\n"
        for proxy in proxies:
            proxy_message += f"{proxy}\n"
        bot.reply_to(message, proxy_message)
    else:
        bot.reply_to(message, "Не удалось получить список прокси. Попробуйте позже.")

@bot.message_handler(commands=['userinfo'])
def user_info(message):
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите юзернейм или ID пользователя. Пример: /userinfo username")
        return
    
    query = parts[1].strip()
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    if query.isdigit():
        cursor.execute("SELECT * FROM users WHERE user_id=?", (int(query),))
    else:
        cursor.execute("SELECT * FROM users WHERE username=?", (query,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, username, first_name, last_name = user
        info_message = (
            f"Информация о пользователе:\n"
            f"ID: {user_id}\n"
            f"Юзернейм: @{username if username else 'Не указан'}\n"
            f"Имя: {first_name if first_name else 'Не указано'}\n"
            f"Фамилия: {last_name if last_name else 'Не указана'}"
        )
        bot.reply_to(message, info_message)
    else:
        bot.reply_to(message, "Пользователь не найден в базе данных.")


@bot.message_handler(commands=['perform_load_test'])
def perform_load_test_command(message):
    parts = message.text.split(' ', 3)
    if len(parts) < 4:
        bot.reply_to(message, "Пожалуйста, укажите URL, количество запросов и количество потоков. Пример: /perform_load_test http://example.com 10 5")
        return

    url = parts[1].strip()
    try:
        num_requests = int(parts[2].strip())
        num_threads = int(parts[3].strip())
    except ValueError:
        bot.reply_to(message, "Количество запросов и потоков должны быть числами.")
        return

    bot.reply_to(message, f"Запускаем нагрузочное тестирование для {url} с {num_requests} запросами и {num_threads} потоками.")
    try:
        perform_load_test(url, num_requests, num_threads)
        bot.reply_to(message, "Нагрузочное тестирование завершено.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при выполнении нагрузочного тестирования: {e}")


if __name__ == '__main__':
    create_table()
    bot.polling()
