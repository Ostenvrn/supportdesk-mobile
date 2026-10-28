# app/core/terminal_emulator.py
#
# Эмулятор командной строки Windows для «Свободного терминала».
# Генерирует реалистичный вывод для базовых сетевых команд.

import random
import re
from datetime import datetime


def execute_command(command: str) -> str:
    """
    Принимает строку команды и возвращает текст, который выдала бы Windows.
    """
    cmd = command.strip().lower()
    
    if not cmd:
        return ""
    
    # --- PING ---
    if cmd.startswith("ping "):
        target = command.split(" ", 1)[1].strip()
        return _emulate_ping(target)
    
    # --- TRACERT ---
    if cmd.startswith("tracert ") or cmd.startswith("traceroute "):
        target = command.split(" ", 1)[1].strip()
        return _emulate_tracert(target)
    
    # --- IPCONFIG ---
    if cmd == "ipconfig":
        return _emulate_ipconfig()
    elif cmd == "ipconfig /all":
        return _emulate_ipconfig_all()
    elif cmd == "ipconfig /flushdns":
        return "Windows IP Configuration\n\nSuccessfully flushed the DNS Resolver Cache."
    elif cmd == "ipconfig /release":
        return "Windows IP Configuration\n\nEthernet adapter Ethernet:\n\n   Connection-specific DNS Suffix  . :\n   Link-local IPv6 Address . . . . . : fe80::a1b2:c3d4:e5f6:7890%10\n   Default Gateway . . . . . . . . . :"
    elif cmd == "ipconfig /renew":
        return "Windows IP Configuration\n\nEthernet adapter Ethernet:\n\n   Connection-specific DNS Suffix  . :\n   IPv4 Address. . . . . . . . . . . : 192.168.1.105\n   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n   Default Gateway . . . . . . . . . : 192.168.1.1"
    
    # --- NSLOOKUP ---
    if cmd.startswith("nslookup "):
        target = command.split(" ", 1)[1].strip()
        return _emulate_nslookup(target)
    
    # --- NETSTAT ---
    if cmd == "netstat -an":
        return _emulate_netstat_an()
    elif cmd == "netstat -rn":
        return _emulate_netstat_rn()
    
    # --- ARP ---
    if cmd == "arp -a":
        return _emulate_arp()
    
    # --- TELNET (эмуляция проверки порта) ---
    if cmd.startswith("telnet "):
        parts = command.split(" ")
        if len(parts) >= 3:
            ip = parts[1]
            port = parts[2]
            return _emulate_telnet(ip, port)
        return "Неверный синтаксис. Используйте: telnet <IP> <порт>"
    
    # --- SYSTEMINFO ---
    if cmd == "systeminfo":
        return _emulate_systeminfo()
    
    # --- СПЕЦИАЛЬНЫЕ ---
    if cmd == "help":
        return (
            "Доступные команды:\n"
            "  ping <хост>       - Проверка доступности узла\n"
            "  tracert <хост>    - Трассировка маршрута\n"
            "  ipconfig          - Базовые настройки IP\n"
            "  ipconfig /all     - Полные настройки IP\n"
            "  ipconfig /flushdns - Очистка кэша DNS\n"
            "  ipconfig /release - Сброс IP\n"
            "  ipconfig /renew   - Обновление IP\n"
            "  nslookup <домен>  - Проверка DNS\n"
            "  netstat -an       - Активные подключения\n"
            "  arp -a            - Таблица ARP\n"
            "  telnet <IP> <порт> - Проверка порта\n"
            "  systeminfo        - Информация о системе\n"
            "  cls               - Очистить экран\n"
        )
    
    # --- НЕИЗВЕСТНАЯ КОМАНДА ---
    return f"'{command.split(' ')[0]}' не является внутренней или внешней командой."


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (Генераторы вывода) ---

def _get_fake_ip(host: str) -> str:
    """Генерирует псевдо-IP для неизвестного хоста."""
    if "ya.ru" in host or "yandex" in host:
        return "87.250.250.242"
    if "google" in host:
        return "142.250.74.46"
    if "gosuslugi" in host:
        return "109.207.15.14"
    if "8.8.8.8" in host:
        return "8.8.8.8"
    if "1.1.1.1" in host:
        return "1.1.1.1"
    if "192.168" in host:
        return host
    # Если это уже похоже на IP
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
        return host
    # Иначе генерируем
    return f"{random.randint(80, 220)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"


def _emulate_ping(target: str) -> str:
    ip = _get_fake_ip(target)
    times = [random.randint(10, 50) for _ in range(4)]
    
    result = f"Обмен пакетами с {target} [{ip}] с 32 байтами данных:\n"
    for t in times:
        result += f"Ответ от {ip}: число байт=32 время={t}мс TTL=117\n"
    
    result += f"\nСтатистика Ping для {ip}:\n"
    result += "    Пакетов: отправлено = 4, получено = 4, потеряно = 0\n"
    result += "    (0% потерь)\n"
    return result


def _emulate_tracert(target: str) -> str:
    ip = _get_fake_ip(target)
    result = f"Трассировка маршрута к {target} [{ip}]\nс максимальным числом прыжков 30:\n\n"
    
    # Генерируем 5 хопов
    for i in range(1, 6):
        hop_ip = f"10.0.{random.randint(1, 5)}.{random.randint(1, 254)}" if i < 5 else ip
        t1 = random.randint(1, 10)
        t2 = random.randint(1, 10)
        t3 = random.randint(1, 10)
        result += f"  {i:2d}    {t1:3d} ms    {t2:3d} ms    {t3:3d} ms  {hop_ip}\n"
    
    result += "\nТрассировка завершена."
    return result


def _emulate_ipconfig() -> str:
    return (
        "Windows IP Configuration\n\n"
        "Ethernet adapter Ethernet:\n\n"
        "   Connection-specific DNS Suffix  . : localdomain\n"
        "   Link-local IPv6 Address . . . . . : fe80::a1b2:c3d4:e5f6:7890%10\n"
        "   IPv4 Address. . . . . . . . . . . : 192.168.1.45\n"
        "   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n"
        "   Default Gateway . . . . . . . . . : 192.168.1.1\n"
    )


def _emulate_ipconfig_all() -> str:
    return (
        "Windows IP Configuration\n\n"
        "   Host Name . . . . . . . . . . . . : Support-PC\n"
        "   Primary Dns Suffix  . . . . . . . : \n"
        "   Node Type . . . . . . . . . . . . : Hybrid\n"
        "   IP Routing Enabled. . . . . . . . : No\n"
        "   WINS Proxy Enabled. . . . . . . . : No\n\n"
        "Ethernet adapter Ethernet:\n\n"
        "   Connection-specific DNS Suffix  . : localdomain\n"
        "   Description . . . . . . . . . . . : Realtek PCIe GbE Family Controller\n"
        "   Physical Address. . . . . . . . . : 00-1A-2B-3C-4D-5E\n"
        "   DHCP Enabled. . . . . . . . . . . : Yes\n"
        "   Autoconfiguration Enabled . . . . : Yes\n"
        "   Link-local IPv6 Address . . . . . : fe80::a1b2:c3d4:e5f6:7890%10(Preferred)\n"
        "   IPv4 Address. . . . . . . . . . . : 192.168.1.45(Preferred)\n"
        "   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n"
        "   Lease Obtained. . . . . . . . . . : 27 октября 2026 г. 14:30:00\n"
        "   Lease Expires . . . . . . . . . . : 28 октября 2026 г. 14:30:00\n"
        "   Default Gateway . . . . . . . . . : 192.168.1.1\n"
        "   DHCP Server . . . . . . . . . . . : 192.168.1.1\n"
        "   DNS Servers . . . . . . . . . . . : 8.8.8.8\n"
        "                                       8.8.4.4\n"
        "   NetBIOS over Tcpip. . . . . . . . : Enabled\n"
    )


def _emulate_nslookup(target: str) -> str:
    if "fail" in target or "invalid" in target:
        return (
            "╤хЁтхЁ:  UnKnown\n"
            "Address:  192.168.1.1\n\n"
            "*** UnKnown не удалось найти " + target + ": Non-existent domain"
        )
    
    ip = _get_fake_ip(target)
    return (
        "╤хЁтхЁ:  UnKnown\n"
        "Address:  192.168.1.1\n\n"
        "╚ь :     " + target + "\n"
        "Address:  " + ip + "\n"
    )


def _emulate_netstat_an() -> str:
    return (
        "Активные подключения\n\n"
        "  Имя    Локальный адрес        Внешний адрес          Состояние\n"
        "  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING\n"
        "  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING\n"
        "  TCP    192.168.1.45:139       0.0.0.0:0              LISTENING\n"
        "  TCP    192.168.1.45:49152     142.250.74.46:443      ESTABLISHED\n"
        "  TCP    192.168.1.45:49153     87.250.250.242:443     ESTABLISHED\n"
        "  TCP    192.168.1.45:49154     8.8.8.8:53             TIME_WAIT\n"
    )


def _emulate_netstat_rn() -> str:
    return (
        "===========================================================================\n"
        "Список интерфейсов\n"
        "  9...00 1a 2b 3c 4d 5e ......Realtek PCIe GbE Family Controller\n"
        "===========================================================================\n\n"
        "Активные маршруты:\n"
        "Сетевой адрес           Маска сети      Адрес шлюза       Интерфейс  Метрика\n"
        "          0.0.0.0          0.0.0.0      192.168.1.1    192.168.1.45     25\n"
        "        127.0.0.0        255.0.0.0         On-link         127.0.0.1    331\n"
        "      192.168.1.0    255.255.255.0         On-link      192.168.1.45    281\n"
    )


def _emulate_arp() -> str:
    return (
        "Интерфейс: 192.168.1.45 --- 0xa\n"
        "  Интернет-адрес      Физический адрес      Тип\n"
        "  192.168.1.1         00-1f-3a-4b-5c-6d     динамический\n"
        "  192.168.1.10        00-0c-29-ab-cd-ef     динамический\n"
        "  192.168.1.105       a4-b1-c1-d2-e3-f4     динамический\n"
        "  192.168.1.255       ff-ff-ff-ff-ff-ff     статический\n"
    )


def _emulate_telnet(ip: str, port: str) -> str:
    if port in ["80", "443"]:
        return f"Подключение к {ip}...Не удалось открыть подключение к этому узлу, на порт {port}\nСбой подключения."
    elif port == "5060":
        return f"Подключение к {ip}...Соединение установлено."
    else:
        return f"Подключение к {ip}...Сбой подключения."


def _emulate_systeminfo() -> str:
    return (
        "Имя узла:                   SUPPORT-PC\n"
        "Название ОС:                Microsoft Windows 10 Pro\n"
        "Версия ОС:                  10.0.19045 Н/Д Сборка 19045\n"
        "Изготовитель ОС:            Microsoft Corporation\n"
        "Тип системы:                x64-based PC\n"
        "Процессор(ы):               1 процессор(ы) установлено.\n"
        "                            [01]: Intel64 Family 6 Model 158 Stepping 10 GenuineIntel ~2592 МГц\n"
        "Полный объем физической памяти: 16 384 МБ\n"
        "Доступная физическая память: 8 192 МБ\n"
    )
