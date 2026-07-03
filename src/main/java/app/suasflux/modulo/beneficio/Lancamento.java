package app.suasflux.modulo.beneficio;

import java.math.BigDecimal;
import java.time.LocalDate;

import app.suasflux.modulo.publico.Individuo;
import lombok.Data;

@Data
public class Lancamento {

	
	private Long codigo;
	
	
	private String descricao;

	
	private LocalDate dataVencimento;

	private LocalDate dataPagamento;

	
	private BigDecimal valor;

	private String observacao;

	
	private TipoLancamento tipo;

	
	private Categoria categoria;

	
	private Individuo pessoa;
	
	private String anexo;
	
	//@Transient
	private String urlAnexo;
	
}
