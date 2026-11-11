package app.suasflux.modulo.acolhimento.internal.domain;

import java.util.ArrayList;
import java.util.List;

import app.suasflux.modulo.publico.Individuo;
import app.suasflux.modulo.setorial.Unidade;

public class UnidadeAcolhimento extends Unidade {
	
	private int capacidade;
	private PublicoAtendidoAlta publico;
	private List<Individuo> acolhidos = new ArrayList<Individuo>();

}
