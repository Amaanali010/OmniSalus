/* ==========================================================================
   OmniSalus Unified Admin Dashboard Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initAdminDashboard();
});

function initAdminDashboard() {
  let currentModel = 'all';
  let currentSeverity = 'all';
  let searchQuery = '';
  let searchDebounceTimer = null;

  const tableBody = document.getElementById('adminTableBody');
  const emptyState = document.getElementById('adminEmptyState');
  const recordCounter = document.getElementById('recordCounter');
  const searchInput = document.getElementById('adminSearchInput');
  const severitySelect = document.getElementById('adminSeverityFilter');
  const btnRefresh = document.getElementById('btnRefreshAdmin');
  const chips = document.querySelectorAll('.admin-chip');

  // Stats elements
  const statTotal = document.getElementById('statTotalAssessments');
  const statToday = document.getElementById('statTodayAssessments');
  const statHighRisk = document.getElementById('statHighRiskAlerts');
  const statTopModule = document.getElementById('statTopModule');

  // Modal elements
  const detailModal = document.getElementById('recordDetailModal');
  const btnCloseModal = document.getElementById('btnCloseDetailModal');
  const btnCloseModalBtn = document.getElementById('btnCloseDetailModalBtn');

  // ------------------------------------------------------------------------
  // 1. MODULE ICONS & BADGE HELPERS
  // ------------------------------------------------------------------------
  const MODULE_METADATA = {
    'heart': { name: 'Heart Disease', icon: 'fa-heart-pulse', colorClass: 'badge-heart' },
    'diabetes': { name: 'Diabetes Risk', icon: 'fa-droplet', colorClass: 'badge-diabetes' },
    'stroke': { name: 'Stroke Vulnerability', icon: 'fa-brain', colorClass: 'badge-stroke' },
    'liver': { name: 'Liver Health', icon: 'fa-flask', colorClass: 'badge-liver' },
    'kidney': { name: 'Kidney & Renal', icon: 'fa-kidneys', colorClass: 'badge-kidney' },
    'breast-cancer': { name: 'Breast Cancer', icon: 'fa-ribbon', colorClass: 'badge-breast' },
    'obesity': { name: 'Obesity Level', icon: 'fa-weight-scale', colorClass: 'badge-obesity' }
  };

  function getModuleMeta(type) {
    return MODULE_METADATA[type] || { name: type, icon: 'fa-notes-medical', colorClass: 'badge-default' };
  }

  function getSeverityClass(sev) {
    const s = String(sev || '').toLowerCase();
    if (s.includes('high') || s.includes('danger') || s.includes('malignant') || s.includes('obesity iii') || s.includes('alert')) {
      return 'sev-high';
    }
    if (s.includes('moderate') || s.includes('overweight') || s.includes('elevated') || s.includes('obesity i')) {
      return 'sev-moderate';
    }
    return 'sev-low';
  }

  function getRelativeTimespan(isoStr) {
    try {
      const date = new Date(isoStr);
      const diffMs = Date.now() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays}d ago`;
    } catch (_) {
      return '';
    }
  }

  // ------------------------------------------------------------------------
  // 2. FETCH & RENDER STATS
  // ------------------------------------------------------------------------
  async function loadStats() {
    try {
      const res = await fetch('/api/admin/stats');
      const data = await res.json();
      if (data.status === 'success' && data.stats) {
        const s = data.stats;
        if (statTotal) statTotal.textContent = s.total_assessments.toLocaleString();
        if (statToday) statToday.textContent = s.today_assessments.toLocaleString();
        if (statHighRisk) statHighRisk.textContent = s.high_risk_alerts.toLocaleString();
        if (statTopModule) {
          const meta = getModuleMeta(s.top_active_module);
          statTopModule.textContent = meta.name;
        }
      }
    } catch (err) {
      console.warn('[Admin] Failed to load stats:', err);
    }
  }

  // ------------------------------------------------------------------------
  // 3. FETCH & RENDER ASSESSMENT RECORDS
  // ------------------------------------------------------------------------
  async function loadRecords() {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="table-loading-cell">
          <i class="fa-solid fa-spinner fa-spin"></i> Querying SQLite database...
        </td>
      </tr>
    `;
    emptyState.style.display = 'none';

    try {
      const params = new URLSearchParams({
        model_type: currentModel,
        severity: currentSeverity,
        search: searchQuery
      });

      const res = await fetch(`/api/admin/records?${params.toString()}`);
      const data = await res.json();

      if (data.status !== 'success' || !data.records || data.records.length === 0) {
        tableBody.innerHTML = '';
        emptyState.style.display = 'block';
        if (recordCounter) recordCounter.textContent = 'Showing 0 records';
        return;
      }

      emptyState.style.display = 'none';
      if (recordCounter) recordCounter.textContent = `Showing ${data.records.length} record${data.records.length === 1 ? '' : 's'}`;

      tableBody.innerHTML = data.records.map(rec => {
        const meta = getModuleMeta(rec.model_type);
        const sevClass = getSeverityClass(rec.severity);
        const relativeTime = getRelativeTimespan(rec.created_at);
        const scoreDisplay = rec.risk_score !== null && rec.risk_score !== undefined
          ? (rec.model_type === 'obesity' ? `BMI ${rec.risk_score}` : `${rec.risk_score}%`)
          : 'Evaluated';

        return `
          <tr id="row_${rec.id}">
            <td class="record-id-cell">#${rec.id}</td>
            <td class="timespan-cell">
              <strong>${rec.timespan_formatted}</strong>
              <small class="timespan-badge">${relativeTime}</small>
            </td>
            <td>
              <span class="module-chip-badge ${meta.colorClass}">
                <i class="fa-solid ${meta.icon}"></i> ${meta.name}
              </span>
            </td>
            <td class="diagnosis-cell">
              <strong>${rec.diagnosis}</strong>
            </td>
            <td>
              <span class="severity-chip ${sevClass}">
                ${rec.severity || 'Normal'}
              </span>
            </td>
            <td class="score-cell">
              <code>${scoreDisplay}</code>
            </td>
            <td class="actions-cell">
              <button type="button" class="btn-action-view" data-id="${rec.id}" title="Inspect full biomarkers">
                <i class="fa-solid fa-eye"></i> View
              </button>
              <button type="button" class="btn-action-del" data-id="${rec.id}" title="Delete record from SQLite">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </td>
          </tr>
        `;
      }).join('');

      // Wire up view and delete buttons
      tableBody.querySelectorAll('.btn-action-view').forEach(btn => {
        btn.addEventListener('click', () => openRecordDetails(btn.dataset.id));
      });

      tableBody.querySelectorAll('.btn-action-del').forEach(btn => {
        btn.addEventListener('click', () => confirmDeleteRecord(btn.dataset.id));
      });

    } catch (err) {
      console.error('[Admin] Query error:', err);
      tableBody.innerHTML = `
        <tr>
          <td colspan="7" class="table-loading-cell" style="color: #f87171;">
            <i class="fa-solid fa-circle-exclamation"></i> Error loading records from server: ${err.message}
          </td>
        </tr>
      `;
    }
  }

  // ------------------------------------------------------------------------
  // 4. RECORD DETAILS INSPECTOR MODAL
  // ------------------------------------------------------------------------
  async function openRecordDetails(recordId) {
    try {
      const res = await fetch(`/api/admin/records/${recordId}`);
      const data = await res.json();
      if (data.status !== 'success' || !data.record) {
        showToast('Could not load record details.');
        return;
      }

      const rec = data.record;
      const meta = getModuleMeta(rec.model_type);

      document.getElementById('modalDetailTitle').textContent = `${meta.name} Assessment`;
      document.getElementById('modalDetailSubtitle').textContent = `Database Record #${rec.id} · IP: ${rec.ip_address || 'Localhost'}`;
      document.getElementById('detailTimespan').textContent = rec.timespan_formatted;
      document.getElementById('detailModule').textContent = meta.name;
      document.getElementById('detailSeverity').textContent = rec.severity;
      document.getElementById('detailScore').textContent = rec.risk_score !== null ? `${rec.risk_score}%` : 'N/A';
      document.getElementById('detailDiagnosisText').textContent = rec.diagnosis;

      // Render Biomarkers Grid
      const grid = document.getElementById('biomarkersGrid');
      grid.innerHTML = '';

      if (rec.inputs && typeof rec.inputs === 'object') {
        const entries = Object.entries(rec.inputs).filter(([k]) => k !== 'model_variant');
        if (entries.length === 0) {
          grid.innerHTML = '<span style="color:var(--text-muted);">No input fields recorded.</span>';
        } else {
          entries.forEach(([key, val]) => {
            const item = document.createElement('div');
            item.className = 'biomarker-item';
            item.innerHTML = `
              <span class="bio-key">${key}</span>
              <strong class="bio-val">${val}</strong>
            `;
            grid.appendChild(item);
          });
        }
      }

      // Raw JSON
      document.getElementById('rawOutputBox').textContent = JSON.stringify(rec.result, null, 2);

      // Open modal
      detailModal.classList.add('open');
      document.body.classList.add('modal-open');

    } catch (err) {
      showToast('Error fetching record details.');
    }
  }

  function closeDetailModal() {
    detailModal.classList.remove('open');
    document.body.classList.remove('modal-open');
  }

  if (btnCloseModal) btnCloseModal.addEventListener('click', closeDetailModal);
  if (btnCloseModalBtn) btnCloseModalBtn.addEventListener('click', closeDetailModal);
  detailModal?.addEventListener('click', (e) => {
    if (e.target === detailModal) closeDetailModal();
  });

  // ------------------------------------------------------------------------
  // 5. DELETE RECORD
  // ------------------------------------------------------------------------
  async function confirmDeleteRecord(recordId) {
    if (!confirm(`Are you sure you want to permanently delete Assessment #${recordId} from SQLite?`)) {
      return;
    }

    try {
      const res = await fetch(`/api/admin/records/${recordId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.status === 'success') {
        showToast(`Record #${recordId} deleted successfully.`);
        const row = document.getElementById(`row_${recordId}`);
        if (row) row.remove();
        loadStats();
        // Check if table is empty
        if (tableBody.children.length === 0) {
          emptyState.style.display = 'block';
        }
      } else {
        showToast(data.message || 'Failed to delete record.');
      }
    } catch (err) {
      showToast('Error communicating with server.');
    }
  }

  // ------------------------------------------------------------------------
  // 6. EVENT LISTENERS & FILTERING
  // ------------------------------------------------------------------------
  // Category tabs
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => {
        c.classList.remove('active');
        c.setAttribute('aria-selected', 'false');
      });
      chip.classList.add('active');
      chip.setAttribute('aria-selected', 'true');
      currentModel = chip.dataset.model;
      loadRecords();
    });
  });

  // Severity filter
  if (severitySelect) {
    severitySelect.addEventListener('change', () => {
      currentSeverity = severitySelect.value;
      loadRecords();
    });
  }

  // Search input debounced
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        searchQuery = searchInput.value.trim();
        loadRecords();
      }, 250);
    });
  }

  // Refresh button
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      btnRefresh.innerHTML = `<i class="fa-solid fa-arrows-rotate fa-spin"></i> Refreshing...`;
      loadStats();
      loadRecords().finally(() => {
        setTimeout(() => {
          btnRefresh.innerHTML = `<i class="fa-solid fa-arrows-rotate"></i> Refresh`;
        }, 400);
      });
    });
  }

  // Initial load
  loadStats();
  loadRecords();
}
