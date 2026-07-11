const state = {
  rentals: [],
  filters: null,
  selectedNeighborhoods: new Set(),
  selectedAmenities: new Set(),
  defaultWeights: {},
  weights: {},
};

const weightLabels = {
  descuento_total: "Descuento total",
  descuento_m2: "Descuento por m2",
  facilidad: "Puntos por facilidad",
  ubicacion: "Ubicacion",
  zonas_interes: "Zonas de interes",
  zonas_evitar: "Zonas a evitar",
  penalizacion_baja_calidad: "Penalizar datos incompletos",
  penalizacion_gastos_no_informados: "Penalizar gastos sin dato",
  penalizacion_gastos_altos: "Penalizar gastos altos",
};

const weightRanges = {
  descuento_total: { min: 0, max: 120, step: 5 },
  descuento_m2: { min: 0, max: 90, step: 5 },
  facilidad: { min: 0, max: 10, step: 1 },
  ubicacion: { min: 0, max: 3, step: 0.25 },
  zonas_interes: { min: 0, max: 3, step: 0.25 },
  zonas_evitar: { min: 0, max: 4, step: 0.25 },
  penalizacion_baja_calidad: { min: 0, max: 40, step: 1 },
  penalizacion_gastos_no_informados: { min: 0, max: 25, step: 1 },
  penalizacion_gastos_altos: { min: 0, max: 30, step: 1 },
};

const elements = {
  totalCount: document.querySelector("#total-count"),
  updatedAt: document.querySelector("#updated-at"),
  neighborhood: document.querySelector("#neighborhood-filter"),
  neighborhoodToggle: document.querySelector("#neighborhood-toggle"),
  neighborhoodMenu: document.querySelector("#neighborhood-menu"),
  neighborhoodSearch: document.querySelector("#neighborhood-search"),
  neighborhoodOptions: document.querySelector("#neighborhood-options"),
  neighborhoodSelected: document.querySelector("#neighborhood-selected"),
  price: document.querySelector("#price-filter"),
  priceLabel: document.querySelector("#price-label"),
  amenities: document.querySelector("#amenities-filter"),
  clear: document.querySelector("#clear-filters"),
  sort: document.querySelector("#sort-filter"),
  weights: document.querySelector("#weights-controls"),
  resetWeights: document.querySelector("#reset-weights"),
  summary: document.querySelector("#results-summary"),
  rentals: document.querySelector("#rentals"),
  empty: document.querySelector("#empty-state"),
};

init();

async function init() {
  try {
    const response = await fetch("/api/rentals");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No se pudo cargar el ranking.");

    state.rentals = data.rentals || [];
    state.filters = data.filters || {};
    state.defaultWeights = data.weights || {};
    state.weights = { ...state.defaultWeights };
    setupFilters(data);
    setupWeights();
    render();
  } catch (error) {
    elements.summary.textContent = error.message;
    elements.empty.hidden = false;
    elements.empty.textContent = "Revisa que exista el CSV del scraper y vuelve a cargar la pagina.";
  }
}

function setupFilters(data) {
  elements.totalCount.textContent = data.total ?? state.rentals.length;
  elements.updatedAt.textContent = data.updated_at ? `Scraping: ${data.updated_at}` : "Datos locales";

  renderNeighborhoodOptions();

  const priceMax = Math.ceil((state.filters.precio_max || 0) / 500) * 500;
  elements.price.min = state.filters.precio_min || 0;
  elements.price.max = priceMax;
  elements.price.value = priceMax;
  updatePriceLabel();

  for (const amenity of state.filters.facilidades || []) {
    const label = document.createElement("label");
    label.className = "chip";
    label.innerHTML = `<input type="checkbox" value="${amenity.key}"> ${amenity.label}`;
    elements.amenities.append(label);
  }

  elements.neighborhoodToggle.addEventListener("click", toggleNeighborhoodMenu);
  elements.neighborhoodSearch.addEventListener("input", renderNeighborhoodOptions);
  elements.neighborhoodOptions.addEventListener("change", handleNeighborhoodChange);
  elements.neighborhoodSelected.addEventListener("click", handleNeighborhoodChipClick);
  document.addEventListener("click", closeNeighborhoodMenuOnOutsideClick);
  document.addEventListener("keydown", closeNeighborhoodMenuOnEscape);
  elements.price.addEventListener("input", () => {
    updatePriceLabel();
    render();
  });
  elements.sort.addEventListener("change", render);
  elements.amenities.addEventListener("change", (event) => {
    if (event.target.type !== "checkbox") return;
    if (event.target.checked) state.selectedAmenities.add(event.target.value);
    else state.selectedAmenities.delete(event.target.value);
    render();
  });
  elements.clear.addEventListener("click", clearFilters);
}

function setupWeights() {
  elements.weights.innerHTML = Object.entries(state.defaultWeights).map(([key, value]) => {
    const range = weightRanges[key] || { min: 0, max: Math.max(value * 2, 10), step: 1 };
    return `
      <label class="weight-control">
        <span>${weightLabels[key] || key}</span>
        <input type="range" data-weight="${key}" min="${range.min}" max="${range.max}" step="${range.step}" value="${value}">
        <strong data-weight-value="${key}">${formatNumber(value)}</strong>
      </label>
    `;
  }).join("");

  elements.weights.addEventListener("input", (event) => {
    const key = event.target.dataset.weight;
    if (!key) return;
    state.weights[key] = Number(event.target.value);
    document.querySelector(`[data-weight-value="${key}"]`).textContent = formatNumber(state.weights[key]);
    render();
  });

  elements.resetWeights.addEventListener("click", () => {
    state.weights = { ...state.defaultWeights };
    for (const input of elements.weights.querySelectorAll("input[data-weight]")) {
      input.value = state.weights[input.dataset.weight];
      document.querySelector(`[data-weight-value="${input.dataset.weight}"]`).textContent = formatNumber(Number(input.value));
    }
    render();
  });
}

function updatePriceLabel() {
  elements.priceLabel.textContent = `Hasta ${formatMoney(Number(elements.price.value))}`;
}

function clearFilters() {
  state.selectedNeighborhoods.clear();
  elements.neighborhoodSearch.value = "";
  renderNeighborhoodOptions();
  renderSelectedNeighborhoods();
  elements.price.value = elements.price.max;
  state.selectedAmenities.clear();
  for (const checkbox of elements.amenities.querySelectorAll("input")) checkbox.checked = false;
  updatePriceLabel();
  render();
}

function render() {
  const selectedNeighborhoods = [...state.selectedNeighborhoods];
  const maxPrice = Number(elements.price.value);
  const selectedAmenities = [...state.selectedAmenities];

  let rentals = state.rentals.map((rental) => ({
    ...rental,
    score_ajustado: calculateScore(rental),
  })).filter((rental) => {
    const matchesNeighborhood = selectedNeighborhoods.length === 0 || selectedNeighborhoods.includes(rental.barrio);
    const matchesPrice = !maxPrice || Number(rental.costo_mensual_total_pesos || 0) <= maxPrice;
    const matchesAmenities = selectedAmenities.every((key) => rental.facilidades_keys.includes(key));
    return matchesNeighborhood && matchesPrice && matchesAmenities;
  });

  rentals = sortRentals(rentals).map((rental, index) => ({ ...rental, puesto_ajustado: index + 1 }));
  elements.summary.textContent = `${rentals.length} de ${state.rentals.length} alquileres visibles`;
  elements.empty.hidden = rentals.length > 0;
  elements.rentals.innerHTML = rentals.slice(0, 120).map(cardTemplate).join("");
}

function toggleNeighborhoodMenu() {
  const shouldOpen = elements.neighborhoodMenu.hidden;
  elements.neighborhoodMenu.hidden = !shouldOpen;
  elements.neighborhoodToggle.setAttribute("aria-expanded", String(shouldOpen));
  if (shouldOpen) elements.neighborhoodSearch.focus();
}

function closeNeighborhoodMenu() {
  elements.neighborhoodMenu.hidden = true;
  elements.neighborhoodToggle.setAttribute("aria-expanded", "false");
}

function closeNeighborhoodMenuOnOutsideClick(event) {
  if (elements.neighborhood.contains(event.target)) return;
  closeNeighborhoodMenu();
}

function closeNeighborhoodMenuOnEscape(event) {
  if (event.key === "Escape") closeNeighborhoodMenu();
}

function renderNeighborhoodOptions() {
  const query = normalizeText(elements.neighborhoodSearch?.value || "");
  const neighborhoods = (state.filters?.barrios || []).filter((barrio) => normalizeText(barrio).includes(query));

  elements.neighborhoodOptions.innerHTML = neighborhoods.length
    ? neighborhoods.map((barrio) => `
      <label class="multi-select-option">
        <input type="checkbox" value="${escapeHtml(barrio)}" ${state.selectedNeighborhoods.has(barrio) ? "checked" : ""}>
        <span>${escapeHtml(barrio)}</span>
      </label>
    `).join("")
    : '<p class="multi-select-empty">Sin barrios encontrados</p>';

  renderSelectedNeighborhoods();
}

function handleNeighborhoodChange(event) {
  if (event.target.type !== "checkbox") return;
  if (event.target.checked) state.selectedNeighborhoods.add(event.target.value);
  else state.selectedNeighborhoods.delete(event.target.value);
  renderSelectedNeighborhoods();
  render();
}

function renderSelectedNeighborhoods() {
  const selected = [...state.selectedNeighborhoods];
  elements.neighborhoodToggle.textContent = selected.length === 0
    ? "Todos los barrios"
    : `${selected.length} barrio${selected.length === 1 ? "" : "s"} seleccionado${selected.length === 1 ? "" : "s"}`;

  elements.neighborhoodSelected.innerHTML = selected.map((barrio) => `
    <button class="selected-chip" type="button" data-neighborhood="${escapeHtml(barrio)}">
      ${escapeHtml(barrio)} <span aria-hidden="true">×</span>
    </button>
  `).join("");
}

function handleNeighborhoodChipClick(event) {
  const chip = event.target.closest("button[data-neighborhood]");
  if (!chip) return;
  state.selectedNeighborhoods.delete(chip.dataset.neighborhood);
  renderNeighborhoodOptions();
  render();
}

function sortRentals(rentals) {
  const sorted = [...rentals];
  if (elements.sort.value === "price") {
    return sorted.sort((a, b) => (a.costo_mensual_total_pesos || Infinity) - (b.costo_mensual_total_pesos || Infinity));
  }
  if (elements.sort.value === "amenities") {
    return sorted.sort((a, b) => b.cantidad_facilidades - a.cantidad_facilidades || b.score_ajustado - a.score_ajustado);
  }
  return sorted.sort((a, b) => b.score_ajustado - a.score_ajustado);
}

function calculateScore(rental) {
  const inputs = rental.score_inputs || {};
  return (
    Number(inputs.descuento_total || 0) * Number(state.weights.descuento_total || 0)
    + Number(inputs.descuento_m2 || 0) * Number(state.weights.descuento_m2 || 0)
    + Number(inputs.facilidades || 0) * Number(state.weights.facilidad || 0)
    + Number(inputs.ubicacion || 0) * Number(state.weights.ubicacion || 0)
    + Number(inputs.zonas_interes || 0) * Number(state.weights.zonas_interes || 0)
    - Number(inputs.zonas_evitar || 0) * Number(state.weights.zonas_evitar || 0)
    - Number(inputs.penalizacion_baja_calidad || 0) * Number(state.weights.penalizacion_baja_calidad || 0)
    - Number(inputs.penalizacion_gastos_no_informados || 0) * Number(state.weights.penalizacion_gastos_no_informados || 0)
    - Number(inputs.penalizacion_gastos_altos || 0) * Number(state.weights.penalizacion_gastos_altos || 0)
  );
}

function cardTemplate(rental) {
  const amenities = rental.facilidades.length
    ? rental.facilidades.slice(0, 6).map((item) => `<span>${escapeHtml(item)}</span>`).join("")
    : "<span>Sin facilidades detectadas</span>";

  return `
    <article class="rental-card">
      <div class="card-top">
        <span class="rank">#${rental.puesto_ajustado}</span>
        <span class="score">${formatNumber(rental.score_ajustado)} pts</span>
      </div>
      <h2>${escapeHtml(rental.titulo || "Alquiler sin titulo")}</h2>
      <p class="neighborhood">${escapeHtml(rental.barrio || "Barrio sin dato")}</p>
      <div class="stats">
        <div class="stat"><span>Total mensual</span><strong>${formatMoney(rental.costo_mensual_total_pesos)}</strong></div>
        <div class="stat"><span>Alquiler</span><strong>${formatMoney(rental.alquiler_pesos)}</strong></div>
        <div class="stat"><span>Metros</span><strong>${formatMeters(rental.metros_cuadrados)}</strong></div>
        <div class="stat"><span>Descuento segmento</span><strong>${formatPercent(rental.descuento_vs_segmento_pct)}</strong></div>
      </div>
      <p class="location-score">${formatLocationScore(rental)}</p>
      <p class="location-score">${formatZoneScore(rental)}</p>
      <p class="base-score">Score base: ${formatNumber(rental.score_base)} pts | Puesto base: #${rental.puesto}</p>
      <div class="amenities">${amenities}</div>
      <a class="card-link" href="${rental.url}" target="_blank" rel="noreferrer">Abrir aviso</a>
    </article>
  `;
}

function formatMoney(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "Sin dato";
  return new Intl.NumberFormat("es-UY", { style: "currency", currency: "UYU", maximumFractionDigits: 0 }).format(value);
}

function formatMeters(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "Sin dato";
  return `${formatNumber(value)} m2`;
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "Sin dato";
  return new Intl.NumberFormat("es-UY", { style: "percent", maximumFractionDigits: 0 }).format(value);
}

function formatLocationScore(rental) {
  if (!rental.distancia_referencia_min_km) return "Ubicacion: sin coordenadas cacheadas";
  return `Ubicacion: +${formatNumber(rental.score_ubicacion || 0)} pts, referencia urbana a ${formatNumber(rental.distancia_referencia_min_km)} km`;
}

function formatZoneScore(rental) {
  const interest = rental.zona_interes_cercana
    ? `interes: ${escapeHtml(rental.zona_interes_cercana)} (+${formatNumber(rental.score_zonas_interes || 0)})`
    : "interes: sin zonas configuradas";
  const avoid = rental.zona_evitar_cercana
    ? `evitar: ${escapeHtml(rental.zona_evitar_cercana)} (-${formatNumber(rental.penalizacion_zona_evitar || 0)})`
    : "evitar: sin penalizacion";
  return `Zonas: ${interest} | ${avoid}`;
}

function formatNumber(value) {
  return new Intl.NumberFormat("es-UY", { maximumFractionDigits: 1 }).format(value);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[char]);
}

function normalizeText(value) {
  return String(value).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}
