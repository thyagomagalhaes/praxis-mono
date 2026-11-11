package app.suasflux.modulo.spatial.internal.repository;
import app.suasflux.modulo.spatial.internal.domain.Bairro;

import org.locationtech.jts.geom.Geometry;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

//As consultas usam funções nativas do PostGIS (ST_Contains, ST_Buffer, ST_MakeLine, etc.):
public interface GeoRepository extends JpaRepository<Bairro, Long> {

    // 1. Verifica se um ponto (p.ex. cliente) está dentro da área do Bairro
    @Query(value = "SELECT b FROM Bairro b WHERE ST_Contains(b.areaGeografica, :ponto) = true")
    List<Bairro> buscarBairrosQueContemPonto(@Param("ponto") Geometry ponto);

    // 2. Cria um Buffer (Raio de atuação circular em metros) em volta de um ponto de serviço
    @Query(value = "SELECT ST_AsText(ST_Buffer(:ponto::geography, :distanciaMetros)::geometry)", nativeQuery = true)
    String gerarRaioBufferWKT(@Param("ponto") Geometry ponto, @Param("distanciaMetros") double distanciaMetros);

    // 3. Traça uma Rota em Linha Reta entre dois pontos
    @Query(value = "SELECT ST_AsText(ST_MakeLine(:origem, :destino))", nativeQuery = true)
    String criarLinhaRetaWKT(@Param("origem") Geometry origem, @Param("destino") Geometry destino);

    // 4. Exemplo de Rota Complexa/Manhattan (Caminho via rede viária se integrado com pgRouting)
    @Query(value = "SELECT ST_AsText(ST_Simplify(ST_LineMerge(:geometriaComplexa), 0.0001))", nativeQuery = true)
    String simplificarRotaComplexa(@Param("geometriaComplexa") Geometry geometriaComplexa);
}
