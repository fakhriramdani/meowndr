/**
 * @meowndr Asset Studio - Client Application Controller
 * Single-Page Visual Asset Management Interface.
 */

// Global State
const state = {
  currentTab: 'overview',
  overview: null,
  backgrounds: [],
  characters: [],
  props: [],
  otherAssets: null,
  collections: [],
  validation: null,
  selectedAsset: null,
  selectedCategory: 'all',
  selectedStatus: 'all',
  selectedTag: 'all',
  searchQuery: '',
  viewMode: 'grid',
  zoom: 1.0,
  canvasBg: 'checkerboard',
};

// API Client
const api = {
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      throw new Error(err.message || 'API request failed');
    }
    return res.json();
  },
  async post(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      throw new Error(err.message || 'API request failed');
    }
    return res.json();
  },
  async put(url, data) {
    const res = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      throw new Error(err.message || 'API request failed');
    }
    return res.json();
  },
  async delete(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      throw new Error(err.message || 'API request failed');
    }
    return res.json();
  },
};

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : '⚠️'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupGlobalActions();
  setupPreviewModal();
  setupAddAssetModal();
  setupEditModal();
  setupDeleteModal();

  await refreshAllData();
  renderCurrentTab();
});

async function refreshAllData() {
  try {
    const [ov, bgs, chars, props, other, colls] = await Promise.all([
      api.get('/api/overview'),
      api.get('/api/backgrounds'),
      api.get('/api/characters'),
      api.get('/api/props'),
      api.get('/api/other-assets'),
      api.get('/api/collections'),
    ]);

    state.overview = ov;
    state.backgrounds = bgs;
    state.characters = chars;
    state.props = props;
    state.otherAssets = other;
    state.collections = colls;

    // Update badges
    document.getElementById('badgeTotalAssets').textContent = ov.total_assets;
    document.getElementById('badgeBackgrounds').textContent = ov.backgrounds.total;
    document.getElementById('badgeCharacters').textContent = ov.characters.total;
    document.getElementById('badgeProps').textContent = ov.props.total;
    document.getElementById('badgeOther').textContent = ov.other_assets.foregrounds + ov.other_assets.brand;
    document.getElementById('badgeCollections').textContent = ov.collections_count;
    document.getElementById('badgeValidationIssues').textContent = ov.diagnostics.validation_errors_count;

    if (ov.diagnostics.validation_errors_count === 0) {
      document.getElementById('badgeValidationIssues').className = 'badge badge-active';
    } else {
      document.getElementById('badgeValidationIssues').className = 'badge badge-warning';
    }
  } catch (err) {
    showToast(`Failed to load asset data: ${err.message}`, 'error');
  }
}

// Navigation Handling
function setupNavigation() {
  document.querySelectorAll('.sidebar-nav .nav-item').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sidebar-nav .nav-item').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.currentTab = btn.dataset.tab;
      state.searchQuery = '';
      document.getElementById('globalSearchInput').value = '';
      renderCurrentTab();
    });
  });

  // Global Search
  const searchInput = document.getElementById('globalSearchInput');
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    renderCurrentTab();
  });

  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
  });

  // Theme Toggle
  const themeBtn = document.getElementById('btnThemeToggle');
  themeBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
  });
}

function setupGlobalActions() {
  document.getElementById('btnDownstreamSync').addEventListener('click', async () => {
    try {
      const res = await api.post('/api/sync', {});
      showToast(res.message || 'Downstream assets synchronized!');
      await refreshAllData();
      renderCurrentTab();
    } catch (err) {
      showToast(`Sync failed: ${err.message}`, 'error');
    }
  });

  document.getElementById('btnQuickAdd').addEventListener('click', () => {
    openAddModal();
  });
}

// Render Controller
function renderCurrentTab() {
  const stage = document.getElementById('mainStage');
  stage.innerHTML = '';

  switch (state.currentTab) {
    case 'overview':
      renderOverviewTab(stage);
      break;
    case 'backgrounds':
      renderBackgroundsTab(stage);
      break;
    case 'characters':
      renderCharactersTab(stage);
      break;
    case 'props':
      renderPropsTab(stage);
      break;
    case 'other':
      renderOtherAssetsTab(stage);
      break;
    case 'collections':
      renderCollectionsTab(stage);
      break;
    case 'validation':
      renderValidationTab(stage);
      break;
    default:
      renderOverviewTab(stage);
  }
}

// ----------------------------------------------------------------------------
// 1. Overview Tab
// ----------------------------------------------------------------------------
function renderOverviewTab(container) {
  const ov = state.overview;
  if (!ov) return;

  const html = `
    <div class="overview-hero-grid">
      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-title">Total Production Assets</span>
          <span class="kpi-icon">📦</span>
        </div>
        <div class="kpi-value">${ov.total_assets}</div>
        <div class="kpi-sub">Across 4 asset categories</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-title">Active Environments</span>
          <span class="kpi-icon">🌄</span>
        </div>
        <div class="kpi-value text-success">${ov.backgrounds.active}</div>
        <div class="kpi-sub">1080×1920 9:16 Vertical Cutout</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-title">Mascot & Characters</span>
          <span class="kpi-icon">🐱</span>
        </div>
        <div class="kpi-value" style="color: var(--primary);">${ov.characters.total}</div>
        <div class="kpi-sub">${ov.characters.variants_total} avatar variants • ${ov.characters.states_total} poses</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-title">Scientific Props</span>
          <span class="kpi-icon">🧪</span>
        </div>
        <div class="kpi-value text-accent">${ov.props.total}</div>
        <div class="kpi-sub">Interactive paper apparatus</div>
      </div>
    </div>

    <!-- Quick Actions Toolbar -->
    <div class="quick-actions-bar">
      <span class="qab-title">Quick Actions</span>
      <button class="btn btn-sm btn-outline" onclick="openAddModal('background')">+ Add Background</button>
      <button class="btn btn-sm btn-outline" onclick="openAddModal('character-variant')">+ Add Character Variant</button>
      <button class="btn btn-sm btn-outline" onclick="openAddModal('prop')">+ Add Prop</button>
      <button class="btn btn-sm btn-outline" onclick="switchTab('validation')">🛡️ Integrity Check (${ov.diagnostics.validation_errors_count} Issues)</button>
      <button class="btn btn-sm btn-outline" onclick="triggerSync()">🔄 Downstream Sync</button>
    </div>

    <!-- Overview Split Section -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
      <!-- Featured Environments Preview -->
      <div class="character-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 15px; font-weight: 700;">Featured 9:16 Papercraft Environments</h3>
          <button class="btn btn-xs btn-outline" onclick="switchTab('backgrounds')">View All (${state.backgrounds.length}) &rarr;</button>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
          ${state.backgrounds.slice(0, 4).map(b => `
            <div class="background-card" onclick="openPreview('${b.id}', 'background')">
              <div class="bg-thumbnail-box">
                <img src="/${b.thumbnailPath || b.assetPath}" alt="${b.name}">
                <div class="bg-card-overlay">
                  <span class="badge badge-active">${b.status.toUpperCase()}</span>
                </div>
              </div>
              <div class="bg-card-content">
                <div class="bg-card-title">${b.name}</div>
                <div class="bg-card-category">${b.category}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Mascot Card -->
      <div class="character-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 15px; font-weight: 700;">Canonical Cat Scientist</h3>
          <span class="badge badge-category">#F97316</span>
        </div>
        <div style="text-align: center; padding: 12px 0;">
          <img src="/assets/brand/cat-scientist-avatar-primary.png" style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid var(--primary); box-shadow: var(--shadow-md);">
          <div style="font-weight: 800; font-size: 16px; margin-top: 10px;">Cat Scientist Mascot</div>
          <div style="font-size: 12px; color: var(--text-muted);">Lead Presenter & STEM Guide</div>
        </div>
        <div style="border-top: 1px solid var(--border-color); padding-top: 12px; font-size: 12px; display: flex; flex-direction: column; gap: 6px;">
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">States / Poses:</span>
            <strong>10 Controllable States</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Anchor Line:</span>
            <strong>floor_y: 1380px</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Episodes Using:</span>
            <strong style="color: var(--success);">All Active Episodes</strong>
          </div>
        </div>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

// ----------------------------------------------------------------------------
// 2. Backgrounds Tab
// ----------------------------------------------------------------------------
function renderBackgroundsTab(container) {
  let bgs = [...state.backgrounds];

  // Filter by category
  if (state.selectedCategory !== 'all') {
    bgs = bgs.filter(b => (b.category || '').toLowerCase().includes(state.selectedCategory.toLowerCase()));
  }

  // Filter by status
  if (state.selectedStatus !== 'all') {
    bgs = bgs.filter(b => (b.status || 'active').toLowerCase() === state.selectedStatus.toLowerCase());
  }

  // Filter by search
  if (state.searchQuery) {
    const q = state.searchQuery;
    bgs = bgs.filter(b =>
      b.id.toLowerCase().includes(q) ||
      b.name.toLowerCase().includes(q) ||
      (b.description || '').toLowerCase().includes(q) ||
      (b.tags || []).some(t => t.toLowerCase().includes(q))
    );
  }

  // Get categories list
  const categories = Array.from(new Set(state.backgrounds.map(b => b.category).filter(Boolean)));

  const toolbarHtml = `
    <div class="toolbar-container">
      <div class="toolbar-left">
        <select class="select-control" id="bgCategoryFilter">
          <option value="all">All Categories (${state.backgrounds.length})</option>
          ${categories.map(c => `<option value="${c}" ${state.selectedCategory === c ? 'selected' : ''}>${c}</option>`).join('')}
        </select>

        <select class="select-control" id="bgStatusFilter">
          <option value="all" ${state.selectedStatus === 'all' ? 'selected' : ''}>All Statuses</option>
          <option value="active" ${state.selectedStatus === 'active' ? 'selected' : ''}>Active Only</option>
          <option value="disabled" ${state.selectedStatus === 'disabled' ? 'selected' : ''}>Disabled</option>
          <option value="archived" ${state.selectedStatus === 'archived' ? 'selected' : ''}>Archived</option>
        </select>
        
        <span style="font-size: 12px; color: var(--text-muted);">${bgs.length} matching</span>
      </div>

      <div class="toolbar-right">
        <div class="view-toggle">
          <button class="vt-btn ${state.viewMode === 'grid' ? 'active' : ''}" onclick="setViewMode('grid')">Grid</button>
          <button class="vt-btn ${state.viewMode === 'list' ? 'active' : ''}" onclick="setViewMode('list')">List</button>
        </div>
        <button class="btn btn-sm btn-primary" onclick="openAddModal('background')">+ Add Background</button>
      </div>
    </div>
  `;

  let contentHtml = '';
  if (bgs.length === 0) {
    contentHtml = `
      <div style="text-align: center; padding: 60px 20px; color: var(--text-muted);">
        <span style="font-size: 40px; display: block; margin-bottom: 12px;">🌄</span>
        <h3>No backgrounds match the current filter</h3>
        <p style="font-size: 13px; margin-top: 6px;">Try clearing filters or search query.</p>
      </div>
    `;
  } else if (state.viewMode === 'grid') {
    contentHtml = `
      <div class="asset-grid">
        ${bgs.map(b => {
          const stClass = b.status === 'active' ? 'badge-active' : (b.status === 'disabled' ? 'badge-disabled' : 'badge-archived');
          return `
            <div class="background-card" onclick="openPreview('${b.id}', 'background')">
              <div class="bg-thumbnail-box">
                <img src="/${b.thumbnailPath || b.assetPath}" alt="${b.name}" loading="lazy">
                <div class="bg-card-overlay">
                  <span class="badge ${stClass}">${b.status.toUpperCase()}</span>
                  <span class="badge badge-category">${b.aspectRatio}</span>
                </div>
                <div class="bg-card-bottom-overlay">
                  <span class="badge" style="background: rgba(0,0,0,0.6); color: #fff;">Floor ${b.floorY}px</span>
                </div>
              </div>
              <div class="bg-card-content">
                <div class="bg-card-title" title="${b.name}">${b.name}</div>
                <div class="bg-card-category">${b.category}</div>
                <div class="bg-card-meta">
                  <span>${b.dimensions.width}×${b.dimensions.height}</span>
                  <span>${b.format}</span>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  } else {
    // List View
    contentHtml = `
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
          <thead style="background: var(--bg-card-hover); border-bottom: 1px solid var(--border-color); color: var(--text-muted); font-size: 11px; text-transform: uppercase;">
            <tr>
              <th style="padding: 12px 16px;">Preview</th>
              <th style="padding: 12px 16px;">Name & ID</th>
              <th style="padding: 12px 16px;">Category</th>
              <th style="padding: 12px 16px;">Dimensions</th>
              <th style="padding: 12px 16px;">Floor Y</th>
              <th style="padding: 12px 16px;">Status</th>
              <th style="padding: 12px 16px; text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${bgs.map(b => `
              <tr style="border-bottom: 1px solid var(--border-color); cursor: pointer;" onclick="openPreview('${b.id}', 'background')">
                <td style="padding: 8px 16px;">
                  <img src="/${b.thumbnailPath || b.assetPath}" style="width: 36px; height: 64px; object-fit: cover; border-radius: 3px; display: block;">
                </td>
                <td style="padding: 12px 16px;">
                  <div style="font-weight: 700;">${b.name}</div>
                  <div style="font-size: 11px; color: var(--text-muted);">${b.id}</div>
                </td>
                <td style="padding: 12px 16px; color: var(--text-muted);">${b.category}</td>
                <td style="padding: 12px 16px;">${b.dimensions.width}×${b.dimensions.height} (${b.aspectRatio})</td>
                <td style="padding: 12px 16px;">${b.floorY}px</td>
                <td style="padding: 12px 16px;">
                  <span class="badge ${b.status === 'active' ? 'badge-active' : (b.status === 'disabled' ? 'badge-disabled' : 'badge-archived')}">
                    ${b.status.toUpperCase()}
                  </span>
                </td>
                <td style="padding: 12px 16px; text-align: right;">
                  <button class="btn btn-xs btn-outline" onclick="event.stopPropagation(); openEditModal('${b.id}', 'background')">Edit</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  container.innerHTML = toolbarHtml + contentHtml;

  // Bind toolbar events
  document.getElementById('bgCategoryFilter').addEventListener('change', (e) => {
    state.selectedCategory = e.target.value;
    renderBackgroundsTab(container);
  });

  document.getElementById('bgStatusFilter').addEventListener('change', (e) => {
    state.selectedStatus = e.target.value;
    renderBackgroundsTab(container);
  });
}

function setViewMode(mode) {
  state.viewMode = mode;
  renderCurrentTab();
}

// ----------------------------------------------------------------------------
// 3. Characters Tab
// ----------------------------------------------------------------------------
function renderCharactersTab(container) {
  const chars = state.characters;

  const html = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div>
        <h2 style="font-size: 18px; font-weight: 800;">Character Mascots & Avatars</h2>
        <p style="font-size: 13px; color: var(--text-muted);">First-class papercraft presenters with controllable animation states and transparent avatars.</p>
      </div>
      <button class="btn btn-sm btn-primary" onclick="openAddModal('character-variant')">+ Add Character Variant</button>
    </div>

    <div style="display: flex; flex-direction: column; gap: 24px;">
      ${chars.map(c => `
        <div class="character-card">
          <div class="character-card-header">
            <div class="char-avatar-circle">
              <img src="/${c.previewPath || 'assets/brand/cat-scientist-avatar-primary.png'}" alt="${c.name}">
            </div>
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <h3 style="font-size: 17px; font-weight: 800;">${c.name}</h3>
                <span class="badge badge-active">${c.status.toUpperCase()}</span>
                <span class="badge" style="background: ${c.primary_color}; color: #fff;">${c.primary_color}</span>
              </div>
              <p style="font-size: 13px; color: var(--text-muted); margin-top: 3px;">${c.description}</p>
            </div>
            <div style="margin-left: auto;">
              <button class="btn btn-sm btn-outline" onclick="openEditModal('${c.id}', 'character')">✏️ Edit Metadata</button>
            </div>
          </div>

          <!-- Avatar Variants Section -->
          <div>
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 10px;">
              Avatar Variants & Renders (${c.variants.length})
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px;">
              ${c.variants.map(v => `
                <div style="background: var(--bg-app); border: 1px solid var(--border-color); border-radius: var(--radius-sm); overflow: hidden; cursor: pointer;" onclick="openPreview('${c.id}', 'character', '${v.id}')">
                  <div class="canvas-checkerboard" style="height: 140px; display: flex; align-items: center; justify-content: center; position: relative;">
                    <img src="/${v.path}" style="max-height: 120px; max-width: 120px; object-fit: contain;">
                    <span class="badge badge-category" style="position: absolute; bottom: 6px; right: 6px;">${v.format}</span>
                  </div>
                  <div style="padding: 10px;">
                    <div style="font-weight: 700; font-size: 12px;">${v.name}</div>
                    <div style="font-size: 11px; color: var(--text-muted);">${v.dimensions.width}×${v.dimensions.height}</div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Controllable States -->
          <div>
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">
              Controllable Expression & Motion States (${c.states.length})
            </div>
            <div class="character-states-grid">
              ${c.states.map(s => `<span class="state-chip">🎭 ${s}</span>`).join('')}
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;

  container.innerHTML = html;
}

// ----------------------------------------------------------------------------
// 4. Props Tab
// ----------------------------------------------------------------------------
function renderPropsTab(container) {
  let props = [...state.props];

  if (state.searchQuery) {
    const q = state.searchQuery;
    props = props.filter(p =>
      p.id.toLowerCase().includes(q) ||
      p.name.toLowerCase().includes(q) ||
      (p.description || '').toLowerCase().includes(q)
    );
  }

  const html = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div>
        <h2 style="font-size: 18px; font-weight: 800;">Scientific Props & Apparatus</h2>
        <p style="font-size: 13px; color: var(--text-muted);">Movable papercraft models, glassware, apparatus, and demonstrational dioramas.</p>
      </div>
      <button class="btn btn-sm btn-primary" onclick="openAddModal('prop')">+ Add Prop</button>
    </div>

    <div class="asset-grid" style="grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));">
      ${props.map(p => `
        <div class="character-card" style="cursor: pointer;" onclick="openPreview('${p.id}', 'prop')">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="badge badge-category">PROP</span>
            <span class="badge badge-active">${p.status.toUpperCase()}</span>
          </div>
          <div style="height: 90px; background: var(--bg-app); border: 1px solid var(--border-color); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; font-size: 34px;">
            🧪
          </div>
          <div>
            <h4 style="font-size: 14px; font-weight: 700;">${p.name}</h4>
            <div style="font-size: 11px; color: var(--text-muted);">${p.id}</div>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 6px; line-height: 1.4;">${p.description || '2D papercraft scientific apparatus.'}</p>
          </div>
          <div style="border-top: 1px solid var(--border-color); padding-top: 8px; font-size: 11px; display: flex; justify-content: space-between; color: var(--text-muted);">
            <span>${p.dimensions.width}×${p.dimensions.height}px</span>
            <span>Anchor: ${p.dimensions.anchor || 'bottom'}</span>
          </div>
        </div>
      `).join('')}
    </div>
  `;

  container.innerHTML = html;
}

// ----------------------------------------------------------------------------
// 5. Other Assets (Brand & UI) Tab
// ----------------------------------------------------------------------------
function renderOtherAssetsTab(container) {
  const other = state.otherAssets;
  if (!other) return;

  const html = `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Brand Identity Assets -->
      <div>
        <h2 style="font-size: 18px; font-weight: 800; margin-bottom: 4px;">Channel & Brand Identity Assets</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">Logos, avatars, monograms, and official social media banners.</p>

        <div class="asset-grid" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));">
          ${other.brand.map(b => `
            <div class="background-card" onclick="openPreview('${b.id}', 'brand')">
              <div class="canvas-checkerboard" style="height: 140px; display: flex; align-items: center; justify-content: center;">
                <img src="/${b.path}" style="max-height: 110px; max-width: 90%; object-fit: contain;">
              </div>
              <div class="bg-card-content">
                <div class="bg-card-title">${b.name}</div>
                <div class="bg-card-meta">
                  <span>${b.dimensions.width}×${b.dimensions.height}</span>
                  <span class="badge badge-category">${b.format}</span>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Foregrounds & Banners -->
      <div>
        <h2 style="font-size: 18px; font-weight: 800; margin-bottom: 4px;">UI & Foreground Overlays</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">Papercraft headline banners, word tags, and caption pills.</p>

        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">
          ${other.foregrounds.map(f => `
            <div class="character-card">
              <div style="display: flex; justify-content: space-between;">
                <h4 style="font-size: 15px; font-weight: 700;">${f.name}</h4>
                <span class="badge badge-category">FOREGROUND</span>
              </div>
              <p style="font-size: 12px; color: var(--text-muted);">${f.description}</p>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

// ----------------------------------------------------------------------------
// 6. Collections Tab
// ----------------------------------------------------------------------------
function renderCollectionsTab(container) {
  const colls = state.collections;

  const html = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div>
        <h2 style="font-size: 18px; font-weight: 800;">Asset Collections</h2>
        <p style="font-size: 13px; color: var(--text-muted);">Curated thematic asset bundles for scene composition without altering canonical registries.</p>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 18px;">
      ${colls.map(c => `
        <div class="character-card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <h3 style="font-size: 16px; font-weight: 800;">${c.name}</h3>
              <span class="badge badge-category" style="margin-top: 4px;">${c.category}</span>
            </div>
            <span class="badge badge-active">${c.assetIds.length} Assets</span>
          </div>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.4;">${c.description}</p>

          <div style="border-top: 1px solid var(--border-color); padding-top: 10px;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">Included Assets:</div>
            <div class="tags-container">
              ${c.assetIds.map(id => `<span class="badge" style="cursor: pointer;" onclick="openPreview('${id}')">${id}</span>`).join('')}
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;

  container.innerHTML = html;
}

// ----------------------------------------------------------------------------
// 7. Validation Center Tab
// ----------------------------------------------------------------------------
async function renderValidationTab(container) {
  container.innerHTML = `
    <div style="text-align: center; padding: 40px;">
      <span class="pulse-dot" style="width: 12px; height: 12px; margin: 0 auto 12px;"></span>
      <p>Running comprehensive project integrity audit...</p>
    </div>
  `;

  try {
    const val = await api.get('/api/validation');
    state.validation = val;

    const html = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div>
          <h2 style="font-size: 18px; font-weight: 800;">Asset Validation & Diagnostics Center</h2>
          <p style="font-size: 13px; color: var(--text-muted);">Automated cross-check of dimension compliance, missing files, duplicate IDs, and episode references.</p>
        </div>
        <button class="btn btn-sm btn-primary" onclick="renderValidationTab(document.getElementById('mainStage'))">🔄 Re-run Full Audit</button>
      </div>

      <!-- Summary KPI -->
      <div class="overview-hero-grid" style="margin-bottom: 20px;">
        <div class="kpi-card">
          <div class="kpi-title">Audit Verdict</div>
          <div class="kpi-value ${val.is_valid ? 'text-success' : 'text-warning'}">
            ${val.is_valid ? 'ALL PASS' : 'ISSUES DETECTED'}
          </div>
          <div class="kpi-sub">${val.stats.total_issues} flagged item(s)</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Blocking Errors</div>
          <div class="kpi-value text-danger">${val.stats.errors_count}</div>
          <div class="kpi-sub">Must be resolved for gate sign-off</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Warnings & Advice</div>
          <div class="kpi-value text-warning">${val.stats.warnings_count}</div>
          <div class="kpi-sub">Non-blocking recommendations</div>
        </div>
      </div>

      <!-- Issues Table -->
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
          <thead style="background: var(--bg-card-hover); border-bottom: 1px solid var(--border-color); color: var(--text-muted); font-size: 11px; text-transform: uppercase;">
            <tr>
              <th style="padding: 12px 16px;">Severity</th>
              <th style="padding: 12px 16px;">Category</th>
              <th style="padding: 12px 16px;">Audit Message</th>
              <th style="padding: 12px 16px;">Suggested Action</th>
            </tr>
          </thead>
          <tbody>
            ${val.issues.length === 0 ? `
              <tr>
                <td colspan="4" style="padding: 30px; text-align: center; color: var(--success); font-weight: 700;">
                  ✓ Zero asset errors detected. All registered environments, characters, and props conform to production specifications!
                </td>
              </tr>
            ` : val.issues.map(iss => `
              <tr style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 12px 16px;">
                  <span class="badge ${iss.severity === 'ERROR' ? 'badge-danger' : 'badge-warning'}">${iss.severity}</span>
                </td>
                <td style="padding: 12px 16px; font-weight: 700; text-transform: uppercase; font-size: 11px;">${iss.category}</td>
                <td style="padding: 12px 16px;">${iss.message}</td>
                <td style="padding: 12px 16px; color: var(--text-muted); font-size: 12px;">${iss.suggestedAction}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<div class="toast toast-error">Failed to run validation: ${err.message}</div>`;
  }
}

// ----------------------------------------------------------------------------
// Interactive Preview Modal & Canvas
// ----------------------------------------------------------------------------
function setupPreviewModal() {
  document.getElementById('btnClosePreview').addEventListener('click', closePreview);

  // Zoom controls
  document.getElementById('btnZoomIn').addEventListener('click', () => {
    state.zoom = Math.min(state.zoom + 0.15, 3.0);
    applyZoom();
  });
  document.getElementById('btnZoomOut').addEventListener('click', () => {
    state.zoom = Math.max(state.zoom - 0.15, 0.25);
    applyZoom();
  });
  document.getElementById('btnZoom100').addEventListener('click', () => {
    state.zoom = 1.0;
    applyZoom();
  });
  document.getElementById('btnZoomFit').addEventListener('click', () => {
    state.zoom = 0.8;
    applyZoom();
  });

  // Canvas switcher
  document.querySelectorAll('.canvas-switcher .cs-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.canvas-switcher .cs-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const bg = btn.dataset.bg;
      state.canvasBg = bg;
      const canvas = document.getElementById('previewCanvasContainer');
      canvas.className = `preview-canvas-container canvas-${bg}`;
    });
  });

  // Action buttons
  document.getElementById('btnEditMetadata').addEventListener('click', () => {
    if (state.selectedAsset) {
      openEditModal(state.selectedAsset.id, state.selectedAsset.category);
    }
  });

  document.getElementById('btnToggleStatus').addEventListener('click', async () => {
    if (!state.selectedAsset) return;
    const current = state.selectedAsset.status || 'active';
    const next = current === 'active' ? 'disabled' : 'active';
    try {
      await api.post(`/api/backgrounds/${state.selectedAsset.id}/status`, { status: next, reason: `Changed via Studio UI` });
      showToast(`Asset status updated to ${next.toUpperCase()}`);
      closePreview();
      await refreshAllData();
      renderCurrentTab();
    } catch (err) {
      showToast(`Status change failed: ${err.message}`, 'error');
    }
  });

  document.getElementById('btnArchiveAsset').addEventListener('click', async () => {
    if (!state.selectedAsset) return;
    try {
      await api.post(`/api/backgrounds/${state.selectedAsset.id}/status`, { status: 'archived', reason: `Archived via Studio UI` });
      showToast(`Asset archived.`);
      closePreview();
      await refreshAllData();
      renderCurrentTab();
    } catch (err) {
      showToast(`Archive failed: ${err.message}`, 'error');
    }
  });

  document.getElementById('btnDeleteAsset').addEventListener('click', () => {
    if (state.selectedAsset) {
      openDeleteModal(state.selectedAsset);
    }
  });
}

async function openPreview(assetId, assetType = 'background', subId = null) {
  let asset = null;

  if (assetType === 'background') {
    asset = await api.get(`/api/backgrounds/${assetId}`);
  } else if (assetType === 'character') {
    asset = await api.get(`/api/characters/${assetId}`);
    if (subId && asset.variants) {
      const v = asset.variants.find(x => x.id === subId);
      if (v) {
        asset.customPreviewPath = v.path;
        asset.name = `${asset.name} (${v.name})`;
        asset.dimensions = v.dimensions;
        asset.format = v.format;
      }
    }
  } else if (assetType === 'prop') {
    asset = await api.get(`/api/props/${assetId}`);
  } else if (assetType === 'brand') {
    asset = state.otherAssets.brand.find(b => b.id === assetId);
  }

  if (!asset) {
    // Search general
    asset = state.backgrounds.find(b => b.id === assetId) ||
            state.props.find(p => p.id === assetId);
  }

  if (!asset) return;

  state.selectedAsset = asset;
  state.zoom = 1.0;
  applyZoom();

  // Populate preview elements
  document.getElementById('pvTitle').textContent = asset.name || asset.id;
  document.getElementById('pvCategory').textContent = asset.category || 'General';
  document.getElementById('pvStatus').textContent = (asset.status || 'ACTIVE').toUpperCase();
  document.getElementById('pvDimensions').textContent = asset.dimensions ? `${asset.dimensions.width}×${asset.dimensions.height}` : 'N/A';
  document.getElementById('pvFormat').textContent = asset.format || 'PNG';

  const imgSrc = '/' + (asset.customPreviewPath || asset.assetPath || asset.thumbnailPath || asset.path || 'assets/backgrounds/science-lab/background.png');
  const imgEl = document.getElementById('previewImage');
  imgEl.src = imgSrc;

  // Guides
  const isEnv = asset.category && (asset.category.includes('STEM') || asset.category.includes('Biology') || asset.category.includes('Nature') || asset.category.includes('Everyday') || asset.dimensions?.height === 1920);
  document.getElementById('pvFloorGuide').style.display = isEnv ? 'block' : 'none';

  // Metadata properties list
  const propsEl = document.getElementById('pvPropertiesList');
  propsEl.innerHTML = `
    <div class="prop-row"><span class="prop-key">ID</span><span class="prop-val">${asset.id}</span></div>
    <div class="prop-row"><span class="prop-key">Aspect Ratio</span><span class="prop-val">${asset.aspectRatio || '9:16'}</span></div>
    <div class="prop-row"><span class="prop-key">Floor Y</span><span class="prop-val">${asset.floorY || 1380}px</span></div>
    <div class="prop-row"><span class="prop-key">Mood</span><span class="prop-val">${asset.mood || 'Standard'}</span></div>
    <div class="prop-row"><span class="prop-key">Created At</span><span class="prop-val">${asset.createdAt || '2026-10-29'}</span></div>
  `;

  // Tags
  const tagsEl = document.getElementById('pvTagsContainer');
  tagsEl.innerHTML = (asset.tags || [asset.category]).map(t => `<span class="badge">${t}</span>`).join('');

  // References
  const refsEl = document.getElementById('pvReferencesList');
  const refs = asset.references || [];
  if (refs.length === 0) {
    refsEl.innerHTML = `<span style="font-size: 12px; color: var(--text-muted);">(No active episode references - Safe to edit/remove)</span>`;
  } else {
    refsEl.innerHTML = refs.map(r => `
      <div style="background: var(--bg-app); border: 1px solid var(--border-color); padding: 8px; border-radius: 4px; font-size: 12px; margin-bottom: 6px;">
        <strong>Episode: ${r.episode}</strong>
        <div style="color: var(--text-muted); font-size: 11px;">File: ${r.file}</div>
      </div>
    `).join('');
  }

  document.getElementById('previewModal').style.display = 'flex';
}

function closePreview() {
  document.getElementById('previewModal').style.display = 'none';
  state.selectedAsset = null;
}

function applyZoom() {
  const wrapper = document.getElementById('previewStageWrapper');
  if (wrapper) {
    wrapper.style.transform = `scale(${state.zoom})`;
    document.getElementById('zoomLevel').textContent = `${Math.round(state.zoom * 100)}%`;
  }
}

// ----------------------------------------------------------------------------
// Add Asset Modal & Upload
// ----------------------------------------------------------------------------
function setupAddAssetModal() {
  document.getElementById('btnCloseAddModal').addEventListener('click', closeAddModal);
  document.getElementById('btnCancelAdd').addEventListener('click', closeAddModal);

  const dropZone = document.getElementById('fileDropZone');
  const fileInput = document.getElementById('assetFileInput');

  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Form Submit
  document.getElementById('addAssetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const type = document.getElementById('addAssetType').value;
    const stagedPath = document.getElementById('stagedImagePath').value;

    if (!stagedPath) {
      showToast('Please select or upload an image file first.', 'error');
      return;
    }

    const payload = {
      id: document.getElementById('addAssetId').value.trim(),
      name: document.getElementById('addAssetName').value.trim(),
      category: document.getElementById('addAssetCategory').value.trim(),
      mood: document.getElementById('addAssetMood').value.trim(),
      description: document.getElementById('addAssetDescription').value.trim(),
      tags: document.getElementById('addAssetTags').value.split(',').map(t => t.trim()).filter(Boolean),
      imagePath: stagedPath,
    };

    try {
      if (type === 'background') {
        await api.post('/api/backgrounds', payload);
      } else if (type === 'prop') {
        await api.post('/api/props', payload);
      } else if (type === 'character-variant') {
        await api.post('/api/characters/cat-scientist/variants', {
          variantId: payload.id,
          imageSourcePath: stagedPath,
        });
      }

      showToast(`Asset '${payload.name}' registered & synced successfully!`);
      closeAddModal();
      await refreshAllData();
      renderCurrentTab();
    } catch (err) {
      showToast(`Registration failed: ${err.message}`, 'error');
    }
  });
}

function handleFileUpload(file) {
  const feedback = document.getElementById('fileUploadFeedback');
  feedback.style.display = 'block';
  feedback.textContent = `Processing '${file.name}' (${(file.size / 1024).toFixed(1)} KB)...`;

  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const res = await api.post('/api/upload', {
        filename: file.name,
        contentBase64: reader.result,
      });
      document.getElementById('stagedImagePath').value = res.stagedPath;
      feedback.textContent = `✓ Staged '${file.name}' ready for registration.`;
      feedback.className = 'upload-feedback text-success';

      // Auto-suggest ID and Name
      const baseName = file.name.replace(/\.[^/.]+$/, '').toLowerCase().replace(/[^a-z0-9_-]+/g, '-');
      if (!document.getElementById('addAssetId').value) {
        document.getElementById('addAssetId').value = baseName;
        document.getElementById('addAssetName').value = baseName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      }
    } catch (err) {
      feedback.textContent = `Upload failed: ${err.message}`;
      feedback.className = 'upload-feedback text-danger';
    }
  };
  reader.readAsDataURL(file);
}

function openAddModal(type = 'background') {
  document.getElementById('addAssetType').value = type;
  document.getElementById('addAssetForm').reset();
  document.getElementById('stagedImagePath').value = '';
  document.getElementById('fileUploadFeedback').style.display = 'none';
  document.getElementById('addAssetModal').style.display = 'flex';
}

function closeAddModal() {
  document.getElementById('addAssetModal').style.display = 'none';
}

// ----------------------------------------------------------------------------
// Edit Metadata Modal
// ----------------------------------------------------------------------------
function setupEditModal() {
  document.getElementById('btnCloseEditModal').addEventListener('click', closeEditModal);
  document.getElementById('btnCancelEdit').addEventListener('click', closeEditModal);

  document.getElementById('editAssetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('editAssetId').value;
    const type = document.getElementById('editAssetType').value;

    const updates = {
      name: document.getElementById('editAssetName').value.trim(),
      category: document.getElementById('editAssetCategory').value.trim(),
      floorY: parseInt(document.getElementById('editAssetFloorY').value, 10) || 1380,
      mood: document.getElementById('editAssetMood').value.trim(),
      description: document.getElementById('editAssetDescription').value.trim(),
      tags: document.getElementById('editAssetTags').value.split(',').map(t => t.trim()).filter(Boolean),
    };

    try {
      if (type === 'background') {
        await api.put(`/api/backgrounds/${id}`, updates);
      } else if (type === 'character') {
        await api.put(`/api/characters/${id}`, updates);
      }

      showToast(`Metadata for '${updates.name}' saved and synced!`);
      closeEditModal();
      closePreview();
      await refreshAllData();
      renderCurrentTab();
    } catch (err) {
      showToast(`Save failed: ${err.message}`, 'error');
    }
  });
}

function openEditModal(assetId, assetType) {
  const asset = state.backgrounds.find(b => b.id === assetId) ||
                state.characters.find(c => c.id === assetId);

  if (!asset) return;

  document.getElementById('editAssetId').value = asset.id;
  document.getElementById('editAssetType').value = assetType || 'background';
  document.getElementById('editAssetName').value = asset.name || '';
  document.getElementById('editAssetCategory').value = asset.category || '';
  document.getElementById('editAssetFloorY').value = asset.floorY || 1380;
  document.getElementById('editAssetMood').value = asset.mood || '';
  document.getElementById('editAssetDescription').value = asset.description || '';
  document.getElementById('editAssetTags').value = (asset.tags || []).join(', ');

  document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
}

// ----------------------------------------------------------------------------
// Delete Modal with Safety Guard
// ----------------------------------------------------------------------------
function setupDeleteModal() {
  document.getElementById('btnCloseDeleteModal').addEventListener('click', closeDeleteModal);
  document.getElementById('btnCancelDelete').addEventListener('click', closeDeleteModal);

  document.getElementById('btnConfirmDelete').addEventListener('click', async () => {
    if (!state.selectedAsset) return;

    const id = state.selectedAsset.id;
    const force = document.getElementById('delForceOverride').checked;
    const deletePhysical = document.getElementById('delDeletePhysical').checked;

    try {
      await api.delete(`/api/backgrounds/${id}?force=${force}&delete_asset=${deletePhysical}`);
      showToast(`Asset '${id}' removed from registry.`);
      closeDeleteModal();
      closePreview();
      await refreshAllData();
      renderCurrentTab();
    } catch (err) {
      showToast(`Removal failed: ${err.message}`, 'error');
    }
  });
}

function openDeleteModal(asset) {
  document.getElementById('delAssetId').textContent = asset.id;
  document.getElementById('delAssetName').textContent = asset.name;

  const refs = asset.references || [];
  const warnBox = document.getElementById('delRefWarningBox');
  const warnText = document.getElementById('delRefWarningText');

  if (refs.length > 0) {
    warnBox.style.display = 'flex';
    warnText.textContent = `This asset is referenced in ${refs.length} active location(s) across episode(s): ${Array.from(new Set(refs.map(r => r.episode))).join(', ')}.`;
  } else {
    warnBox.style.display = 'none';
  }

  document.getElementById('delForceOverride').checked = false;
  document.getElementById('delDeletePhysical').checked = false;
  document.getElementById('deleteConfirmModal').style.display = 'flex';
}

function closeDeleteModal() {
  document.getElementById('deleteConfirmModal').style.display = 'none';
}

// Helpers
function switchTab(tab) {
  const btn = document.querySelector(`.sidebar-nav [data-tab="${tab}"]`);
  if (btn) btn.click();
}

async function triggerSync() {
  document.getElementById('btnDownstreamSync').click();
}
