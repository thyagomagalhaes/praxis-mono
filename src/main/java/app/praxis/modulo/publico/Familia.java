package app.praxis.modulo.publico;

import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class Familia {
	
	private Endereco endereco;	
	private List<Individuo> membros = new ArrayList<Individuo>();


}
