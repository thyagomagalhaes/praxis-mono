CREATE TABLE public.tb_estado (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    source_id bigint NOT NULL UNIQUE,
    pais_id uuid NOT NULL REFERENCES public.tb_pais(id),
    nome varchar(255) NOT NULL,
    sigla varchar(255), populacao text,
    latitude numeric(10,8), longitude numeric(11,8),
    geom geometry(Point,4326),
    CONSTRAINT ck_tb_estado_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_tb_estado_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT uq_tb_estado_id_pais UNIQUE (id, pais_id)
);

-- GiST spatial indexes
CREATE INDEX ix_tb_estado_geom_gist ON public.tb_estado USING gist (geom);

-- B-Tree indexes on UUIDv7 foreign keys (PostgreSQL does not create these automatically)
CREATE INDEX ix_tb_estado_pais_id_btree ON public.tb_estado USING btree (pais_id);
