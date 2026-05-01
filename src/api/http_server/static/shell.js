// Agent Pitch — App Shell JavaScript
// Implements hash router, nav pin toggle, connection monitoring, and section dispatch
// Coordinates with section-specific modules (matches.js, placeholders.js, etc.)

// ── State ───────────────────────────────────────────────────────
let currentSection = 'matches';
let navPinned = false;
let connectionLostCount = 0;
let healthCheckInterval = null;
let tooltipTimer = null;

// ── DOM Elements ────────────────────────────────────────────────
const bodyGrid = document.querySelector('.body-grid');
const pinToggle = document.getElementById('pin-toggle');
const navItems = document.querySelectorAll('.nav-item');
const sectionBody = document.getElementById('section-body');
const sectionTitle = document.getElementById('section-title');
const shellSubtitle = document.getElementById('shell-subtitle');
const rightCap = document.getElementById('right-cap');
const statusBar = document.getElementById('status-bar');
const connectionLostBanner = document.getElementById('connection-lost-banner');
const tooltip = document.getElementById('nav-tooltip');
const sbApi = document.getElementById('sb-api');

// ── Router ──────────────────────────────────────────────────────
function parseRoute() {
  const hash = window.location.hash.slice(1); // Remove #
  if (!hash || hash === '/') return { section: 'matches' };

  const parts = hash.split('/').filter(p => p);
  const section = parts[0] || 'matches';
  const subsection = parts[1] || null;

  return { section, subsection };
}

function navigateToSection(section, subsection = null) {
  const route = subsection ? `#/${section}/${subsection}` : `#/${section}`;
  if (window.location.hash !== route) {
    window.location.hash = route;
  }
  activateSection(section, subsection);
}

function activateSection(section, subsection = null) {
  // Re-dispatch even when staying on the same section — sub-routes
  // (e.g., #/matches → #/matches/new) need the section module to
  // re-render the correct sub-view. Skip ONLY the chrome updates
  // (nav active state, title) when section is unchanged.
  const sectionUnchanged = currentSection === section;
  if (sectionUnchanged) {
    // Section module still needs to know about the sub-route change
    loadSectionContent(section, subsection);
    return;
  }

  // Call deactivate on the outgoing section before switching
  const outgoingSection = window[`${currentSection}Section`];
  if (outgoingSection && typeof outgoingSection.deactivate === 'function') {
    outgoingSection.deactivate();
  }

  // Update active nav item
  navItems.forEach(item => {
    item.classList.remove('active');
    item.removeAttribute('aria-current');
  });

  const targetNavItem = document.querySelector(`[data-section="${section}"]`);
  if (targetNavItem) {
    targetNavItem.classList.add('active');
    targetNavItem.setAttribute('aria-current', 'page');
  }

  // Update section title and subtitle
  const sectionNames = {
    matches: 'MATCHES',
    strategies: 'STRATEGIES',
    arena: 'ARENA',
    cup: 'CUP',
    league: 'LEAGUE',
    config: 'CONFIG'
  };

  const sectionName = sectionNames[section] || section.toUpperCase();
  sectionTitle.textContent = sectionName;
  shellSubtitle.textContent = sectionName;

  // Clear right cap
  rightCap.textContent = '';

  // Update document title
  document.title = `Agent Pitch — ${sectionName}`;

  // Load section content
  loadSectionContent(section, subsection);

  // Emit section changed event
  window.dispatchEvent(new CustomEvent('app:sectionChanged', {
    detail: { section, subsection }
  }));

  currentSection = section;
}

function loadSectionContent(section, subsection = null) {
  try {
    switch (section) {
      case 'matches':
        if (typeof window.matchesSection !== 'undefined') {
          window.matchesSection.activate({ section, subsection });
        } else {
          console.error('matches.js not loaded - matchesSection not found');
          sectionBody.innerHTML = '<div class="section-placeholder">Failed to load matches section</div>';
        }
        break;

      case 'strategies':
        if (typeof window.strategiesSection !== 'undefined') {
          window.strategiesSection.activate({ section, subsection });
        } else {
          console.error('placeholders.js not loaded - strategiesSection not found');
          sectionBody.innerHTML = '<div class="section-placeholder">Failed to load strategies section</div>';
        }
        break;

      case 'arena':
        if (typeof window.arenaSection !== 'undefined') {
          window.arenaSection.activate({ section, subsection });
        } else {
          console.error('placeholders.js not loaded - arenaSection not found');
          sectionBody.innerHTML = '<div class="section-placeholder">Failed to load arena section</div>';
        }
        break;

      case 'cup':
        if (typeof window.cupSection !== 'undefined') {
          window.cupSection.activate({ section, subsection });
        } else {
          console.error('cup.js not loaded - cupSection not found');
          sectionBody.innerHTML = '<div class="section-placeholder">Failed to load cup section</div>';
        }
        break;

      case 'league':
        if (typeof window.leagueSection !== 'undefined') {
          window.leagueSection.activate({ section, subsection });
        } else {
          console.error('league.js not loaded - leagueSection not found');
          sectionBody.innerHTML = '<div class="section-placeholder">Failed to load league section</div>';
        }
        break;

      case 'config':
        if (typeof window.configSection !== 'undefined') {
          window.configSection.activate({ section, subsection });
        } else {
          console.error('placeholders.js not loaded - configSection not found');
          sectionBody.innerHTML = '<div class="section-placeholder">Failed to load config section</div>';
        }
        break;

      default:
        sectionBody.innerHTML = '<div class="section-placeholder">Section not found</div>';
    }
  } catch (error) {
    console.error('Failed to load section:', section, error);
    sectionBody.innerHTML = '<div class="section-placeholder">Failed to load section</div>';
  }
}

// ── Nav Pin Toggle ──────────────────────────────────────────────
function updateNavPinState() {
  if (navPinned) {
    bodyGrid.classList.add('nav-pinned');
    pinToggle.setAttribute('aria-label', 'Unpin navigation');
    pinToggle.setAttribute('aria-pressed', 'true');
  } else {
    bodyGrid.classList.remove('nav-pinned');
    pinToggle.setAttribute('aria-label', 'Pin navigation');
    pinToggle.setAttribute('aria-pressed', 'false');
  }

  // Store in localStorage
  try {
    localStorage.setItem('ap_nav_pinned', navPinned.toString());
  } catch (e) {
    console.warn('Could not save nav pin state to localStorage');
  }
}

function toggleNavPin() {
  navPinned = !navPinned;
  updateNavPinState();

  window.dispatchEvent(new CustomEvent('app:navPinChanged', {
    detail: { pinned: navPinned }
  }));
}

// ── Tooltip ─────────────────────────────────────────────────────
function showTooltip(navItem, text) {
  if (navPinned) return; // No tooltip when pinned

  // Render offscreen first so we can measure actual rendered size.
  tooltip.textContent = text;
  tooltip.style.left = '-9999px';
  tooltip.style.top = '0';
  tooltip.hidden = false;

  const navRect = navItem.getBoundingClientRect();
  const tipRect = tooltip.getBoundingClientRect();

  // Position to the right of nav item by default
  let left = navRect.right + 8;
  // Auto-flip to LEFT side when right side would clip viewport
  if (left + tipRect.width > window.innerWidth) {
    left = navRect.left - tipRect.width - 8;
  }
  const top = navRect.top + navRect.height / 2 - tipRect.height / 2;

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function hideTooltip() {
  tooltip.hidden = true;
}

// ── Health Check & Connection Monitoring ───────────────────────
async function checkHealth() {
  try {
    const response = await fetch(`${getApiBase()}/api/health`);
    if (response.ok) {
      connectionRestored();
    } else {
      connectionLost();
    }
  } catch (error) {
    connectionLost();
  }
}

function connectionLost() {
  connectionLostCount++;

  if (connectionLostCount >= 3) {
    // Show banner after 3 consecutive failures
    if (connectionLostBanner.hidden) {
      statusBar.style.display = 'none';
      connectionLostBanner.hidden = false;

      window.dispatchEvent(new CustomEvent('app:connectionLost', {
        detail: { lastSuccess: new Date().toISOString() }
      }));
    }
  }
}

function connectionRestored() {
  if (connectionLostCount > 0) {
    connectionLostCount = 0;

    if (!connectionLostBanner.hidden) {
      statusBar.style.display = 'flex';
      connectionLostBanner.hidden = true;

      window.dispatchEvent(new CustomEvent('app:connectionRestored', {
        detail: {}
      }));
    }
  }
}

function getApiBase() {
  return `${window.location.protocol}//${window.location.host}`;
}

function updateApiEndpoint() {
  const host = window.location.host;
  sbApi.textContent = `API · ${host}`;
}

// ── Event Handlers ──────────────────────────────────────────────
function setupEventHandlers() {
  // Pin toggle
  pinToggle.addEventListener('click', toggleNavPin);

  // Nav items
  navItems.forEach(item => {
    const section = item.dataset.section;

    item.addEventListener('click', () => {
      navigateToSection(section);
    });

    // Tooltip on hover (collapsed mode only). Source of truth for the
    // displayed label is the nav button's aria-label — same text screen
    // readers hear, no separate hardcoded mapping to drift.
    item.addEventListener('mouseenter', () => {
      if (tooltipTimer) clearTimeout(tooltipTimer);

      tooltipTimer = setTimeout(() => {
        if (!navPinned) {
          showTooltip(item, item.getAttribute('aria-label') || section);
        }
      }, 300);
    });

    item.addEventListener('mouseleave', () => {
      if (tooltipTimer) {
        clearTimeout(tooltipTimer);
        tooltipTimer = null;
      }
      hideTooltip();
    });

    item.addEventListener('focus', () => {
      // Show tooltip immediately on focus (no 300ms delay for keyboard users)
      if (!navPinned) {
        showTooltip(item, item.getAttribute('aria-label') || section);
      }
    });

    item.addEventListener('blur', () => {
      hideTooltip();
    });
  });

  // Hash change
  window.addEventListener('hashchange', () => {
    const route = parseRoute();
    activateSection(route.section, route.subsection);
  });

  // Listen for subtitle changes from sections
  window.addEventListener('shell:subtitleChanged', (event) => {
    if (event.detail && event.detail.subtitle) {
      shellSubtitle.textContent = event.detail.subtitle;
    }
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      hideTooltip();
    }
  });
}

// ── Initialization ──────────────────────────────────────────────
function initializeShell() {
  // Load nav pin state from localStorage
  try {
    const stored = localStorage.getItem('ap_nav_pinned');
    if (stored !== null) {
      navPinned = stored === 'true';
    }
  } catch (e) {
    console.warn('Could not load nav pin state from localStorage');
  }

  updateNavPinState();
  updateApiEndpoint();

  // Set up periodic health checks (every 5 seconds)
  healthCheckInterval = setInterval(checkHealth, 5000);

  // Initial health check
  checkHealth();

  // Parse initial route or default to matches
  const route = parseRoute();
  if (!route.section || route.section === 'matches') {
    // Default to matches
    if (!window.location.hash || window.location.hash === '#/') {
      window.location.hash = '#/matches';
    }
  }

  activateSection(route.section, route.subsection);
}

// ── Cleanup ─────────────────────────────────────────────────────
function cleanup() {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
  }

  if (tooltipTimer) {
    clearTimeout(tooltipTimer);
  }
}

// ── Exports for section modules ────────────────────────────────
window.shell = {
  navigateToSection,
  updateSubtitle: (subtitle) => {
    window.dispatchEvent(new CustomEvent('shell:subtitleChanged', {
      detail: { subtitle }
    }));
  },
  updateRightCap: (content) => {
    rightCap.innerHTML = content;
  },
  getApiBase
};

// ── Bootstrap ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupEventHandlers();
  initializeShell();
});

window.addEventListener('beforeunload', cleanup);