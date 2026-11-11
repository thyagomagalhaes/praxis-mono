package app.suasflux.modulo.spatial;

import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.PrecisionModel;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/geo")
public class GeoRestController {

    private final GeometryFactory geometryFactory = new GeometryFactory(new PrecisionModel(), 4326);

    @GetMapping("/coordenadas-exemplo")
    public Map<String, Object> getExemploMapa() {
        // Exemplo: Recife/PE (-8.0476, -34.8770)
        double lat = -8.0476;
        double lng = -34.8770;

        return Map.of(
            "centro", new double[]{lat, lng},
            "raioMetros", 1500,
            "linhaReta", new double[][]{
                {lat, lng},
                {-8.0550, -34.8850}
            },
            "bairroPoligono", new double[][]{
                {-8.040, -34.880},
                {-8.040, -34.870},
                {-8.050, -34.870},
                {-8.050, -34.880},
                {-8.040, -34.880} // Fecha o polígono no ponto inicial
            }
        );
    }
}
