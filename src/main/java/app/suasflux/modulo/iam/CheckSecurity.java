package app.suasflux.modulo.iam;

import static java.lang.annotation.ElementType.METHOD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;
import org.springframework.security.access.prepost.PreAuthorize;

public interface CheckSecurity {
	
	public @interface Municipios {

	    @PreAuthorize("hasAuthority('SCOPE_WRITE') and hasAuthority('EDITAR_MUNICIPIOS')")
	    @Retention(RUNTIME)
	    @Target(METHOD)
	    public @interface PodeEditar { }

	    @PreAuthorize("hasAuthority('SCOPE_READ') and isAuthenticated()")
	    @Retention(RUNTIME)
	    @Target(METHOD)
	    public @interface PodeConsultar { }
	    
	}

	public @interface Estados {
	    
	    @PreAuthorize("hasAuthority('SCOPE_WRITE') and hasAuthority('EDITAR_ESTADOS')")
	    @Retention(RUNTIME)
	    @Target(METHOD)
	    public @interface PodeEditar { }

	    @PreAuthorize("hasAuthority('SCOPE_READ') and isAuthenticated()")
	    @Retention(RUNTIME)
	    @Target(METHOD)
	    public @interface PodeConsultar { }
	    
	}

}
