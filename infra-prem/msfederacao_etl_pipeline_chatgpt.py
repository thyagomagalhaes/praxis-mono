import os
import json
import uuid6
import pandas as pd
import requests
from sqlalchemy import create_engine, text

# Configurações do Banco de Dados PostGIS
DB_USER = "postgres"
DB_PASS = "7f+gg62dOq3+2svhdJbUGapBoyymTiRTYylfZI+PJWw5IkrO"
DB_HOST = "127.0.0.1"
DB_PORT = "5431"
DB_NAME = "db_msfederacao"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

CACHE_DIR = os.path.join(os.path.dirname(__file__), "data")

def generate_uuid7():
    return str(uuid6.uuid7())

def reset_database(engine_instance):
    """Esvazia as tabelas de federação respeitando a integridade referencial via CASCADE."""
    print("\n[RESET] Limpando tabelas de federação...")
    truncate_query = text("TRUNCATE TABLE tb_pais RESTART IDENTITY CASCADE;")
    with engine_instance.begin() as conn:
        conn.execute(truncate_query)
    print("-> Tabelas `tb_pais`, `tb_estado` e `tb_municipio` limpas com sucesso!")

def create_indexes(engine_instance):
    """
    Cria índices B-Tree, GiST (espacial) e GIN (busca textual por trigram)
    após a carga dos dados, otimizando o planner com ANALYZE.
    """
    print("\n[INDEXAÇÃO] Criando índices B-Tree, GiST e GIN no PostGIS...")
    
    indexes_sql = """
        -- Habilita extensão para buscas por padrão textual (opcional)
        CREATE EXTENSION IF NOT EXISTS pg_trgm;

        -- 1. ÍNDICES TB_PAIS
        CREATE INDEX IF NOT EXISTS idx_tb_pais_nome ON tb_pais USING btree (nome);
        CREATE INDEX IF NOT EXISTS idx_tb_pais_iso2 ON tb_pais USING btree (codigo_iso2);
        CREATE INDEX IF NOT EXISTS idx_tb_pais_iso3 ON tb_pais USING btree (codigo_iso3);
        CREATE INDEX IF NOT EXISTS idx_tb_pais_geom ON tb_pais USING gist (geom);

        -- 2. ÍNDICES TB_ESTADO
        CREATE INDEX IF NOT EXISTS idx_tb_estado_id_pais ON tb_estado USING btree (id_pais);
        CREATE INDEX IF NOT EXISTS idx_tb_estado_nome ON tb_estado USING btree (nome);
        CREATE INDEX IF NOT EXISTS idx_tb_estado_codigo_uf ON tb_estado USING btree (codigo_uf);
        CREATE INDEX IF NOT EXISTS idx_tb_estado_geom ON tb_estado USING gist (geom);

        -- 3. ÍNDICES TB_MUNICIPIO
        CREATE INDEX IF NOT EXISTS idx_tb_municipio_id_estado ON tb_municipio USING btree (id_estado);
        CREATE INDEX IF NOT EXISTS idx_tb_municipio_nome ON tb_municipio USING btree (nome);
        CREATE INDEX IF NOT EXISTS idx_tb_municipio_ibge_iso ON tb_municipio USING btree (codigo_ibge_or_iso);
        CREATE INDEX IF NOT EXISTS idx_tb_municipio_geom ON tb_municipio USING gist (geom);
        CREATE INDEX IF NOT EXISTS idx_tb_municipio_nome_trgm ON tb_municipio USING gin (nome gin_trgm_ops);

        -- Atualiza estatísticas para o otimizador de consultas do PostgreSQL
        ANALYZE tb_pais;
        ANALYZE tb_estado;
        ANALYZE tb_municipio;
    """
    
    with engine_instance.begin() as conn:
        conn.execute(text(indexes_sql))
        
    print("-> Índices B-Tree, GiST e GIN criados e estatísticas atualizadas com sucesso!")

def load_local_json(filename):
    filepath = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}. Execute primeiro o script 'download_data_global.py'.")
    print(f"-> [CACHE LOCAL] Carregando {filename}...")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_etl_global():
    print("=" * 60)
    print("INICIANDO ETL GLOBAL DE FEDERAÇÃO (TODOS OS PAÍSES)")
    print("=" * 60)

    # Limpeza preventiva do banco
    reset_database(engine)

    # -------------------------------------------------------------------------
    # 1. PAÍSES (GLOBAL)
    # -------------------------------------------------------------------------
    print("\n[1/3] Processando Países...")
    raw_paises = load_local_json("countries.json")

    paises_list = []
    map_iso2_idpais = {}
    map_idcsc_idpais = {}

    for c in raw_paises:
        iso2 = c.get("iso2") or c.get("cca2")
        iso3 = c.get("iso3") or c.get("cca3")
        
        if not iso2:
            continue

        id_pais = generate_uuid7()
        id_csc = c.get("id")

        map_iso2_idpais[iso2] = id_pais
        if id_csc is not None:
            map_idcsc_idpais[id_csc] = id_pais

        translations = c.get("translations", {})
        if isinstance(translations, dict):
            pt_trans = translations.get("pt")
            if isinstance(pt_trans, dict):
                nome_pt = pt_trans.get("common") or pt_trans.get("official")
            else:
                nome_pt = pt_trans or c.get("name")
        else:
            nome_pt = c.get("name")

        if not nome_pt:
            nome_pt = c.get("name", iso2)

        paises_list.append({
            "id_pais": id_pais,
            "nome": nome_pt,
            "codigo_iso2": iso2,
            "codigo_iso3": iso3,
            "nacionalidade_masc": c.get("nationality"),
            "nacionalidade_fem": c.get("nationality"),
            "geom": None
        })

    df_paises = pd.DataFrame(paises_list).dropna(subset=['codigo_iso2']).drop_duplicates(subset=['codigo_iso2'])
    df_paises.to_sql('tb_pais', engine, if_exists='append', index=False, method='multi')
    print(f"-> Tabela `tb_pais` populada com {len(df_paises)} países do mundo.")

    # -------------------------------------------------------------------------
    # 2. ESTADOS (GLOBAL)
    # -------------------------------------------------------------------------
    print("\n[2/3] Processando Estados...")
    raw_estados = load_local_json("states.json")

    estados_list = []
    map_idcsc_idestado = {}
    map_code_country_idestado = {}

    for s in raw_estados:
        country_id = s.get("country_id")
        country_code = s.get("country_code")

        id_pais = map_idcsc_idpais.get(country_id) or map_iso2_idpais.get(country_code)
        if not id_pais:
            continue

        id_estado = generate_uuid7()
        id_csc_estado = s.get("id")
        state_code = s.get("state_code")

        if id_csc_estado is not None:
            map_idcsc_idestado[id_csc_estado] = id_estado
        if country_code and state_code:
            map_code_country_idestado[(country_code, state_code)] = id_estado

        estados_list.append({
            "id_estado": id_estado,
            "id_pais": id_pais,
            "nome": s.get("name"),
            "codigo_uf": state_code,
            "gentilico_masc": None,
            "gentilico_fem": None,
            "geom": None
        })

    df_estados = pd.DataFrame(estados_list)
    if not df_estados.empty:
        df_estados.to_sql('tb_estado', engine, if_exists='append', index=False, method='multi', chunksize=2000)
        print(f"-> Tabela `tb_estado` populada com {len(df_estados)} estados globalmente.")

    # -------------------------------------------------------------------------
    # 3. MUNICÍPIOS / CIDADES (GLOBAL COM TRÊS NÍVEIS DE FALLBACK)
    # -------------------------------------------------------------------------
    print("\n[3/3] Processando Municípios / Cidades Globais...")
    cidades_list = []

    cities_json_path = os.path.join(CACHE_DIR, "cities.json")
    countries_dir = os.path.join(CACHE_DIR, "countries")

    # Opção A: Arquivo local unificado 'cities.json'
    if os.path.exists(cities_json_path):
        raw_cidades = load_local_json("cities.json")
        for c in raw_cidades:
            state_id = c.get("state_id")
            state_code = c.get("state_code")
            country_code = c.get("country_code")

            id_estado = map_idcsc_idestado.get(state_id) or map_code_country_idestado.get((country_code, state_code))
            if not id_estado:
                continue

            cidades_list.append({
                "id_municipio": generate_uuid7(),
                "id_estado": id_estado,
                "nome": c.get("name"),
                "codigo_ibge_or_iso": str(c.get("id")),
                "gentilico_masc": None,
                "gentilico_fem": None,
                "geom": None
            })

    # Opção B: Arquivos locais na pasta 'data/countries/'
    elif os.path.exists(countries_dir) and len(os.listdir(countries_dir)) > 0:
        print("-> [CACHE LOCAL] Carregando cidades a partir da pasta ./data/countries/...")
        for filename in os.listdir(countries_dir):
            if filename.endswith(".json"):
                iso2 = filename.replace(".json", "")
                with open(os.path.join(countries_dir, filename), "r", encoding="utf-8") as f:
                    dados_pais = json.load(f)
                    for estado in dados_pais.get("states", []):
                        id_estado = map_idcsc_idestado.get(estado.get("id")) or \
                                    map_code_country_idestado.get((iso2, estado.get("state_code")))
                        if not id_estado:
                            continue

                        for c in estado.get("cities", []):
                            cidades_list.append({
                                "id_municipio": generate_uuid7(),
                                "id_estado": id_estado,
                                "nome": c.get("name"),
                                "codigo_ibge_or_iso": str(c.get("id")),
                                "gentilico_masc": None,
                                "gentilico_fem": None,
                                "geom": None
                            })

    # Opção C: Fallback remoto dinâmico via CDN
    else:
        print("-> [REMOTOS] Cache local de cidades ausente. Baixando por país via CDN...")
        headers = {"User-Agent": "Mozilla/5.0"}
        for iso2 in map_iso2_idpais.keys():
            url = f"https://cdn.jsdelivr.net/gh/dr5hn/countries-states-cities-database@master/countries/{iso2}.json"
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    dados_pais = res.json()
                    for estado in dados_pais.get("states", []):
                        id_estado = map_idcsc_idestado.get(estado.get("id")) or \
                                    map_code_country_idestado.get((iso2, estado.get("state_code")))
                        if not id_estado:
                            continue

                        for c in estado.get("cities", []):
                            cidades_list.append({
                                "id_municipio": generate_uuid7(),
                                "id_estado": id_estado,
                                "nome": c.get("name"),
                                "codigo_ibge_or_iso": str(c.get("id")),
                                "gentilico_masc