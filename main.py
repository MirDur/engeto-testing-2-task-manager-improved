#!/usr/bin/env python3
"""
main.py: čtvrtý projekt do kurzu 'Tester s Pythonem'
author: Miroslav Ďuriš

Popis:
Tento skript funguje jako jednoduchý správce úkolů (Task Manager) v příkazové řádce.
Umožňuje uživateli interaktivně spravovat seznam úkolů.

Hlavní funkce aplikace:
1. Přidání nového úkolu (vyžaduje název a popis).
2. Zobrazení všech aktuálních úkolů.
3. Odstranění úkolu podle jeho pořadového čísla.
4. Bezpečné ukončení programu.

Data jsou trvale ukládána v relační databázi MySQL.
"""

from typing import List, Dict
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Načtení proměnných ze souboru .env
load_dotenv()

# Konfigurační údaje pro připojení 
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'task_manager_db'
}

def pripojeni_db():
    """Vytvoří a vrátí připojení k MySQL databázi."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Chyba při připojování k MySQL: {e}")
    return None


def vytvoreni_tabulky():
    """Vytvoří tabulku 'ukoly', pokud ještě neexistuje."""
    conn = pripojeni_db()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # SQL dotaz pro vytvoření tabulky dle zadání
            sql_query = """
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(sql_query)
            conn.commit()
        except Error as e:
            print(f"Chyba při vytváření tabulky: {e}")
        finally:
            cursor.close()
            conn.close()


def zobrazit_nabidku() -> None:
    """Vypíše možnosti hlavního menu do konzole."""
    print("Správce úkolů - Hlavní menu")
    print("1. Přidat úkol")
    print("2. Zobrazit úkoly (jen probíhající a nezahájené)")
    print("3. Aktualizovat úkol")
    print("4. Odstranit úkol")
    print("5. Ukončit program")


def pridat_ukol() -> None:
    """Umožní uživateli zadat název a popis nového úkolu a uloží ho do databáze."""
    while True:
        nazev = input("\nZadejte název úkolu: ").strip()
        if not nazev:
            print("Název nesmí být prázdný. Zkuste to znovu.")
            continue

        popis = input("Zadejte popis úkolu: ").strip()
        if not popis:
            print("Popis nesmí být prázdný. Zkuste to znovu.")
            continue

        conn = pripojeni_db()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
                cursor.execute(sql, (nazev, popis))
                conn.commit()
                print(f"Úkol '{nazev}' byl přidán do databáze.\n")
            except Error as e:
                print(f"Chyba databáze: {e}")
            finally:
                cursor.close()
                conn.close()
        break


def zobrazit_ukoly() -> None:
    """Načte z databáze a vypíše všechny úkoly, které mají stav 'Nezahájeno' nebo 'Probíhá'."""
    conn = pripojeni_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Filtr podle zadání: pouze Nezahájeno a Probíhá
            sql_query = "SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('Nezahájeno', 'Probíhá')"
            cursor.execute(sql_query)
            ukoly = cursor.fetchall()
            
            if not ukoly:
                print("\nSeznam úkolů je prázdný.\n")
            else:
                print("\nSeznam úkolů:")
                for u in ukoly:
                    print(f"ID: {u['id']} | {u['nazev']} - {u['popis']} | Stav: {u['stav']}")
                print()
        except Error as e:
            print(f"Chyba databáze: {e}")
        finally:
            cursor.close()
            conn.close()


def aktualizovat_ukol() -> None:
    """Umožní uživateli změnit stav existujícího úkolu (Probíhá / Hotovo) podle jeho ID."""
    conn = pripojeni_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            sql_query = "SELECT id, nazev, stav FROM ukoly"
            cursor.execute(sql_query)
            ukoly = cursor.fetchall()
            
            if not ukoly:
                print("\nŽádné úkoly k aktualizaci.\n")
                return
                
            print("\nDostupné úkoly:")
            for u in ukoly:
                print(f"ID: {u['id']} | {u['nazev']} | Stav: {u['stav']}")
                
            try:
                id_ukolu = int(input("\nZadejte ID úkolu pro aktualizaci: "))
                
                # Kontrola existence ID
                cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
                if not cursor.fetchone():
                    print("Neplatné ID úkolu.\n")
                    return
                
                novy_stav = input("Zadejte nový stav (Probíhá / Hotovo): ").strip()
                if novy_stav not in ['Probíhá', 'Hotovo']:
                    print("Neplatný stav. Zrušeno.\n")
                    return
                    
                cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
                conn.commit()
                print(f"Stav úkolu ID {id_ukolu} aktualizován na '{novy_stav}'.\n")
                
            except ValueError:
                print("Chyba: Zadáno neplatné číslo (ID úkolu).\n")
        except Error as e:
            print(f"Chyba databáze: {e}")
        finally:
            cursor.close()
            conn.close()


def odstranit_ukol() -> None:
    """Umožní uživateli trvale smazat úkol z databáze na základě jeho ID."""
    conn = pripojeni_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            sql_query = "SELECT id, nazev FROM ukoly"
            cursor.execute(sql_query)
            ukoly = cursor.fetchall()
            
            if not ukoly:
                print("\nŽádné úkoly k odstranění.\n")
                return
                
            print("\nDostupné úkoly:")
            for u in ukoly:
                print(f"ID: {u['id']} | {u['nazev']}")
                
            try:
                id_ukolu = int(input("\nZadejte ID úkolu pro odstranění: "))
                
                # Zjištění názvu pro výpis a kontrola existence
                sql_query = "SELECT nazev FROM ukoly WHERE id = %s"
                cursor.execute(sql_query, (id_ukolu,))
                ukol = cursor.fetchone()
                
                if not ukol:
                    print("Neplatné ID úkolu.\n")
                    return
                    
                cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
                conn.commit()
                print(f"Úkol '{ukol['nazev']}' byl odstraněn.\n")
                
            except ValueError:
                print("Chyba: Zadáno neplatné číslo (ID úkolu).\n")
        except Error as e:
            print(f"Chyba databáze: {e}")
        finally:
            cursor.close()
            conn.close()


def hlavni_menu() -> None:
    while True:
        zobrazit_nabidku()
        volba = input("Vyberte možnost (1-5): ")

        if volba == '1':
            pridat_ukol()
        elif volba == '2':
            zobrazit_ukoly()
        elif volba == '3':
            aktualizovat_ukol()
        elif volba == '4':
            odstranit_ukol()
        elif volba == '5':
            print("\nKonec programu.")
            break
        else:
            print("Neplatná volba, prosím zadejte číslo 1-5.\n")


if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()