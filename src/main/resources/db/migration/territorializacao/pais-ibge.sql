 CREATE TABLE IF NOT EXISTS db_msterritorializacao.tb_pais (
        co_m49                      smallint     PRIMARY KEY,
        co_iso_alpha2               char(2),
        co_iso_alpha3               char(3),
        no_pais                     text         NOT NULL,
        co_regiao_m49               smallint,
        no_regiao                   text,
        co_subregiao_m49            smallint,
        no_subregiao                text,
        co_regiao_intermediaria_m49 smallint,
        no_regiao_intermediaria     text,
        geom                        geometry(MultiPolygon, 4326),
        dt_carga                    timestamptz  NOT NULL DEFAULT now()
 );
 
COMMENT ON TABLE db_msterritorializacao.tb_pais
  IS 'Países e Nações';

COMMENT ON COLUMN db_msterritorializacao.tb_pais.co_iso_alpha2
  IS 'ISO 3166-1 Alpha2';
    
    
 CREATE INDEX IF NOT EXISTS {ix_geom} ON db_msterritorializacao.tb_pais USING gist (geom);
 CREATE UNIQUE INDEX IF NOT EXISTS {ix_iso2} ON db_msterritorializacao.tb_pais (co_iso_alpha2) WHERE co_iso_alpha2 IS NOT NULL;