-- The supplied dump is counties.sql; source counties are loaded into tb_cidade as requested.
-- Country and state UUIDv7 FKs are resolved through retained source IDs.
INSERT INTO public.tb_cidade (source_id, pais_id, estado_id, nome, tipo, populacao, latitude, longitude, geom)
SELECT v.source_id, p.id, e.id, v.nome, v.tipo, v.populacao, v.latitude, v.longitude,
       ST_SetSRID(ST_MakePoint(v.longitude, v.latitude), 4326)::geometry(Point,4326)
FROM (VALUES

) AS v(source_id, source_country_id, source_state_id, nome, tipo, populacao, latitude, longitude)
JOIN public.tb_pais p ON p.source_id=v.source_country_id
LEFT JOIN public.tb_estado e ON e.source_id=v.source_state_id
ON CONFLICT (source_id) DO UPDATE SET pais_id=EXCLUDED.pais_id, estado_id=EXCLUDED.estado_id, nome=EXCLUDED.nome,
 tipo=EXCLUDED.tipo, populacao=EXCLUDED.populacao, latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude, geom=EXCLUDED.geom;