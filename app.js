async function loadData() {
  const res = await fetch('data/latest.json', { cache: 'no-store' });
  if (!res.ok) throw new Error('Could not load latest data');
  return res.json();
}

function render(data) {
  document.getElementById('updated').textContent = `Updated: ${data.updated} · Sources: ${data.meta.totalSources} · Items: ${data.meta.totalItems}`;
  const app = document.getElementById('app');
  const template = document.getElementById('section-template');

  // Decision-first panel
  if (data.changes) {
    const node = template.content.cloneNode(true);
    node.querySelector('h2').textContent = 'What changed since yesterday';
    const ul = node.querySelector('ul');

    const summary = document.createElement('li');
    summary.innerHTML = `<strong>${data.changes.summary}</strong>`;
    ul.appendChild(summary);

    if (data.changes.previousUpdated) {
      const prev = document.createElement('li');
      prev.innerHTML = `<small>Compared against snapshot: ${data.changes.previousUpdated}</small>`;
      ul.appendChild(prev);
    }

    for (const item of (data.changes.newItems || [])) {
      const li = document.createElement('li');
      const date = item.published ? ` (${item.published})` : '';
      li.innerHTML = `🆕 <a href="${item.url}" target="_blank" rel="noopener">${item.title}</a>${date}<br><small>${item.source} · ${item.section}</small>`;
      ul.appendChild(li);
    }

    app.appendChild(node);
  }

  for (const section of data.sections) {
    const node = template.content.cloneNode(true);
    node.querySelector('h2').textContent = section.title;
    const ul = node.querySelector('ul');

    for (const item of section.items) {
      const li = document.createElement('li');
      const date = item.published ? ` (${item.published})` : '';
      li.innerHTML = `<a href="${item.url}" target="_blank" rel="noopener">${item.title}</a>${date}<br><small>${item.source}</small>`;
      ul.appendChild(li);
    }
    app.appendChild(node);
  }
}

loadData().then(render).catch((err) => {
  document.getElementById('updated').textContent = `Data load error: ${err.message}`;
});
