package app.suasflux.modulo.setorial;

import lombok.Data;

@Data
public class TrabalhadorSuas {
	private String nome;
	private Unidade lotacao;
	private String matricula;
	private GrupoOperacional grupo;

}
