package app.praxis.modulo.publico;

import lombok.Getter;

@Getter
public enum TipoVinculo {
	ASCENDENTE("GENITOR(A)","MÃE OU PAI"),
	DESCENDENTE("PROLE", "FILHA(O)");
	
	private String ascendente;
	private String descendente;
	
	TipoVinculo(String asc, String desc){
		this.descendente=desc;
		this.ascendente=asc;
	}

}
