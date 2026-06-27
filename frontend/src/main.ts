/* -------------------------------------------------------------------------- */
/* Types — shape of the JSON returned by the backend /search endpoint.        */
/* Kept inline (no imports) so the compiled output is a plain script that runs */
/* without a module loader, even when opened directly from the filesystem.    */
/* -------------------------------------------------------------------------- */

interface ProductResult {
  platform: string;
  product_name: string;
  quantity: string;
  price: number | null;
  unit_price: number | null;
  unit_basis: string | null; // "100g" | "L" | "unit"
  savings_vs_max: number | null;
  savings_pct: number | null;
  is_best_value: boolean;
  stock: boolean;
  delivery: string;
  product_url: string;
  image_url: string;
  demo: boolean;
}

interface SearchResponse {
  query: string;
  location: string;
  mode: "live" | "demo" | "demo-fallback";
  is_demo: boolean;
  results: ProductResult[];
  cached: boolean;
  count: number;
  in_stock_count: number;
  best_platform: string | null;
  cheapest_price: number | null;
  cheapest_unit_price: number | null;
  cheapest_unit_basis: string | null;
}

type SortMode = "value_asc" | "price_asc" | "availability";

/* -------------------------------------------------------------------------- */
/* Configuration                                                              */
/* -------------------------------------------------------------------------- */

// Single source of truth for the production backend. Update here if it changes.
const PROD_API_BASE = "https://budgetmart-backend.vercel.app";
const LOCAL_HOSTS = ["127.0.0.1", "localhost", ""];
const API_BASE = LOCAL_HOSTS.includes(window.location.hostname)
  ? "http://127.0.0.1:5000"
  : PROD_API_BASE;

/* -------------------------------------------------------------------------- */
/* DOM references                                                             */
/* -------------------------------------------------------------------------- */

const $ = <T extends HTMLElement>(id: string): T => {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  return el as T;
};

const form = $<HTMLFormElement>("searchForm");
const searchInput = $<HTMLInputElement>("searchInput");
const locationInput = $<HTMLInputElement>("locationInput");
const sortSelect = $<HTMLSelectElement>("sortSelect");
const searchBtn = $<HTMLButtonElement>("searchBtn");
const loader = $("loader");
const errorBox = $("errorMessage");
const errorText = $("errorText");
const emptyBox = $("emptyMessage");
const emptyText = $("emptyText");
const summary = $("resultsSummary");
const demoBanner = $("demoBanner");
const grid = $("resultsGrid");

/* -------------------------------------------------------------------------- */
/* State                                                                      */
/* -------------------------------------------------------------------------- */

let lastResponse: SearchResponse | null = null;
let isLoading = false;
let inFlight: AbortController | null = null;

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

const show = (el: HTMLElement) => el.classList.remove("hidden");
const hide = (el: HTMLElement) => el.classList.add("hidden");
const rupee = (n: number) => `₹${Number.isInteger(n) ? n : n.toFixed(2)}`;

/** Only allow http(s) links; everything else (javascript:, data:) becomes "#". */
function safeUrl(url: string): string {
  try {
    const u = new URL(url, window.location.href);
    return u.protocol === "http:" || u.protocol === "https:" ? u.href : "#";
  } catch {
    return "#";
  }
}

/** Stable colour per platform name (so BigBasket is always the same hue). */
function platformColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return `hsl(${Math.abs(hash) % 360}, 70%, 55%)`;
}

/* -------------------------------------------------------------------------- */
/* Fetching                                                                   */
/* -------------------------------------------------------------------------- */

async function runSearch(query: string, location: string): Promise<void> {
  if (isLoading) return; // guard against double-submit
  isLoading = true;
  inFlight?.abort();
  inFlight = new AbortController();

  setBusy(true);
  grid.innerHTML = "";
  hide(errorBox);
  hide(emptyBox);
  hide(summary);
  hide(demoBanner);

  try {
    let url = `${API_BASE}/search?product=${encodeURIComponent(query)}`;
    if (location) url += `&location=${encodeURIComponent(location)}`;

    const res = await fetch(url, { signal: inFlight.signal });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      // Distinguish "nothing found" (calm) from "something broke" (alarming).
      if (res.status === 404) {
        renderEmpty(query);
      } else if (res.status === 429) {
        renderError("Too many searches — please wait a minute and try again.");
      } else {
        renderError((data && data.error) || `Request failed (${res.status}).`);
      }
      return;
    }

    lastResponse = data as SearchResponse;
    render();
  } catch (err) {
    if ((err as Error)?.name === "AbortError") return; // superseded by a newer search
    renderError("Could not reach the server. Check your connection and try again.");
  } finally {
    isLoading = false;
    setBusy(false);
  }
}

function setBusy(busy: boolean): void {
  searchBtn.disabled = busy;
  searchBtn.setAttribute("aria-busy", String(busy));
  if (busy) show(loader);
  else hide(loader);
}

/* -------------------------------------------------------------------------- */
/* Rendering                                                                  */
/* -------------------------------------------------------------------------- */

function sortResults(results: ProductResult[]): ProductResult[] {
  const mode = sortSelect.value as SortMode;
  const out = [...results];
  const oosLast = (a: ProductResult, b: ProductResult) =>
    a.stock === b.stock ? 0 : a.stock ? -1 : 1;

  if (mode === "price_asc") {
    out.sort((a, b) => oosLast(a, b) || (a.price ?? Infinity) - (b.price ?? Infinity));
  } else if (mode === "value_asc") {
    // True value first: items with a comparable unit price rank by it; items
    // with no parseable size sink to the bottom (their cheap sticker is not a
    // fair comparison), sorted among themselves by sticker price.
    out.sort((a, b) => {
      const stock = oosLast(a, b);
      if (stock) return stock;
      const au = a.unit_price;
      const bu = b.unit_price;
      if (au != null && bu != null) return au - bu;
      if (au != null) return -1;
      if (bu != null) return 1;
      return (a.price ?? Infinity) - (b.price ?? Infinity);
    });
  } else {
    out.sort(oosLast);
  }
  return out;
}

function render(): void {
  if (!lastResponse) return;
  grid.innerHTML = "";

  const results = Array.isArray(lastResponse.results) ? lastResponse.results : [];
  if (results.length === 0) {
    renderEmpty(lastResponse.query);
    return;
  }

  // Demo banner (sample data — never passed off as live).
  if (lastResponse.is_demo) {
    demoBanner.textContent =
      "Showing sample data — no live API key configured, so prices are illustrative.";
    show(demoBanner);
  } else {
    hide(demoBanner);
  }

  // Summary line.
  const best =
    lastResponse.cheapest_price != null && lastResponse.best_platform
      ? ` · Best: ${rupee(lastResponse.cheapest_price)} on ${lastResponse.best_platform}`
      : "";
  summary.textContent = `Found ${lastResponse.count} offer${lastResponse.count === 1 ? "" : "s"} for “${lastResponse.query}”${best}`;
  show(summary);

  const sorted = sortResults(results);
  sorted.forEach((item, i) => grid.appendChild(buildCard(item, i)));
}

function buildCard(item: ProductResult, index: number): HTMLElement {
  const isOos = !item.stock || item.price == null;

  const card = document.createElement("div");
  card.className = "card";
  if (item.is_best_value) card.classList.add("best-value");
  if (isOos) card.classList.add("out-of-stock");
  card.style.animationDelay = `${index * 0.08}s`;

  // Best-value ribbon: real DOM text + a non-colour icon (not colour-only).
  if (item.is_best_value) {
    const ribbon = document.createElement("div");
    ribbon.className = "best-ribbon";
    ribbon.textContent = "★ BEST VALUE";
    card.appendChild(ribbon);
  }

  // Image with a graceful fallback when the third-party thumbnail 404s.
  card.appendChild(buildImage(item));

  // Platform badge.
  const header = document.createElement("div");
  header.className = "card-header";
  const badge = document.createElement("span");
  badge.className = "platform-badge";
  badge.style.color = platformColor(item.platform);
  badge.textContent = item.platform;
  header.appendChild(badge);
  card.appendChild(header);

  // Product name.
  const name = document.createElement("h3");
  name.className = "product-name";
  name.textContent = item.product_name;
  card.appendChild(name);

  // Badges row: stock + quantity.
  const badges = document.createElement("div");
  badges.className = "badge-row";
  const stockBadge = document.createElement("span");
  stockBadge.className = `status-badge ${isOos ? "status-oos" : "status-in-stock"}`;
  stockBadge.textContent = isOos ? "Out of Stock" : "In Stock";
  badges.appendChild(stockBadge);
  if (item.quantity) {
    const qty = document.createElement("span");
    qty.className = "status-badge status-qty";
    qty.textContent = item.quantity;
    badges.appendChild(qty);
  }
  card.appendChild(badges);

  // Price + unit price.
  const priceBox = document.createElement("div");
  priceBox.className = "price-container";
  if (isOos) {
    const p = document.createElement("span");
    p.className = "price";
    p.textContent = "--";
    p.setAttribute("aria-label", "Price unavailable");
    priceBox.appendChild(p);
  } else {
    const cur = document.createElement("span");
    cur.className = "currency";
    cur.textContent = "₹";
    const p = document.createElement("span");
    p.className = "price";
    p.textContent = String(item.price);
    priceBox.appendChild(cur);
    priceBox.appendChild(p);
    const unit = document.createElement("span");
    if (item.unit_price != null && item.unit_basis) {
      unit.className = "unit-price";
      unit.textContent = `${rupee(item.unit_price)}/${item.unit_basis}`;
    } else {
      // No size in the title -> sticker price is not comparable. Say so.
      unit.className = "unit-price unit-price-na";
      unit.textContent = "size n/a";
      unit.title = "No pack size found, so price-per-unit cannot be compared";
    }
    priceBox.appendChild(unit);
  }
  card.appendChild(priceBox);

  // Savings line.
  if (!isOos && item.savings_vs_max != null && item.savings_vs_max > 0) {
    const save = document.createElement("div");
    save.className = "savings";
    const pct = item.savings_pct != null ? ` (${item.savings_pct}%)` : "";
    save.textContent = `Save ${rupee(item.savings_vs_max)}${pct} vs priciest`;
    card.appendChild(save);
  } else {
    const spacer = document.createElement("div");
    spacer.className = "savings savings-empty";
    card.appendChild(spacer);
  }

  // Delivery.
  const delivery = document.createElement("div");
  delivery.className = "delivery";
  delivery.textContent = !isOos && item.delivery ? item.delivery : "";
  card.appendChild(delivery);

  // Visit store.
  const link = document.createElement("a");
  link.className = "visit-btn";
  link.href = safeUrl(item.product_url);
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "Visit Store ↗";
  card.appendChild(link);

  return card;
}

function fallbackTile(alt: string): HTMLElement {
  const div = document.createElement("div");
  div.className = "product-img img-fallback";
  div.setAttribute("role", "img");
  div.setAttribute("aria-label", alt);
  div.textContent = "🛒";
  return div;
}

function buildImage(item: ProductResult): HTMLElement {
  if (!item.image_url) return fallbackTile(item.product_name);
  const img = document.createElement("img");
  img.className = "product-img";
  img.loading = "lazy";
  img.alt = item.product_name;
  img.src = item.image_url;
  img.addEventListener("error", () => img.replaceWith(fallbackTile(item.product_name)));
  return img;
}

function renderEmpty(query: string): void {
  hide(summary);
  hide(demoBanner);
  grid.innerHTML = "";
  emptyText.textContent = `No results for “${query}”. Try a different spelling or a broader term.`;
  show(emptyBox);
}

function renderError(message: string): void {
  hide(summary);
  hide(demoBanner);
  grid.innerHTML = "";
  errorText.textContent = message;
  show(errorBox);
}

/* -------------------------------------------------------------------------- */
/* Events                                                                     */
/* -------------------------------------------------------------------------- */

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const query = searchInput.value.trim();
  const location = locationInput.value.trim();
  if (query) void runSearch(query, location);
});

sortSelect.addEventListener("change", () => {
  if (lastResponse) render();
});
