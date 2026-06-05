"""
test_task_manager.py: Testovací sada pro aplikaci Task Manager.

Obsahuje pozitivní i negativní testovací scénáře pro hlavní 
databázové operace: přidání, aktualizaci a odstranění úkolu.
Testy využívají k běhu dočasnou testovací databázi.
"""

import pytest
from unittest.mock import patch
import main

# Konfigurace namířená na testovací databázi (heslo si bere z .env přes tvůj main.py)
TEST_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': main.DB_CONFIG['password'],
    'database': 'task_manager_test_db'
}

@pytest.fixture(autouse=True)
def priprava_databaze():
    """Před každým testem vytvoří tabulku a po testu ji smaže (vyčištění dat)."""
    with patch('main.DB_CONFIG', TEST_DB_CONFIG):
        main.vytvoreni_tabulky()
        yield
        conn = main.pripojeni_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS ukoly")
            conn.commit()
            cursor.close()
            conn.close()


def pomocne_vlozeni_ukolu(nazev, popis):
    """Pomocná funkce pro rychlé vložení úkolu do testovací DB a vrácení jeho ID."""
    with patch('main.DB_CONFIG', TEST_DB_CONFIG):
        conn = main.pripojeni_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
        conn.commit()
        ukol_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return ukol_id


# --- TESTY PRO PŘIDÁNÍ ÚKOLU ---

@patch('builtins.input', side_effect=['Nákup', 'Koupit mléko'])
def test_pridat_ukol_pozitivni(mock_input):
    with patch('main.DB_CONFIG', TEST_DB_CONFIG):
        main.pridat_ukol()
        
        conn = main.pripojeni_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ukoly")
        vysledek = cursor.fetchall()
        cursor.close()
        conn.close()
        
        assert len(vysledek) == 1
        assert vysledek[0]['nazev'] == 'Nákup'
        assert vysledek[0]['stav'] == 'Nezahájeno'


@patch('builtins.input', side_effect=['', 'Platný název', 'Platný popis'])
def test_pridat_ukol_negativni(mock_input, capsys):
    """Ověřuje chování programu při zadání prázdného názvu úkolu."""
    with patch('main.DB_CONFIG', TEST_DB_CONFIG):
        main.pridat_ukol()
        vypis = capsys.readouterr().out
        assert "Název nesmí být prázdný" in vypis


# --- TESTY PRO AKTUALIZACI ÚKOLU ---

def test_aktualizovat_ukol_pozitivni():
    id_ukolu = pomocne_vlozeni_ukolu("Programování", "Napsat testy")
    
    with patch('builtins.input', side_effect=[str(id_ukolu), 'Hotovo']):
        with patch('main.DB_CONFIG', TEST_DB_CONFIG):
            main.aktualizovat_ukol()
            
    conn = main.pripojeni_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (id_ukolu,))
    novy_stav = cursor.fetchone()['stav']
    cursor.close()
    conn.close()
    
    assert novy_stav == 'Hotovo'


@patch('builtins.input', side_effect=['99', 'Hotovo'])
def test_aktualizovat_ukol_negativni(mock_input, capsys):
    """Ověřuje chování programu při pokusu o aktualizaci úkolu s neexistujícím ID."""
    pomocne_vlozeni_ukolu("Existující úkol", "Popis")
    
    with patch('main.DB_CONFIG', TEST_DB_CONFIG):
        main.aktualizovat_ukol()
        vypis = capsys.readouterr().out
        assert "Neplatné ID úkolu" in vypis


# --- TESTY PRO ODSTRANĚNÍ ÚKOLU ---

def test_odstranit_ukol_pozitivni():
    id_ukolu = pomocne_vlozeni_ukolu("Smazat mě", "Tento úkol zmizí")
    
    with patch('builtins.input', side_effect=[str(id_ukolu)]):
        with patch('main.DB_CONFIG', TEST_DB_CONFIG):
            main.odstranit_ukol()
            
    conn = main.pripojeni_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (id_ukolu,))
    vysledek = cursor.fetchone()
    cursor.close()
    conn.close()
    
    assert vysledek is None # Úkol by už neměl existovat


@patch('builtins.input', side_effect=['slovo_místo_čísla'])
def test_odstranit_ukol_negativni(mock_input, capsys):
    """Ověřuje chování programu při zadání textu namísto celočíselného ID."""
    pomocne_vlozeni_ukolu("Nějaký úkol", "Popis")
    
    with patch('main.DB_CONFIG', TEST_DB_CONFIG):
        main.odstranit_ukol()
        vypis = capsys.readouterr().out
        assert "Zadáno neplatné číslo" in vypis