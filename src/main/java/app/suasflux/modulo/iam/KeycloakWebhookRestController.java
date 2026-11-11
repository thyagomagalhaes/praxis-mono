package app.suasflux.modulo.iam;

import org.springframework.context.ApplicationEventPublisher;
import org.springframework.web.bind.annotation.*;
import org.keycloak.events.admin.AdminEvent;

//End-Point que recebe os Webhooks do Keycloak
@RestController
@RequestMapping("/webhooks/keycloak")
public class KeycloakWebhookRestController {
    private final ApplicationEventPublisher events;

    public KeycloakWebhookRestController(ApplicationEventPublisher events) {
        this.events = events;
    }

    @PostMapping("/usuariosso-events")
    public void handleKeycloakUsuarioSsoCriado(@RequestBody KeycloakEventPayload payload) {
        // Dispara evento interno no Spring Modulith
        events.publishEvent(new UsuarioSsoCriadoEvent(
            payload.userId(), 
            payload.email(), 
            payload.firstName()
        ));
    }
}