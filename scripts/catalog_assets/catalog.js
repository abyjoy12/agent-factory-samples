/* Progressive enhancement: the complete catalog and guide links work without JS. */
(() => {
  'use strict';
  const data = document.getElementById('catalog-data');
  if (!data) {
    const back = document.getElementById('back-to-catalog');
    const from = new URLSearchParams(location.search).get('catalog');
    if (back && from) {
      const safe = new URLSearchParams(from);
      for (const key of [...safe.keys()]) {
        if (!['q', 'application', 'domain', 'module', 'usecase', 'feature', 'sort'].includes(key)) safe.delete(key);
      }
      back.href = '../../../?' + safe.toString();
    }
    return;
  }
  const records = JSON.parse(data.textContent);
  const keys = ['application', 'domain', 'usecase', 'module', 'feature'];
  const labels = {application: 'Application', domain: 'Domain', usecase: 'Use case', module: 'Module', feature: 'Feature'};
  const grid = document.getElementById('agent-grid');
  const cards = new Map([...grid.children].map(card => [card.dataset.slug, card]));
  const search = document.getElementById('catalog-search');
  const sort = document.getElementById('sort-order');
  const inputs = [...document.querySelectorAll('.filters input')];
  const chips = document.getElementById('active-filters');
  const shareStatus = document.getElementById('share-status');
  const sidebar = document.getElementById('catalog-sidebar');
  const mobile = document.getElementById('mobile-filters');
  const validSorts = ['application', 'name', 'domain', 'usecase'];
  const vocabulary = Object.fromEntries(keys.map(k => [k, new Set(records.flatMap(r => r.facets[k]))]));
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const searchable = new Map(records.map(r => [r.slug, normalize(r.search + ' ' + Object.values(r.facets).flat().join(' '))]));
  let selected, query, ordering;
  function readURL() {
    const p = new URLSearchParams(location.search);
    query = p.get('q') || '';
    ordering = validSorts.includes(p.get('sort')) ? p.get('sort') : 'application';
    selected = Object.fromEntries(keys.map(k => [k, new Set(p.getAll(k).filter(v => vocabulary[k].has(v)))]));
    search.value = query;
    sort.value = ordering;
    inputs.forEach(input => { input.checked = selected[input.name].has(input.value); });
  }
  function params() {
    const p = new URLSearchParams();
    if (query.trim()) p.set('q', query.trim());
    keys.forEach(k => [...selected[k]].sort().forEach(v => p.append(k, v)));
    if (ordering !== 'application') p.set('sort', ordering);
    return p.toString();
  }
  function matches(r, ignore) {
    if (!normalize(query).trim().split(/\s+/).every(term => searchable.get(r.slug).includes(term))) return false;
    return keys.every(k => k === ignore || !selected[k].size || r.facets[k].some(v => selected[k].has(v)));
  }
  function chip(text, remove) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'filter-chip'; b.textContent = text + ' ×';
    b.setAttribute('aria-label', 'Remove ' + text);
    b.addEventListener('click', () => {
      const index = [...chips.children].indexOf(b);
      remove(); render(true);
      (chips.children[Math.min(index, chips.children.length - 1)] || search).focus();
    });
    chips.append(b);
  }
  function render(writeURL = false) {
    const encoded = params();
    if (writeURL) history.replaceState(null, '', location.pathname + (encoded ? '?' + encoded : '') + location.hash);
    shareStatus.textContent = '';
    chips.replaceChildren();
    if (query.trim()) chip('Search: ' + query.trim(), () => { query = ''; search.value = ''; });
    keys.forEach(k => selected[k].forEach(v => chip(labels[k] + ': ' + v, () => {
      selected[k].delete(v); inputs.filter(i => i.name === k && i.value === v).forEach(i => { i.checked = false; });
    })));
    const filtered = records.filter(r => matches(r));
    const visible = new Set(filtered.map(r => r.slug));
    const primary = r => ordering === 'name' ? r.name : (r.facets[ordering]?.[0] || r.name);
    const sorted = [...records].sort((a, b) => primary(a).localeCompare(primary(b)) || a.name.localeCompare(b.name));
    sorted.forEach(r => {
      const card = cards.get(r.slug); card.hidden = !visible.has(r.slug); grid.append(card);
      card.querySelectorAll('.agent-link').forEach(a => {
        a.href = r.page + (encoded ? '?' + new URLSearchParams({catalog: encoded}).toString() : '');
      });
    });
    document.getElementById('results-title').textContent = chips.children.length ? 'Your matches' : 'All agents';
    document.getElementById('result-count').textContent = filtered.length + ' of ' + records.length + ' agents' + (chips.children.length ? ' match your search' : ' to explore');
    document.getElementById('empty-state').hidden = filtered.length !== 0;
    inputs.forEach(input => {
      const n = records.filter(r => matches(r, input.name) && r.facets[input.name].includes(input.value)).length;
      input.parentElement.querySelector('.facet-count').textContent = n;
      input.disabled = n === 0 && !input.checked;
      input.parentElement.classList.toggle('unavailable', input.disabled);
    });
    const count = keys.reduce((n, k) => n + selected[k].size, 0);
    mobile.textContent = count ? 'Filters (' + count + ')' : 'Filters';
  }
  function clear() {
    query = ''; search.value = ''; selected = Object.fromEntries(keys.map(k => [k, new Set()]));
    inputs.forEach(i => { i.checked = false; }); render(true);
  }
  inputs.forEach(input => input.addEventListener('change', () => {
    input.checked ? selected[input.name].add(input.value) : selected[input.name].delete(input.value); render(true);
  }));
  search.addEventListener('input', () => { query = search.value; render(true); });
  sort.addEventListener('change', () => { ordering = sort.value; render(true); });
  document.getElementById('clear-sidebar').addEventListener('click', clear);
  document.getElementById('clear-empty').addEventListener('click', () => { clear(); search.focus(); });
  document.querySelectorAll('[data-preset]').forEach(link => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); query = ''; search.value = '';
    selected = Object.fromEntries(keys.map(k => [k, new Set()])); selected.usecase.add(link.dataset.preset);
    inputs.forEach(i => { i.checked = selected[i.name].has(i.value); }); render(true);
  }));
  document.getElementById('share-filters').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); shareStatus.textContent = 'Catalog link copied.'; }
    catch { shareStatus.textContent = 'Copy the URL from your address bar to share this view.'; }
  });
  mobile.addEventListener('click', () => {
    const expanded = mobile.getAttribute('aria-expanded') !== 'true';
    mobile.setAttribute('aria-expanded', String(expanded)); sidebar.classList.toggle('mobile-open', expanded);
    if (expanded) sidebar.querySelector('input:not(:disabled)')?.focus();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
      sidebar.classList.remove('mobile-open'); mobile.setAttribute('aria-expanded', 'false'); mobile.focus();
    }
  });
  window.addEventListener('popstate', () => { readURL(); render(); });
  readURL(); render();
  document.querySelectorAll('.js-control').forEach(e => { e.hidden = false; });
  document.documentElement.classList.add('catalog-ready');
})();
