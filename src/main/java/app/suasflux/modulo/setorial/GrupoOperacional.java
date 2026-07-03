package app.suasflux.modulo.setorial;

import lombok.Getter;

@Getter
public enum GrupoOperacional {
	
	gestor_div("Chefe de Divisão"),
	gestor_setor("Chefe de Setor"),
	analista_soc("Analistas Sociais - Assistentes Sociais"),
	analista_ped("Analistas Sociais - Pedagogas(os)"),
	analista_psi("Analistas Sociais - Psicólogas(os)"),
	tecnico_adm("Técnicos - Administrativos"),
	tecnico_edu("Técnicos - Educadores Sociais");
	
	private String perfil;

	
	GrupoOperacional(String perfil){
		this.perfil=perfil;
		
	}

}
