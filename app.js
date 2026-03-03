const data = {
  updated: new Date().toISOString(),
  sections: [
    {
      title: 'MAM + Workflow Signals',
      items: [
        'iconik changelog monitoring: prioritize metadata quality, search relevance, and review workflows.',
        'LucidLink release notes: watch for caching/perf/admin controls that reduce producer friction.',
        'Backlight ecosystem: identify integration opportunities that shorten clip-to-publish cycle times.'
      ]
    },
    {
      title: 'Video-first Distribution Trends',
      items: [
        'Vertical-first packaging and platform-native hooks are now baseline for audience growth.',
        'Editorial teams are moving to rapid multi-cut workflows: one source package, many channel variants.',
        'Distribution strategy is shifting from “publish once” to “continuous repackaging”.'
      ]
    },
    {
      title: 'AI Automation Opportunities',
      items: [
        'Auto-generate shot-level metadata and candidate clips for faster commissioning.',
        'Create social caption/thumbnail variants and score them before publishing.',
        'Build daily “what changed” agent loops for vendors + competitors + platform formats.'
      ]
    },
    {
      title: 'Experiments for The Guardian (next 14 days)',
      items: [
        'Run a 3-format pilot: same story cut for YouTube Shorts, Instagram Reels, TikTok.',
        'Measure metadata completeness vs retrieval speed in iconik to quantify ops gains.',
        'Trial an AI-assisted clip shortlist for one desk; track edit-time saved and publish velocity.'
      ]
    },
    {
      title: 'Daily Sources to Monitor',
      items: [
        '<a href="https://help.iconik.backlight.co/hc/en-us/articles/25304685702167-Iconik-Web-Changelog">iconik web changelog</a>',
        '<a href="https://support.lucidlink.com/hc/en-us/sections/31125638256269-Release-notes">LucidLink release notes</a>',
        '<a href="https://www.backlight.co/">Backlight news</a>'
      ]
    }
  ]
};

document.getElementById('updated').textContent = `Updated: ${data.updated}`;
const app = document.getElementById('app');
const template = document.getElementById('section-template');

for (const section of data.sections) {
  const node = template.content.cloneNode(true);
  node.querySelector('h2').textContent = section.title;
  const ul = node.querySelector('ul');
  for (const item of section.items) {
    const li = document.createElement('li');
    li.innerHTML = item;
    ul.appendChild(li);
  }
  app.appendChild(node);
}
