import fs from 'node:fs/promises';

const UA = 'AIOMetadata/research';
const outPath = 'research/profile3-letterboxd-source-research.json';

function stripTags(s) {
  return s.replace(/<[^>]*>/g, ' ').replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/\s+/g, ' ').trim();
}

async function get(url) {
  const res = await fetch(url, {
    redirect: 'follow',
    headers: {
      'User-Agent': UA,
      'Accept-Language': 'en-US,en;q=0.9'
    }
  });
  return res;
}

async function discoverEfaList() {
  const wanted = 'european film awards winners: european film';
  const candidates = [];
  for (let page = 1; page <= 6; page++) {
    const url = page === 1
      ? 'https://letterboxd.com/eurofilmacademy/lists/'
      : `https://letterboxd.com/eurofilmacademy/lists/page/${page}/`;
    const res = await get(url);
    const html = await res.text();
    const rx = /<a[^>]+href="([^"]*\/eurofilmacademy\/list\/[^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
    for (const m of html.matchAll(rx)) {
      const text = stripTags(m[2]).toLowerCase();
      if (text.includes(wanted)) {
        const href = new URL(m[1], 'https://letterboxd.com').href;
        candidates.push({page, href, text: stripTags(m[2])});
      }
    }
  }
  const exact = candidates.find(x => x.text.toLowerCase() === wanted)
    ?? candidates.find(x => x.text.toLowerCase().includes(wanted));
  return { candidates, exact: exact ?? null };
}

async function extractIdentifier(url) {
  if (!url.endsWith('/')) url += '/';
  let res;
  let method = 'GET';
  try {
    res = await get(url);
  } catch (e) {
    method = 'HEAD';
    res = await fetch(url, {
      method: 'HEAD',
      redirect: 'follow',
      headers: {'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'}
    });
  }
  return {
    requestedUrl: url,
    finalUrl: res.url,
    status: res.status,
    method,
    identifier: res.headers.get('x-letterboxd-identifier'),
    contentType: res.headers.get('content-type')
  };
}

const result = {
  generatedAt: new Date().toISOString(),
  policy: 'Research only; no catalog IDs are committed unless x-letterboxd-identifier is returned by Letterboxd.',
  efa: {},
  tiff: {}
};

const efaDiscovery = await discoverEfaList();
result.efa.discovery = efaDiscovery;
if (efaDiscovery.exact?.href) {
  result.efa.extraction = await extractIdentifier(efaDiscovery.exact.href);
}

const tiffUrl = 'https://letterboxd.com/alderwar/list/tiff-peoples-choice-award-winners-runners/';
result.tiff.sourceUrl = tiffUrl;
result.tiff.extraction = await extractIdentifier(tiffUrl);

await fs.mkdir('research', {recursive:true});
await fs.writeFile(outPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify(result, null, 2));
