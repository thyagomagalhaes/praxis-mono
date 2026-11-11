package app.suasflux.modulo.iam;

//Evento de Domínio Imutável
public record UsuarioSsoCriadoEvent(String keycloakId, String email, String name) {
}
