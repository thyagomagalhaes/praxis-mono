package app.suasflux.modulo.spatial.internal.domain;

import jakarta.persistence.*;
import org.locationtech.jts.geom.Polygon;

@Entity
@Table(name = "tb_bairro")
public class Bairro {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;

    // Polígono delimitando o perímetro da comunidade ou bairro
    @Column(columnDefinition = "geometry(Polygon, 4326)")
    private Polygon areaGeografica;

    // Getters e Setters
}