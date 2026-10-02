// Exercise the actual page script and event handlers without network/CDN access.
// DOM/Leaflet doubles test wiring and state, not browser layout or tile rendering.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
const snapshots = Object.fromEntries(['gcp', 'aws', 'azure'].map(p => [p + '.json', JSON.parse(fs.readFileSync(path.join(root, p + '.json'), 'utf8'))]));
snapshots['accelerator_catalog.json'] = JSON.parse(fs.readFileSync(path.join(root, 'accelerator_catalog.json'), 'utf8'));

async function app({ search = '', responses = {} } = {}) {
  const ids = new Map();
  class Element {
    constructor(tag = 'div', id = '') {
      this.tag = tag; this.id = id; this.children = []; this.dataset = {};
      this.events = {}; this.value = ''; this.checked = false; this.selected = false;
      this.className = ''; this.textContent = ''; this.disabled = false;
      if (id) ids.set(id, this);
      this.classList = {
        contains: c => this.className.split(' ').includes(c),
        add: (...cs) => { this.className = [...new Set([...this.className.split(' '), ...cs])].join(' '); },
        remove: (...cs) => { this.className = this.className.split(' ').filter(c => !cs.includes(c)).join(' '); },
        toggle: (c, force) => {
          const on = force ?? !this.classList.contains(c);
          this.classList[on ? 'add' : 'remove'](c); return on;
        },
      };
    }
    get options() { return this.children.filter(e => e.tag === 'option'); }
    get selectedOptions() { return this.options.filter(e => e.selected); }
    set innerHTML(value) {
      this._html = value; this.children = [];
      for (const match of value.matchAll(/<(\w+)[^>]*id="([^"]+)"[^>]*>/g)) this.appendChild(new Element(match[1], match[2]));
    }
    get innerHTML() { return this._html || ''; }
    appendChild(e) { this.children.push(e); e.parent = this; return e; }
    replaceChildren() { this.children = []; }
    setAttribute(name, value) { this[name] = value; }
    addEventListener(event, fn) { this.events[event] = fn; }
    fire(event) { return this.events[event]?.({ target: this, currentTarget: this, stopPropagation() {} }); }
    insertAdjacentHTML(position, value) { this.innerHTML = value; }
    remove() { ids.delete(this.id); if (this.parent) this.parent.children = this.parent.children.filter(e => e !== this); }
  }
  const body = new Element('body');
  for (const match of html.matchAll(/<(\w+)([^>]*\sid="([^"]+)"[^>]*)>/g)) {
    const e = body.appendChild(new Element(match[1], match[3]));
    e.className = match[2].match(/class="([^"]*)"/)?.[1] || '';
    e.checked = /\schecked(?:\s|$)/.test(match[2]);
    e.value = match[2].match(/value="([^"]*)"/)?.[1] || '';
  }
  const walk = e => [e, ...e.children.flatMap(walk)];
  const queryAll = selector => {
    if (selector.startsWith('input[name="provider"]')) return [...ids.values()].filter(e => e.id.startsWith('provider-') && e.id !== 'provider-radios' && (!selector.endsWith(':checked') || e.checked));
    if (selector.startsWith('.')) {
      const [name, checked] = selector.slice(1).split(':');
      return walk(body).filter(e => e.classList.contains(name) && (!checked || e.checked));
    }
    throw new Error('Unhandled test selector: ' + selector);
  };
  const document = { body, getElementById: id => ids.get(id) || null, createElement: tag => new Element(tag), querySelectorAll: queryAll, querySelector: s => queryAll(s)[0] };
  const layer = () => ({ layers: [], addTo(target) { target.addLayer?.(this); return this; }, addLayer(e) { this.layers.push(e); }, clearLayers() { this.layers = []; } });
  const map = { panes: {}, setView(coords, zoom) { this.coords = coords; this.zoom = zoom; return this; }, getZoom() { return this.zoom; }, getPane(n) { return this.panes[n]; }, createPane(n) { this.panes[n] = { style: {} }; } };
  const marker = (coords, options) => ({ ...layer(), coords, options, events: {}, bindPopup(text) { this.popup = text; return this; }, on(event, fn) { this.events[event] = fn; return this; }, setStyle() {} });
  let tile;
  const L = { map: () => map, tileLayer: (url, options) => { tile = { url, options }; return layer(); }, layerGroup: layer, markerClusterGroup: layer, circleMarker: marker, marker, polyline: marker, divIcon: o => o, Point: function() {} };
  const location = { pathname: '/', search };
  const errors = [];
  const context = vm.createContext({ document, L, window: { location }, URLSearchParams, btoa, atob, setTimeout,
    navigator: { clipboard: { writeText: async () => {} } }, console: { error: (...args) => errors.push(args), warn() {} },
    history: { replaceState(a, b, url) { location.search = new URL(url, 'https://example.test').search; } },
    fetch: async file => responses[file] || { ok: true, json: async () => snapshots[file] },
  });
  await vm.runInContext(script, context); // Last expression is init()'s promise.
  const run = code => vm.runInContext(code, context);
  const plain = code => JSON.parse(JSON.stringify(run(code)));
  const input = value => { ids.get('dc-json-input').value = value; ids.get('update-dcs-btn').fire('click'); };
  return { run, plain, ids, input, location, map, tile, errors, queryAll };
}

test('page loads all three current snapshots and uses an attributed, keyless basemap', async () => {
  const a = await app();
  assert.equal(a.run('dataReady'), true);
  assert.equal(a.errors.length, 0);
  assert.equal(a.ids.get('update-dcs-btn').disabled, false);
  assert.equal(a.run('gcpData.length'), snapshots['gcp.json'].length);
  assert.equal(a.run('awsData.length'), snapshots['aws.json'].length);
  assert.equal(a.run('azureData.length'), snapshots['azure.json'].length);
  assert.equal(a.tile.url, 'https://tile.openstreetmap.org/{z}/{x}/{y}.png');
  assert.match(a.tile.options.attribution, /openstreetmap.org\/copyright/);
  assert.equal(a.tile.options.referrerPolicy, 'strict-origin-when-cross-origin');
});

test('lon input automatically selects a location and produces five sorted distances', async () => {
  const a = await app();
  a.input('{"Amsterdam":{"lat":52.36,"lon":4.9},"Tokyo":{"lat":35.68,"lng":139.69}}');
  assert.deepEqual(a.plain('selectedDC'), { name: 'Amsterdam', lat: 52.36, lng: 4.9 });
  assert.equal(a.ids.get('compare-all-btn').disabled, false);
  assert.equal(a.ids.get('location-select').value, 'Amsterdam');
  const rows = a.ids.get('results-content').children.at(-1).children;
  assert.equal(rows.length, 5);
  const distances = rows.map(row => Number(row.innerHTML.match(/>(\d+) km</)[1]));
  assert.deepEqual(distances, [...distances].sort((x, y) => x - y));
  assert.ok(distances[0] < 100);
  a.ids.get('location-select').value = 'Tokyo';
  a.ids.get('location-select').fire('change');
  assert.equal(a.run('selectedDC.name'), 'Tokyo');
  assert.match(a.ids.get('results-content').innerHTML, /Closest Regions to Tokyo/);
  assert.equal(new URLSearchParams(a.location.search).get('selected'), 'Tokyo');
  a.run('dcMarkers.Amsterdam.events.click()');
  assert.equal(a.ids.get('location-select').value, 'Amsterdam');
});

test('invalid manual coordinates preserve the applied locations and saved URL', async () => {
  const a = await app();
  a.input('{"Valid":{"lat":0,"lng":0}}');
  const saved = a.location.search;
  for (const value of ['null', '[]', '{"bad":null}', '{"bad":{"lat":91,"lng":0}}', '{"bad":{"lat":0,"lng":181}}', '{"bad":{"lat":"0","lng":0}}', '{"bad":{"lat":1e999,"lng":0}}', '{"bad":{"lat":0,"lng":0,"lon":1}}']) {
    a.input(value);
    assert.match(a.ids.get('json-status').textContent, /Invalid JSON/);
    assert.equal(a.run('selectedDC.name'), 'Valid');
    a.run('triggerUpdate()');
    assert.equal(a.location.search, saved);
  }
});

test('empty locations clear results, lines and comparison control', async () => {
  const a = await app();
  a.input('{"Zero":{"lat":0,"lng":0}}');
  a.input('{}');
  assert.equal(a.run('selectedDC'), null);
  assert.equal(a.run('linesLayer.layers.length'), 0);
  assert.equal(a.ids.get('compare-all-btn').disabled, true);
  assert.equal(a.ids.get('results-content').classList.contains('hidden'), true);
  assert.equal(a.ids.get('location-selector-container').classList.contains('hidden'), true);
});

test('unchecking the last category removes its filter', async () => {
  const a = await app();
  const cb = a.queryAll('.category-checkbox').find(e => e.dataset.category === 'H100');
  cb.checked = true; cb.fire('change');
  assert.ok(a.run('getSelectedAcceleratorTypes().length') > 0);
  cb.checked = false; cb.fire('change');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), []);
  assert.equal(new URLSearchParams(a.location.search).has('gpus'), false);
});

test('a shared raw-family selection stays exact, including after reload', async () => {
  const locations = btoa(encodeURIComponent('{"Tokyo":{"lat":35.68,"lon":139.69}}'));
  const a = await app({ search: '?' + new URLSearchParams({ gpus: 'A3 High', locations }) });
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['A3 High']);
  assert.equal(a.run('selectedDC.name'), 'Tokyo');
  const cb = a.queryAll('.category-checkbox').find(e => e.dataset.category === 'H100');
  assert.equal(cb.indeterminate, true);
  const b = await app({ search: a.location.search });
  assert.deepEqual(b.plain('getSelectedAcceleratorTypes()'), ['A3 High']);
  assert.equal(b.ids.get('compare-all-btn').disabled, false);
});

test('invalid URL locations are rejected without breaking provider map', async () => {
  for (const value of ['null', '{"bad":null}', '{"bad":{"lat":91,"lng":0}}']) {
    const a = await app({ search: '?locations=' + encodeURIComponent(btoa(encodeURIComponent(value))) });
    assert.equal(a.run('selectedDC'), null);
    assert.equal(a.run('gcpLayer.layers.length') > 0, true);
    assert.match(a.ids.get('json-status').textContent, /Failed to load/);
    assert.equal(a.ids.get('compare-all-btn').disabled, true);
  }
});

test('location names render as text in results, popups and comparison', async () => {
  const a = await app();
  const name = '<img src=x onerror=alert(1)>';
  a.input(JSON.stringify({ [name]: { lat: 52.36, lng: 4.9 } }));
  assert.match(a.ids.get('results-content').innerHTML, /&lt;img/);
  assert.match(a.run('Object.values(dcMarkers)[0].popup'), /&lt;img/);
  a.ids.get('compare-all-btn').fire('click');
  assert.match(a.run('document.body.innerHTML'), /&lt;img/);
  assert.doesNotMatch(a.run('document.body.innerHTML'), /<img/);
});

test('distance formula handles zero, dateline, and antipodes', async () => {
  const a = await app();
  assert.equal(a.run('getDistance(0, 0, 0, 0)'), 0);
  assert.ok(Math.abs(a.run('getDistance(0, 179, 0, -179)') - 222.39) < 0.1);
  assert.ok(Math.abs(a.run('getDistance(48.8566, 2.3522, -48.8566, -177.6478)') - 20015.09) < 0.1);
});

test('new Blackwell families appear in their GPU categories', async () => {
  const a = await app();
  assert.equal(a.run('categorize("P6-B300", "AWS")'), 'B300');
  assert.equal(a.run('categorize("NC_RTXPRO6000BSE_v6", "Azure")'), 'RTX PRO 6000');
});

test('provider and family filters apply to ranked results and comparison', async () => {
  const a = await app();
  a.input('{"Amsterdam":{"lat":52.36,"lng":4.9}}');
  a.ids.get('provider-all').checked = false;
  a.ids.get('provider-aws').checked = true;
  a.ids.get('provider-aws').fire('change');
  for (const option of a.ids.get('gpu-type').options) option.selected = option.value === 'P5';
  a.ids.get('gpu-type').fire('change');
  const rows = a.ids.get('results-content').children.at(-1).children;
  assert.equal(rows.length, 5);
  for (const row of rows) {
    assert.match(row.innerHTML, /chip-aws/);
    assert.match(row.innerHTML, /Matches: NVIDIA H100 \[P5\]</);
    assert.doesNotMatch(row.innerHTML, /chip-gcp|chip-azure|NaN/);
  }
  a.ids.get('compare-all-btn').fire('click');
  assert.match(a.run('document.body.innerHTML'), /chip-aws/);
  assert.doesNotMatch(a.run('document.body.innerHTML'), /chip-gcp|chip-azure|NaN/);
});

test('no matching family clears old distance lines and shows an explanation', async () => {
  const a = await app();
  a.input('{"Zero":{"lat":0,"lng":0}}');
  a.run('gcpData = []; awsData = []; azureData = []; triggerUpdate()');
  assert.match(a.ids.get('results-content').innerHTML, /No regions match/);
  assert.equal(a.run('linesLayer.layers.length'), 0);
});

test('failed or malformed provider loads show an error and disable proximity', async () => {
  for (const response of [{ ok: false, status: 503 }, { ok: true, json: async () => ({ error: 'bad' }) }, { ok: true, json: async () => [] }, { ok: true, json: async () => [{ region: 'bad', lat: null, lon: 1, families: [] }] }]) {
    const a = await app({ responses: { 'gcp.json': response } });
    assert.equal(a.run('dataReady'), false);
    assert.match(a.ids.get('data-status').textContent, /could not be loaded/);
    assert.equal(a.ids.get('update-dcs-btn').disabled, true);
  }
});

test('every mapped provider family has an explicit reviewed hardware entry', () => {
  const catalog = snapshots['accelerator_catalog.json'];
  assert.equal(catalog.schema_version, 1);
  assert.match(catalog.verified_on, /^\d{4}-\d{2}-\d{2}$/);
  for (const [provider, file] of [['GCP', 'gcp.json'], ['AWS', 'aws.json'], ['Azure', 'azure.json']]) {
    for (const family of new Set(snapshots[file].flatMap(record => record.families))) {
      const entry = catalog.families[family];
      assert.ok(entry, `Unclassified family needs review: ${provider} ${family}`);
      assert.equal(entry.provider, provider, `Wrong provider for ${family}`);
      assert.ok(catalog.models[entry.model], `Unknown model for ${family}`);
      assert.notEqual(entry.model, 'Unclassified');
      assert.equal(typeof entry.variant, 'string');
      assert.match(entry.source || catalog.sources[provider], /^https:\/\//);
    }
  }
});

test('GB and GPU-only Blackwell systems are distinct; unknown names are not guessed', async () => {
  const a = await app();
  for (const [family, provider, model] of [
    ['A4X Max', 'GCP', 'GB300'], ['A4X', 'GCP', 'GB200'], ['A4', 'GCP', 'B200'],
    ['P6e-GB300', 'AWS', 'GB300'], ['P6e-GB200', 'AWS', 'GB200'],
    ['P6-B300', 'AWS', 'B300'], ['P6-B200', 'AWS', 'B200'],
    ['G7', 'AWS', 'RTX PRO 4500'], ['G7e', 'AWS', 'RTX PRO 6000'],
    ['G4 (Fractional GPU)', 'GCP', 'RTX PRO 6000'],
    ['NVadsA10_v5-series', 'Azure', 'A10'], ['G5', 'AWS', 'A10G'],
    ['NDsr MI300X v5-Series', 'Azure', 'MI300X'],
  ]) assert.equal(a.run(`categorize(${JSON.stringify(family)}, ${JSON.stringify(provider)})`), model);
  for (const family of ['P6e', 'A4X Future', 'A3 Future', '__proto__', 'constructor']) {
    assert.equal(a.run(`categorize(${JSON.stringify(family)}, '')`), 'Unclassified');
  }
  assert.equal(a.run('categorize("A4X Max", "AWS")'), 'Unclassified');
});

test('model search finds documented AWS GB300 without inventing mapped regions', async () => {
  const a = await app();
  a.ids.get('hardware-search').value = 'GB300'; a.ids.get('hardware-search').fire('input');
  const entries = a.plain('getFilteredFamilyEntries().map(e => ({ family: e.family, model: e.model, regions: e.regions.size }))');
  assert.ok(entries.some(e => e.family === 'A4X Max' && e.regions > 0));
  assert.ok(entries.some(e => e.family === 'P6e-GB300' && e.regions === 0));
  assert.ok(entries.some(e => e.family === 'ND GB300-v6' && e.regions === 0));
  assert.equal(entries.every(e => e.model === 'GB300'), true);
  const aws = a.queryAll('.family-checkbox').find(e => e.dataset.family === 'P6e-GB300');
  assert.equal(aws.disabled, true);
  const model = a.queryAll('.category-checkbox').find(e => e.dataset.category === 'GB300');
  model.checked = true; model.fire('change');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['A4X Max']);
  a.ids.get('hardware-search').value = 'B300'; a.ids.get('hardware-search').fire('input');
  assert.deepEqual(a.plain('getFilteredFamilyEntries().map(e => e.family)'), ['P6-B300']);
});

test('family, provider, architecture and GPU-memory searches work', async () => {
  const a = await app();
  for (const [query, expected] of [['p6e', 'P6e-GB300'], ['aws blackwell', 'G7'], ['a100 80gb', 'A2 Ultra'], ['amd', 'NDsr MI300X v5-Series']]) {
    a.ids.get('hardware-search').value = query;
    assert.ok(a.plain('getFilteredFamilyEntries().map(e => e.family)').includes(expected), query);
  }
  a.ids.get('hardware-search').value = 'a100 80gb';
  assert.equal(a.plain('getFilteredFamilyEntries().map(e => e.family)').includes('NDasr A100 v4-Series'), false);
  assert.equal(a.plain('getFilteredFamilyEntries().map(e => e.family)').includes('NDamsr A100 v4-Series'), true);
});

test('family selection is exact and removable, without Cmd/Ctrl', async () => {
  const a = await app();
  const family = a.queryAll('.family-checkbox').find(e => e.dataset.family === 'A3 High');
  family.checked = true; family.fire('change');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['A3 High']);
  const chip = a.ids.get('selected-hardware').children[0];
  assert.match(chip.textContent, /GCP.*A3 High.*NVIDIA H100/);
  chip.fire('click');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), []);
  assert.equal(family.checked, false);
});

test('search and provider changes retain selections and show out-of-scope warnings', async () => {
  const a = await app();
  a.run('setFamilySelection(["A3 High"], true)');
  a.ids.get('hardware-search').value = 'B300'; a.ids.get('hardware-search').fire('input');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['A3 High']);
  a.ids.get('provider-all').checked = false; a.ids.get('provider-aws').checked = true;
  a.ids.get('provider-aws').fire('change');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['A3 High']);
  assert.match(a.ids.get('selection-status').textContent, /0 active.*No mapped regions can match/);
  a.input('{"Amsterdam":{"lat":52.36,"lng":4.9}}');
  assert.match(a.ids.get('results-content').innerHTML, /No regions match/);
  a.ids.get('provider-aws').checked = false; a.ids.get('provider-all').checked = true;
  a.ids.get('provider-all').fire('change');
  assert.match(a.ids.get('selection-status').textContent, /1 active/);
});

test('selecting a searched model preserves unrelated hidden selections', async () => {
  const a = await app();
  a.run('setFamilySelection(["A3 High"], true)');
  a.ids.get('hardware-search').value = 'a100 80gb'; a.ids.get('hardware-search').fire('input');
  const model = a.queryAll('.category-checkbox').find(e => e.dataset.category === 'A100');
  model.checked = true; model.fire('change');
  const selected = a.plain('getSelectedAcceleratorTypes()');
  assert.ok(selected.includes('A3 High'));
  assert.ok(selected.includes('A2 Ultra'));
  assert.equal(selected.includes('A2 Standard'), false);
  assert.equal(selected.includes('NDasr A100 v4-Series'), false);
  model.checked = false; model.fire('change');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['A3 High']);
});

test('GPU browsing separates AMD/NVIDIA GPUs from ASIC/FPGA/video accelerators', async () => {
  const a = await app();
  a.ids.get('hardware-kind').value = 'gpu';
  const gpu = a.plain('getFilteredFamilyEntries().map(e => e.family)');
  assert.ok(gpu.includes('NDsr MI300X v5-Series'));
  assert.equal(gpu.includes('Trn2'), false);
  assert.equal(gpu.includes('F2'), false);
  a.ids.get('hardware-kind').value = 'non-gpu';
  const other = a.plain('getFilteredFamilyEntries().map(e => e.family)');
  assert.ok(other.includes('Trn2')); assert.ok(other.includes('F2')); assert.ok(other.includes('VT1'));
  assert.equal(other.includes('A4X Max'), false);
});

test('stale shared family names fail closed and can be cleared', async () => {
  const a = await app({ search: '?gpus=Removed-Family' });
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), ['Removed-Family']);
  assert.match(a.ids.get('selection-status').textContent, /No mapped regions can match/);
  a.input('{"Amsterdam":{"lat":52.36,"lng":4.9}}');
  assert.match(a.ids.get('results-content').innerHTML, /No regions match/);
  a.ids.get('clear-hardware-btn').fire('click');
  assert.deepEqual(a.plain('getSelectedAcceleratorTypes()'), []);
  assert.equal(new URLSearchParams(a.location.search).has('gpus'), false);
});

test('catalog schema/source errors are visible instead of silently misclassifying hardware', async () => {
  for (const catalog of [{}, { ...snapshots['accelerator_catalog.json'], schema_version: 2 }, { ...snapshots['accelerator_catalog.json'], sources: { GCP: 'https://untrusted.example/', AWS: 'https://untrusted.example/', Azure: 'https://untrusted.example/' } }]) {
    const a = await app({ responses: { 'accelerator_catalog.json': { ok: true, json: async () => catalog } } });
    assert.equal(a.run('dataReady'), false);
    assert.match(a.ids.get('data-status').textContent, /could not be loaded/);
  }
});
