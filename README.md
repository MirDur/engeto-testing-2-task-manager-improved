# Vylepšený Task Manager s MySQL databází

Tento projekt je rozšířením konzolové aplikace Task Manager o ukládání dat do MySQL databáze. Projekt provádí základní CRUD operace (Create, Read, Update, Delete) a obsahuje automatizované testy pomocí frameworku `pytest`.

## Požadavky

* Python 3.x
* Spuštěný lokální MySQL server
* Nainstalované závislosti z `requirements.txt` (nebo ručně: `mysql-connector-python`, `python-dotenv`, `pytest`)

## Nastavení prostředí a databáze

1. **Databáze:** Než aplikaci spustíte, je nutné vytvořit v MySQL databáze ručně (tabulky si aplikace vytvoří sama):
```sql
CREATE DATABASE task_manager_db;
CREATE DATABASE task_manager_test_db;
```
2. **Přístupové údaje:** V kořenovém adresáři projektu si vytvořte soubor `.env` (můžete vycházet z přiloženého `.env.example`) a doplňte heslo ke svému lokálnímu MySQL root uživateli:
```text
DB_PASSWORD=vase_skutecne_heslo
```

## Spuštění aplikace

Hlavní aplikaci spustíte příkazem:
```shell
python main.py
```

## Automatizované testy

Projekt obsahuje sadu 6 automatizovaných testů (pozitivní i negativní scénáře) pro funkce přidávání (pridat_ukol()), aktualizace (aktualizovat_ukol()) a odstraňování úkolů (odstranit_ukol()). 
Testy využívají samostatnou testovací databázi `task_manager_test_db` a po svém proběhnutí po sobě testovací data mažou.

Testy spustíte příkazem:
```shell
pytest test_task_manager.py -v
```