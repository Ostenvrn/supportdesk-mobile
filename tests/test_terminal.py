# tests/test_terminal.py

import pytest
from app.core.terminal_emulator import execute_command


class TestTerminalEmulator:
    """Тесты для эмулятора терминала."""

    def test_empty_command(self):
        """Пустая команда должна возвращать пустую строку."""
        assert execute_command("") == ""
        assert execute_command("   ") == ""

    def test_ping_8_8_8_8(self):
        """Проверка базового пинга."""
        result = execute_command("ping 8.8.8.8")
        assert "Обмен пакетами с 8.8.8.8" in result
        assert "Ответ от 8.8.8.8" in result
        assert "0% потерь" in result

    def test_ping_ya_ru(self):
        """Проверка пинга с доменным именем."""
        result = execute_command("ping ya.ru")
        assert "87.250.250.242" in result
        assert "Ответ от" in result

    def test_tracert(self):
        """Проверка трассировки."""
        result = execute_command("tracert ya.ru")
        assert "Трассировка маршрута к ya.ru" in result
        assert "Трассировка завершена." in result

    def test_ipconfig(self):
        """Проверка базового ipconfig."""
        result = execute_command("ipconfig")
        assert "IPv4 Address" in result
        assert "192.168.1.45" in result

    def test_ipconfig_all(self):
        """Проверка расширенного ipconfig /all."""
        result = execute_command("ipconfig /all")
        assert "Host Name" in result
        assert "DNS Servers" in result

    def test_nslookup(self):
        """Проверка nslookup."""
        result = execute_command("nslookup google.com")
        assert "Server:" in result or "Сервер:" in result
        assert "Address:" in result or "Address:" in result

    def test_nslookup_fail(self):
        """Проверка nslookup для несуществующего домена."""
        result = execute_command("nslookup fail.domain")
        assert "Non-existent domain" in result

    def test_netstat(self):
        """Проверка netstat -an."""
        result = execute_command("netstat -an")
        assert "LISTENING" in result
        assert "ESTABLISHED" in result

    def test_arp(self):
        """Проверка arp -a."""
        result = execute_command("arp -a")
        assert "192.168.1.1" in result
        assert "динамический" in result

    def test_telnet(self):
        """Проверка telnet."""
        result = execute_command("telnet 10.0.0.1 80")
        assert "Сбой подключения." in result

    def test_systeminfo(self):
        """Проверка systeminfo."""
        result = execute_command("systeminfo")
        assert "Microsoft Windows 10 Pro" in result
        assert "16 384 МБ" in result

    def test_help(self):
        """Проверка команды help."""
        result = execute_command("help")
        assert "Доступные команды:" in result
        assert "ping <хост>" in result

    def test_unknown_command(self):
        """Проверка неизвестной команды."""
        result = execute_command("blablabla")
        assert "не является внутренней или внешней командой" in result

    def test_case_insensitive(self):
        """Команды должны быть нечувствительны к регистру."""
        result1 = execute_command("PING 8.8.8.8")
        result2 = execute_command("ping 8.8.8.8")
        # Вывод может отличаться по времени, но структура должна быть одинаковой
        assert "Обмен пакетами" in result1
        assert "Обмен пакетами" in result2
