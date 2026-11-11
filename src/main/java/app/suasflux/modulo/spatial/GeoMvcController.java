package app.suasflux.modulo.spatial;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class GeoMvcController {

    @GetMapping("/mapa")
    public String exibirMapa(Model model) {
        model.addAttribute("tituloPage", "Mapa de Abrangência e Serviços");
        return "mapa";
    }
}
