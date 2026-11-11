package app.suasflux.modulo.spatial.internal.domain;

import jakarta.persistence.*;
import org.locationtech.jts.geom.Point;

@Entity
@Table(name = "tb_localidade")
public class Localidade {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;

    // Ponto em coordenadas WGS84 (SRID 4326 - Latitude/Longitude padrão GPS)
    @Column(columnDefinition = "geometry(Point, 4326)")
    private Point ponto;

    private Double raioAtuacaoMetros; // Raio de serviço

    // Getters e Setters
}
