// Shared modal helpers — extracted 2026-04-25 from matches.js and strategies.js
// after both grew nearly-identical type-to-confirm delete dialogs that drifted
// (strategies' version was missing design-system base classes — bug fixed,
// then unified here so the drift can't recur).
//
// Pattern 18 a11y: focus trap, ESC-to-dismiss, restore focus to the trigger.

/**
 * Show a "type the name to confirm" delete dialog.
 *
 * Caller provides the copy + the actual delete action; the helper owns the
 * dialog lifecycle, focus management, and input validation.
 *
 * @param {object}   opts
 * @param {string}   opts.title         Dialog title (e.g. "Delete strategy foo?")
 * @param {string}   opts.body          One-line explanation above the input
 * @param {string}   opts.expectedText  User must type this exactly to enable Delete
 * @param {function} opts.onConfirm     async (ctx) => void; ctx exposes:
 *                                       - setBusy(label)  flip button to "Deleting…", disable inputs
 *                                       - setError(msg)   flash an error label on the button (auto-resets)
 *                                       - close()         dismiss the modal
 */
export function showDeleteConfirmModal({ title, body, expectedText, onConfirm }) {
  const triggerElement = document.activeElement;

  const modal = document.createElement('div');
  modal.className = 'delete-modal-overlay';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'delete-modal-title');
  modal.innerHTML = `
    <div class="delete-modal">
      <div class="delete-modal-title" id="delete-modal-title"></div>
      <div class="delete-modal-body">
        <span class="delete-modal-body-text"></span>
        <br><br>
        Type the name to confirm:
        <br>
        <input type="text" class="ipt delete-confirm-input" autocomplete="off"
               aria-label="Type the name to confirm deletion">
      </div>
      <div class="delete-modal-actions">
        <button class="btn delete-modal-cancel">Cancel</button>
        <button class="btn btn-danger delete-modal-confirm" disabled>Delete</button>
      </div>
    </div>
  `;

  // Inject the dynamic copy via textContent (XSS-safe — names and prose
  // never get HTML-interpreted even if they contain <, >, or &).
  modal.querySelector('.delete-modal-title').textContent = title;
  modal.querySelector('.delete-modal-body-text').textContent = body;
  const input = modal.querySelector('.delete-confirm-input');
  input.placeholder = expectedText;

  const cancelBtn  = modal.querySelector('.delete-modal-cancel');
  const confirmBtn = modal.querySelector('.delete-modal-confirm');

  // ── Lifecycle helpers + ctx exposed to onConfirm ──────────────────────
  function close() {
    document.removeEventListener('keydown', trapHandler);
    modal.remove();
    if (triggerElement && typeof triggerElement.focus === 'function') {
      triggerElement.focus();
    }
  }

  function setBusy(label) {
    confirmBtn.disabled = true;
    cancelBtn.disabled = true;
    input.disabled = true;
    confirmBtn.textContent = label || 'Working…';
  }

  function setError(msg) {
    confirmBtn.textContent = msg || 'Failed';
    setTimeout(() => {
      // Re-enable for retry, restore label.
      confirmBtn.textContent = 'Delete';
      cancelBtn.disabled = false;
      input.disabled = false;
      // Re-validate — only enable confirm if input still matches.
      confirmBtn.disabled = input.value !== expectedText;
    }, 2000);
  }

  const ctx = { setBusy, setError, close };

  // ── Wire interaction ─────────────────────────────────────────────────
  input.oninput = () => {
    confirmBtn.disabled = input.value !== expectedText;
  };

  cancelBtn.onclick = close;
  confirmBtn.onclick = async () => {
    if (confirmBtn.disabled) return;
    try {
      await onConfirm(ctx);
    } catch (err) {
      console.error('[modals] onConfirm threw:', err);
      setError('Failed');
    }
  };

  // Backdrop click to dismiss (ignore clicks on the inner modal).
  modal.onclick = (e) => {
    if (e.target === modal) close();
  };

  // Focus trap + ESC handler (Pattern 18).
  const focusableSelectors = '.delete-confirm-input, .delete-modal-cancel, .delete-modal-confirm';
  function trapHandler(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
      return;
    }
    if (e.key !== 'Tab') return;
    const focusable = Array.from(modal.querySelectorAll(focusableSelectors))
      .filter(el => !el.disabled && el.offsetParent !== null);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
  document.addEventListener('keydown', trapHandler);

  document.body.appendChild(modal);

  // Focus the input on next tick (after layout).
  setTimeout(() => input.focus(), 100);

  // Stash the close callback so external code (e.g. section deactivation)
  // can dismiss the modal without touching its internals.
  modal._close = close;
}

/**
 * Dismiss any open delete-confirm modal (e.g. when the user navigates away
 * from the section that opened it). No-op when no modal is open. Triggers
 * full cleanup: focus restoration + keydown listener removal.
 */
export function dismissOpenDeleteConfirmModal() {
  const modal = document.querySelector('.delete-modal-overlay');
  if (modal && typeof modal._close === 'function') {
    modal._close();
  }
}
