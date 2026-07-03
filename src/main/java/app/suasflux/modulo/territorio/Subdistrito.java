package app.suasflux.modulo.territorio;

import lombok.Getter;

@Getter
public enum Subdistrito {
	
	RPA1("RPA-1"),
    RPA2("RPA-2"),
    RPA3A("RPA-3A"),
    RPA3B("RPA-3B"),
    RPA4("RPA-4"),
    RPA5("RPA-5"),
    RPA6A("RPA-6A"),
	RPA6B("RPA-6B"),
	OUTRO("SUBDSTRITO DE OUTRO MUNICÍPIO");
	
	public String nome;
	
	
	Subdistrito(String nome) {
		this.nome=nome;
		
	}
}
