package app.suasflux.modulo.spatial.internal.domain;

import org.locationtech.jts.geom.Polygon;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "tb_subdistrito")
public class Subdistrito {
	
	@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;

    // Polígono delimitando o perímetro da área de abrangência da RPA
    @Column(columnDefinition = "geometry(Polygon, 4326)")
    private Polygon areaAbrangencia;
    
 // Polígono delimitando o perímetro da área de referência da RPA
    @Column(columnDefinition = "geometry(Polygon, 4326)")
    private Polygon areaReferencia;
    


    // Getters e Setters

}
