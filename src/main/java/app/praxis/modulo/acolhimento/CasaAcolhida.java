package app.praxis.modulo.acolhimento;

import java.util.ArrayList;
import java.util.List;

import app.praxis.modulo.publico.Individuo;
import app.praxis.modulo.setorial.Unidade;

public class CasaAcolhida extends Unidade {
	
	private int capacidade;
	private PublicoAtendido publico;
	private List<Individuo> acolhidos = new ArrayList<Individuo>();

}
