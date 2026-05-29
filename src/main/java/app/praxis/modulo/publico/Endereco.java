package app.praxis.modulo.publico;

import lombok.Data;

@Data
public class Endereco {
	
	private String logradouro;
	private int numero;
	private String bairro;
	private String municipio;
	private String cep;

}
