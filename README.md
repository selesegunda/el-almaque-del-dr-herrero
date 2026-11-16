# El almaque del Dr. Herrero

Portal **público**, estático y automatizado de vigilancia bibliográfica de **oncología digestiva**. Desarrollado en Python sin IA, sin servicios de pago requeridos y sin ordenador encendido. Recoge referencias y enlaces, **no interpreta** resultados ni reproduce textos completos sujetos a copyright.

## Qué contiene

- Cuatro epígrafes: **guías y protocolos, artículos científicos, comunicaciones científicas, noticias**.
- Metadatos desde **PubMed E-utilities**, para las revistas médicas permitidas y guías identificadas por las búsquedas; enlaces candidatos desde páginas oficiales de **SEOM, SAOM, ESMO y ASCO**.
- Histórico JSON versionado (`data/records.json`, `data/runs.json`) y detectores de cambios de metadatos.
- Panel público estático con filtros por categoría, patología, fuente y estado, contadores e historial.
- Búsqueda programada (7 días iniciales y luego semanal) y a demanda (`workflow_dispatch`).
- Identificación de incidencias por fuente: un fallo de consulta **no equivale** a ausencia de novedades.

## Puesta en marcha (aprox. 5 minutos de configuración)

1. Crea una cuenta de GitHub gratuita, si aún no tienes.
2. Crea un **repositorio público** llamado `el-almaque-del-dr-herrero`, con la rama predeterminada `main`.
3. Sube **todo el contenido de esta carpeta** a la raíz del repositorio (manteniendo `.github/workflows/`).
4. En GitHub → **Settings → Pages → Build and deployment**, selecciona **Source: GitHub Actions**.
5. En **Actions → Actualizar el almaque → Run workflow**, ejecuta la primera actualización. Ese mismo flujo también desplegará el sitio. El flujo independiente **Publicar página** sirve para subir cambios manuales hechos al panel.
6. Abre `https://TUUSUARIO.github.io/el-almaque-del-dr-herrero/` (reemplaza `TUUSUARIO`).
7. Opcional: configura en **Settings → Secrets and variables → Actions** el secreto `NCBI_API_KEY`. No es obligatorio para este volumen de consultas.

Si se crea el repositorio después de las fechas iniciales, la fase programada del 17 al 23 de noviembre de 2026 ya habrá pasado. Podrás lanzar manualmente la primera búsqueda y desde el 30 de noviembre de 2026 se ejecutará semanalmente.

**Privacidad:** aunque el portal es público, también lo son el repositorio y los datos archivados. No añadas datos personales, contraseñas, claves de acceso, ni información de pacientes.

## Horarios

- **Fase inicial:** 17–23/11/2026, todos los días a las 07:15 UTC (08:15 CET).
- **Fase semanal:** lunes a las 07:15 UTC desde el 30/11/2026 (08:15 en invierno; 09:15 en verano, España peninsular).
- Las ejecuciones programadas de GitHub pueden retrasarse u omitirse; no se garantiza puntualidad al minuto.
- **A demanda:** botón **Run workflow** en GitHub → Actions. No hay botón de ejecución en la web pública, para no exponer un acceso privilegiado.
- Para ajustar la hora o cadencia, modifica `.github/workflows/actualizar.yml`.

## Ejecutar localmente (opcional)

```bash
python -m pip install -r requirements.txt
python -m almaque --days 14
python -m http.server 8000 --directory docs
# abrir http://localhost:8000
```

Solo regenerar el portal con el histórico actual:

```bash
python -m almaque --build-only
```

Tests sin acceso a internet:

```bash
python -m unittest discover -s tests -v
```

## Criterios y limitaciones importantes

1. **No IA, ni análisis clínico.** Solo hay reglas de clasificación textual. Los enlaces se agrupan por palabras clave y tipos de registro. Un artículo puede estar mal clasificado; ningún cambio implica una recomendación clínica.
2. **No exhaustividad garantizada.** El módulo PubMed consulta publicaciones indexadas recientemente (`edat`) y filtra por revistas seleccionadas o sociedades presentes en título. No incluye todas las revistas y puede omitir documentos, comunicaciones y actualizaciones tardías. Cambia el período con `--days 30`, las patologías y revistas en `almaque/config.py`.
3. **Sociedades:** el módulo de páginas oficiales extrae enlaces HTML con mención explícita de patologías y tipo documental. Las páginas dinámicas, los PDF y contenidos sin enlaces o sin términos en el texto visible pueden no ser detectados. No se eluden inicios de sesión, captchas ni muros de pago. La fecha de publicaciones de estas páginas se muestra como **no verificada**. Recomendación para una segunda versión: conectores específicos para calendarios, bibliotecas de abstracts y archivos de guías de cada sociedad, tras validar sus páginas y permisos.
4. **Comunicaciones:** se recoge la categoría si una página oficial enlaza al abstract/póster, o si un registro PubMed declara el tipo congresual. **No hay garantía de cobertura de los abstracts completos de congresos**. Es la principal limitación de este prototipo.
5. **Versiones:** cambios en títulos, fechas, DOI o URL generan una alerta de «Actualizada». No compara el contenido íntegro de guías ni identifica la misma investigación entre un abstract y un artículo por su significado; para enlazar versiones se necesitarían reglas adicionales basadas en identificadores comunes.
6. **Copyright:** en el portal se muestran títulos, metadatos y enlaces; no se descargan ni republican abstracts extensos ni textos completos. Se pueden añadir extractos **solo** donde una licencia lo permita y quede identificada.
7. **Duplicados:** se deduplica por PMID en PubMed y por URL en páginas oficiales. Un mismo documento accesible por ambos canales puede aparecer dos veces. Una fase posterior puede reconciliar DOI/PMID/URL cuando el sitio oficial declare esos identificadores.
8. **Histórico:** los archivos JSON se guardan mediante commits de GitHub; nunca se elimina el archivo en una ejecución normal. Haz copias de seguridad del repositorio. Un histórico muy grande podría requerir migración a otra base de datos.
9. **Cuenta gratuita:** los límites y condiciones de GitHub pueden cambiar. El diseño evita infraestructuras de pago; no hay promesa de gratuidad ilimitada.
10. **Seguridad:** un repositorio público habilita lectura del histórico por cualquier visitante. La acción manual solo se lanza desde la interfaz de GitHub tras iniciar sesión.

## Fuentes técnicas de referencia

- NCBI E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25497/
- Límites NCBI: https://eutilities.github.io/site/API_Key/usageandkey/
- GitHub Pages: https://docs.github.com/en/pages
- GitHub Actions: https://docs.github.com/en/actions

## Licencia

Código fuente: MIT (ver `LICENSE`). El contenido de terceros enlazado conserva sus propios derechos.
