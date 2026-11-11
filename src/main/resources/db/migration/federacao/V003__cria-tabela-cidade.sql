CREATE TABLE public.tb_cidade (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    source_id bigint NOT NULL UNIQUE,
    pais_id uuid NOT NULL REFERENCES public.tb_pais(id),
    estado_id uuid,
    nome varchar(255) NOT NULL,
    tipo varchar(191), populacao bigint,
    latitude numeric(10,8) NOT NULL, longitude numeric(11,8) NOT NULL,
    geom geometry(Point,4326) NOT NULL,
    CONSTRAINT ck_tb_cidade_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_tb_cidade_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT fk_tb_cidade_estado_pais FOREIGN KEY (estado_id, pais_id)
        REFERENCES public.tb_estado (id, pais_id)
);


-- GiST spatial indexes
CREATE INDEX ix_tb_cidade_geom_gist ON public.tb_cidade USING gist (geom);

-- B-Tree indexes on UUIDv7 foreign keys (PostgreSQL does not create these automatically)
CREATE INDEX ix_tb_cidade_pais_id_btree ON public.tb_cidade USING btree (pais_id);
CREATE INDEX ix_tb_cidade_estado_id_btree ON public.tb_cidade USING btree (estado_id);