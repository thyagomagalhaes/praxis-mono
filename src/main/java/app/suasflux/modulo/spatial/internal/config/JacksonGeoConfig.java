package app.suasflux.modulo.spatial.internal.config;

import com.bedatadriven.jackson.datatype.jts.JtsModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JacksonGeoConfig {

 @Bean
 public JtsModule jtsModule() {
     return new JtsModule();
 }
}

//Dessa forma, quando a sua API retornar uma entidade com Point, o Spring irá gerar um 
//JSON no formato padrão GeoJSON:
//
//{
//	  "id": 1,
//	  "nome": "Marco Zero Recife",
//	  "localizacao": {
//	    "type": "Point",
//	    "coordinates": [-34.8813, -8.0539]
//	  }
//}