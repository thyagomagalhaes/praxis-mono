CREATE TABLE public.tb_pais (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    source_id bigint NOT NULL UNIQUE,
    nome varchar(100) NOT NULL,
    iso2 char(2), iso3 char(3),
    populacao bigint,
    latitude numeric(10,8), longitude numeric(11,8),
    geom geometry(Point,4326),
    CONSTRAINT ck_tb_pais_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_tb_pais_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

-- GiST spatial indexes
CREATE INDEX ix_tb_pais_geom_gist ON public.tb_pais USING gist (geom);