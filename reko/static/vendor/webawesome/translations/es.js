/*! Copyright 2025 Fonticons, Inc. - https://webawesome.com/license */
import "../chunks/chunk.DR3YY3XN.js";
import "../chunks/chunk.YR76HA7F.js";
import {
  registerTranslation
} from "../chunks/chunk.BYHIFG43.js";
import "../chunks/chunk.6E4D3PD7.js";

// src/translations/es.ts
var translation = {
  $code: "es",
  $name: "Espa\xF1ol",
  $dir: "ltr",
  carousel: "Carrusel",
  clearEntry: "Borrar entrada",
  close: "Cerrar",
  copied: "Copiado",
  copy: "Copiar",
  currentValue: "Valor actual",
  error: "Error",
  goToSlide: (slide, count) => `Ir a la diapositiva ${slide} de ${count}`,
  hidePassword: "Ocultar contrase\xF1a",
  loading: "Cargando",
  nextSlide: "Siguiente diapositiva",
  numOptionsSelected: (num) => {
    if (num === 0) return "No hay opciones seleccionadas";
    if (num === 1) return "1 opci\xF3n seleccionada";
    return `${num} opci\xF3n seleccionada`;
  },
  pauseAnimation: "Pausar animaci\xF3n",
  playAnimation: "Reproducir animaci\xF3n",
  previousSlide: "Diapositiva anterior",
  progress: "Progreso",
  remove: "Eliminar",
  resize: "Cambiar el tama\xF1o",
  scrollableRegion: "Regi\xF3n desplazable",
  scrollToEnd: "Desplazarse hasta el final",
  scrollToStart: "Desplazarse al inicio",
  selectAColorFromTheScreen: "Seleccione un color de la pantalla",
  showPassword: "Mostrar contrase\xF1a",
  slideNum: (slide) => `Diapositiva ${slide}`,
  toggleColorFormat: "Alternar formato de color",
  zoomIn: "Acercar",
  zoomOut: "Alejar"
};
registerTranslation(translation);
var es_default = translation;
export {
  es_default as default
};
