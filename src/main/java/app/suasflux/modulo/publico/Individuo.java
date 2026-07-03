package app.suasflux.modulo.publico;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class Individuo {
	
	private String nomeCivil;
	private String nomeSocial;
	private String cin;
	private String nis;
	private String sus;
	private OffsetDateTime dataNascimento;
	//@Transient
	private int idade=0;
	private FaixaEtaria faixaEtaria;
	private TipoVinculo vinculo;
	private List<Individuo> dependentes = new ArrayList<Individuo>();


}
