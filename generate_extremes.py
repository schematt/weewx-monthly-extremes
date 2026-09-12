#!/usr/bin/env python3
"""
Genera JSON con estremi mensili da file NOAA WeeWX (2020-2025)
Eseguire via cron domenicale
"""

import json
import re
from pathlib import Path
from collections import defaultdict

NOAA_DIR = Path("/var/www/html/weewx/noaa")
OUTPUT_FILE = Path("/var/www/html/weewx/extremes-2020-2025.json")

MONTHS = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
          "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

def parse_noaa_file(filepath):
    """Parseggia file NOAA WeeWX e restituisce dati giornalieri"""
    data = defaultdict(list)  # {month_idx: [(year, high, low), ...]}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Errore lettura {filepath}: {e}")
        return data
    
    # Estrai anno dal nome file (NOAA-YYYY-MM.txt)
    filename = filepath.name
    year_match = re.search(r'(\d{4})-(\d{2})', filename)
    if not year_match:
        return data
    
    year = int(year_match.group(1))
    month_idx = int(year_match.group(2)) - 1  # 0-11
    
    # Parseggia sezione dati
    in_data = False
    for line in text.split('\n'):
        if 'DAY' in line and 'HIGH' in line:
            in_data = True
            continue
        
        if not in_data or not line.strip():
            continue
        
        if '---' in line:
            continue
        
        # Parseggia riga dati
        # Formato: DAY TEMP HIGH TIME LOW TIME ...
        parts = line.split()
        if len(parts) < 5:
            continue
        
        try:
            day = int(parts[0])
            if day < 1 or day > 31:
                continue
            
            high = float(parts[2])
            low = float(parts[4])
            
            data[month_idx].append((year, high, low))
        except (ValueError, IndexError):
            continue
    
    return data

def generate_extremes():
    """Legge file NOAA 2020-2026 (incluso parziale) e genera extremes.json"""
    monthly_data = defaultdict(lambda: {"temps": []})
    
    # Leggi tutti i file NOAA 2020-2026
    for noaa_file in sorted(NOAA_DIR.glob("NOAA-202[0-6]-*.txt")):
        data = parse_noaa_file(noaa_file)
        for month_idx, temps in data.items():
            monthly_data[month_idx]["temps"].extend(temps)
    
    # Leggi anche i file annuali (es. NOAA-2026.txt) per completare l'anno parziale
    for noaa_file in sorted(NOAA_DIR.glob("NOAA-202[0-6].txt")):
        data = parse_noaa_file(noaa_file)
        for month_idx, temps in data.items():
            # Evita duplicati: se il mese esiste già, non aggiungere
            existing_years = {t[0] for t in monthly_data[month_idx]["temps"]}
            monthly_data[month_idx]["temps"].extend([t for t in temps if t[0] not in existing_years])
    
    # Calcola estremi per ogni mese
    output = []
    for month_idx in range(12):
        if month_idx not in monthly_data or not monthly_data[month_idx]["temps"]:
            continue
        
        temps = monthly_data[month_idx]["temps"]
        
        # Estrai T.min e T.max assolute
        min_temp = min(t[2] for t in temps)
        max_temp = max(t[1] for t in temps)
        min_year = next(t[0] for t in temps if t[2] == min_temp)
        max_year = next(t[0] for t in temps if t[1] == max_temp)
        
        # Calcola medie
        avg_min = sum(t[2] for t in temps) / len(temps)
        avg_max = sum(t[1] for t in temps) / len(temps)
        
        output.append({
            "month": MONTHS[month_idx],
            "month_idx": month_idx + 1,
            "min_temp": round(min_temp, 1),
            "min_year": min_year,
            "max_temp": round(max_temp, 1),
            "max_year": max_year,
            "avg_min": round(avg_min, 1),
            "avg_max": round(avg_max, 1),
            "years_count": len(set(t[0] for t in temps))
        })
    
    # Salva JSON
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON generato: {OUTPUT_FILE}")
        print(f"  Mesi processati: {len(output)}")
    except Exception as e:
        print(f"✗ Errore salvataggio JSON: {e}")

if __name__ == "__main__":
    generate_extremes()
