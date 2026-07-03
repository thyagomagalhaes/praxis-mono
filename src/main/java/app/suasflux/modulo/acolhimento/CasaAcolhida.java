package app.suasflux.modulo.acolhimento;

import java.util.ArrayList;
import java.util.List;

import app.suasflux.modulo.publico.Individuo;
import app.suasflux.modulo.setorial.Unidade;

public class CasaAcolhida extends Unidade {
	
	private int capacidade;
	private PublicoAtendido publico;
	private List<Individuo> acolhidos = new ArrayList<Individuo>();

}
