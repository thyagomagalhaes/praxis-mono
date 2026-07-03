package app.suasflux.modulo.integracao;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class LocalizacaoViaCepService {

	@Autowired
	private WebClient webClientEndereco;

	public LocalizacaoViaCepModel buscarCep(String cepInformado) {
		Mono<LocalizacaoViaCepModel> monoEndereco = this.webClientEndereco.method(HttpMethod.GET)
				.uri("/{cep}/json", cepInformado).retrieve()
				.bodyToMono(LocalizacaoViaCepModel.class);
		return monoEndereco.block();
	}
	
	public LocalizacaoViaCepModel buscarLogradouroRecife(String logradouro) {
		Mono<LocalizacaoViaCepModel> monoEndereco = this.webClientEndereco.method(HttpMethod.GET)
				.uri("/PE/Recife/{cep}/json", logradouro).retrieve()
				.bodyToMono(LocalizacaoViaCepModel.class);
		return monoEndereco.block();
	}

}
