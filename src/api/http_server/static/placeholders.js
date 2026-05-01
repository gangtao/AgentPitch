// Agent Pitch — Placeholder Sections Module
// Manages visibility for unimplemented sections (Strategies, Arena, Config)

// ── Shared Section Management Logic ─────────────────────────────
function createSectionHandler(targetSectionId, sectionName) {
  return {
    activate({ section, subsection } = {}) {
      // All section IDs to manage
      const allSectionIds = ['section-matches', 'section-strategies', 'section-arena', 'section-config'];

      // Show target section, hide others
      allSectionIds.forEach(sectionId => {
        const sectionEl = document.getElementById(sectionId);
        if (!sectionEl) return;

        if (sectionId === targetSectionId) {
          sectionEl.removeAttribute('hidden');
        } else {
          sectionEl.setAttribute('hidden', '');
        }
      });

      // Fire subtitle change event
      window.dispatchEvent(new CustomEvent('shell:subtitleChanged', {
        detail: { subtitle: sectionName }
      }));

      console.log(`[placeholders.js] Activated ${sectionName.toLowerCase()} section`);
    },

    deactivate() {
      // Hide target section
      const targetSection = document.getElementById(targetSectionId);
      if (targetSection) {
        targetSection.setAttribute('hidden', '');
      }

      console.log(`[placeholders.js] Deactivated ${sectionName.toLowerCase()} section`);
    }
  };
}

// ── Export Section Objects ──────────────────────────────────────
// Note: strategiesSection is now provided by strategies.js module (Phase 3a implementation)
// Note: arenaSection is now provided by arena.js module — removed from placeholders 2026-04-28

// Config section delegates to the real config shell implementation
window.configSection = {
  activate({ section, subsection } = {}) {
    // Hide other sections
    const allSectionIds = ['section-matches', 'section-strategies', 'section-arena', 'section-config', 'section-cup', 'section-league'];
    allSectionIds.forEach(sectionId => {
      const sectionEl = document.getElementById(sectionId);
      if (!sectionEl) return;

      if (sectionId === 'section-config') {
        sectionEl.removeAttribute('hidden');
      } else {
        sectionEl.setAttribute('hidden', '');
      }
    });

    // Delegate to config shell for tab-specific handling
    if (typeof window.configShellSection !== 'undefined') {
      window.configShellSection.activate({ section, subsection });
    } else {
      console.error('config-shell.js not loaded - configShellSection not found');
      const sectionEl = document.getElementById('section-config');
      if (sectionEl) {
        sectionEl.innerHTML = '<div class="section-placeholder">Failed to load config shell</div>';
      }
    }
  },

  deactivate() {
    const targetSection = document.getElementById('section-config');
    if (targetSection) {
      targetSection.setAttribute('hidden', '');
    }

    if (typeof window.configShellSection !== 'undefined') {
      window.configShellSection.deactivate();
    }
  }
};

console.log('[placeholders.js] Placeholder sections module loaded');