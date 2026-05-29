package app.praxis.modulo.integracao;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;



@RestController
public class LocalizacaoViaCepController {
	
	@Autowired
	private LocalizacaoViaCepService localizacaoViaCepService;
	
	 @GetMapping("/apis-externas/busca-cep/{cep}")
	 public ResponseEntity<LocalizacaoViaCepModel> buscaPorCep(@PathVariable String cep) {
		 LocalizacaoViaCepModel enderecoBuscado = this.localizacaoViaCepService.buscarCep(cep);
		 return ResponseEntity.ok(enderecoBuscado);
	  }
	 
	 @GetMapping("/apis-externas/busca-logradouro/{logradouro}")
	 public ResponseEntity<LocalizacaoViaCepModel> buscaPorLogradouroDeRecife(@PathVariable String logradouro) {
		 LocalizacaoViaCepModel enderecoBuscado = this.localizacaoViaCepService.buscarLogradouroRecife(logradouro);
		 return ResponseEntity.ok(enderecoBuscado);
	  }

}
