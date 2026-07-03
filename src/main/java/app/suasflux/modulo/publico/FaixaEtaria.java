package app.suasflux.modulo.publico;

import lombok.Getter;

@Getter
public enum FaixaEtaria {
	
		INFANTIL1("NEONATO OU RECÉM-NASCIDO(RN)","Pessoas de 0 a 28 dias de vida"),
        INFANTIL2("BEBÊ","Pessoas com mais de 28 dias e menos de 2 anos de idade"),
	    INFANTIL3("CRIANÇA", "Pessoas com mais de 2 anos de idade e menos de 11 anos"),
	    PRE_ADOLESCENCIA("PRÉ-ADOLESCENTE","Pessoas a partir de 11 anos e menos de 17 anos"),
	    ADOLESCENCIA("ADOLESCENTE","Pessoas a partir de 14 anos e menos de 18 anos"),
	    JUVENTUDE("JOVEM","Pessoas a partir de 18 anos e menos de 20 anos"),
	    ADULTO("PESSOA ADULTA","Pessoas a partir de 20 anos e até os 59 anos"),
	    IDOSO("PESSOA IDOSA","Pessoas 60+");
        
	    private String nome;
        private String descricao;
        
        FaixaEtaria(String nome, String descricao){
			this.nome=nome;
			this.descricao=descricao;
		}   
        
	
 
}
