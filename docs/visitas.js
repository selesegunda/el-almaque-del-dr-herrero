/* Contador público de visitas con GoatCounter (sin claves privadas). */
(() => {
  const todayNode = document.getElementById('visitas-hoy');
  const totalNode = document.getElementById('visitas-total');
  const note = document.getElementById('visitas-nota');
  if (!todayNode || !totalNode || !note) return;
  const code = String(window.ALMAQUE_GOATCOUNTER_CODE || '').trim();
  if (!/^[a-z0-9][a-z0-9-]*$/.test(code)) {
    note.textContent = 'Contador pendiente de activar por el administrador.';
    return;
  }
  const base = `https://${code}.goatcounter.com`;
  // Se cuentan las visitas a todas las páginas del sitio, sin compartir una API key.
  const tracker = document.createElement('script');
  tracker.src = 'https://gc.zgo.at/count.js';
  tracker.async = true;
  tracker.dataset.goatcounter = `${base}/count`;
  document.head.appendChild(tracker);

  const ymd = Object.fromEntries(
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date()).filter(p => ['year', 'month', 'day'].includes(p.type))
      .map(p => [p.type, p.value])
  );
  const today = `${ymd.year}-${ymd.month}-${ymd.day}`;
  const getCount = async (params = '') => {
    const url = `${base}/counter/TOTAL.json${params}`;
    const res = await fetch(url, {cache: 'no-store'});
    if (!res.ok) throw new Error(`GoatCounter HTTP ${res.status}`);
    const json = await res.json();
    if (typeof json.count !== 'string' && typeof json.count !== 'number') {
      throw new Error('Respuesta de contador no válida');
    }
    return String(json.count);
  };
  Promise.allSettled([
    getCount(`?start=${today}&end=${today}`),
    getCount()
  ]).then(([day, total]) => {
    todayNode.textContent = day.status === 'fulfilled' ? day.value : '—';
    totalNode.textContent = total.status === 'fulfilled' ? total.value : '—';
    note.textContent = day.status === 'fulfilled' && total.status === 'fulfilled'
      ? 'Páginas vistas · Hoy según horario peninsular · Los datos pueden tardar hasta 4 horas en actualizarse.'
      : 'No se pueden mostrar las cifras. Comprueba que has activado los contadores públicos en GoatCounter.';
  });
})();
