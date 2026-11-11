package app.suasflux.modulo.setorial;

import org.springframework.modulith.ApplicationModule;
import org.springframework.stereotype.Component;
import app.suasflux.modulo.iam.UsuarioSsoCriadoEvent;

//Módulo de Negócio que consome o evento ()
@Component
public class TrabalhadorSuasEventListener {
	
	@ApplicationModule
    public void on(UsuarioSsoCriadoEvent event) {
        // Cria uma representação local do cliente sem fazer chamada HTTP ao Keycloak
        System.out.println("Criando perfil do cliente a partir do Keycloak ID: " + event.keycloakId());
    }

}
