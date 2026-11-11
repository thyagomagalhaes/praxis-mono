import os
import io
import json
import gzip
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def save_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"-> Salvo com sucesso: {filepath} ({os.path.getsize(filepath) / (1024*1024):.2f} MB)")

def download_paises():
    print("\n[1/3] Baixando lista global de Países...")
    urls = [
        "https://cdn.jsdelivr.net/gh/dr5hn/countries-states-cities-database@master/json/countries.json",
        "https://raw.githubusercontent.com/mledoze/countries/master/dist/countries.json",
        "https://restcountries.com/v3.1/all"
    ]
    for url in urls:
        try:
            print(f"Tentando: {url}...")
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code == 200:
                save_json("countries.json", res.json())
                return res.json()
        except Exception as e:
            print(f"[AVISO] Falha em {url}: {e}")
            continue
    raise RuntimeError("Não foi possível baixar os países.")

def download_estados():
    print("\n[2/3] Baixando lista global de Estados...")
    urls = [
        "https://cdn.jsdelivr.net/gh/dr5hn/countries-states-cities-database@master/json/states.json",
        "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json"
    ]
    for url in urls:
        try:
            print(f"Tentando: {url}...")
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code == 200:
                save_json("states.json", res.json())
                return
        except Exception as e:
            print(f"[AVISO] Falha em {url}: {e}")
            continue
    print("[ERRO] Não foi possível baixar os estados.")

def download_cidades_global(paises):
    print("\n[3/3] Baixando lista global de Cidades / Municípios...")
    
    # Tentativa 1: Arquivo GZ comprimido do Release Oficial (~15 MB comprimido / ~150 MB descomprimido)
    urls_gz = [
        "https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/cities.json.gz",
        "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/cities.json.gz"
    ]
    
    for url in urls_gz:
        try:
            print(f"Tentando baixar base unificada (.gz): {url}...")
            res = requests.get(url, headers=HEADERS, stream=True, timeout=120)
            if res.status_code == 200:
                buffer = io.BytesIO()
                for chunk in res.iter_content(chunk_size=65536):
                    if chunk:
                        buffer.write(chunk)
                buffer.seek(0)
                
                with gzip.GzipFile(fileobj=buffer, mode="rb") as gz_file:
                    data = json.load(gz_file)
                
                save_json("cities.json", data)
                print("-> Base global de cidades unificada salva com sucesso!")
                return
        except Exception as e:
            print(f"[AVISO] Falha ao baixar pacote GZ de {url}: {e}")

    # Fallback: Download individual por país se a base unificada falhar
    print("-> Baixando cidades por arquivos individuais de país...")
    os.makedirs(os.path.join(DATA_DIR, "countries"), exist_ok=True)
    
    iso_list = []
    for p in paises:
        iso2 = p.get("iso2") or p.get("cca2")
        if iso2:
            iso_list.append(iso2)

    for iso2 in iso_list:
        url = f"https://cdn.jsdelivr.net/gh/dr5hn/countries-states-cities-database@master/countries/{iso2}.json"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                filepath = os.path.join(DATA_DIR, "countries", f"{iso2}.json")
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(res.json(), f, ensure_ascii=False)
                print(f"  [OK] Cidades de {iso2} salvas.")
        except Exception:
            continue

if __name__ == "__main__":
    print("=" * 60)
    print("DOWNLOAD GLOBAL DE DADOS DE FEDERAÇÃO")
    print("=" * 60)
    paises = download_paises()
    download_estados()
    download_cidades_global(paises)
    print("\n" + "=" * 60)
    print("DOWNLOAD GLOBAL FINALIZADO! ARQUIVOS SALVOS EM ./data/")
    print("=" * 60)