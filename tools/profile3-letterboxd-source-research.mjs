import fs from 'node:fs/promises';

const UA = 'AIOMetadata/research';
const outPath = 'research/profile3-letterboxd-source-research.json';

function stripTags(s) {
  return s.replace(/<[^>]*>/g, ' ').replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/\s+/g, ' ').trim();
}

async function get(url) {
  return fetch(url, {
    redirect: 'follow',
    headers: {
      'User-Agent': UA,
      'Accept-Language': 'en-US,en;q=0.9'
    }
  });
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

async function validateStremThru(identifier) {
  if (!identifier) return null;
  const url = `https://stremthru.13377001.xyz/v0/meta/letterboxd/lists/${identifier}`;
  const res = await fetch(url, {
    redirect: 'follow',
    headers: {'Accept': 'application/json', 'User-Agent': 'AIOMetadata/1.0'}
  });
  let body = null;
  let parseError = null;
  try {
    body = await res.json();
  } catch (e) {
    parseError = e.message;
  }
  const items = body?.data?.items;
  return {
    url,
    status: res.status,
    ok: res.ok,
    contentType: res.headers.get('content-type'),
    title: body?.data?.title ?? null,
    itemCount: Array.isArray(items) ? items.length : null,
    sampleTitles: Array.isArray(items) ? items.slice(0, 5).map(x => x?.title ?? null) : [],
    topLevelKeys: body && typeof body === 'object' ? Object.keys(body) : [],
    parseError
  };
}

const result = {
  generatedAt: new Date().toISOString(),
  policy: 'Research only; no catalog IDs are committed unless x-letterboxd-identifier is returned by Letterboxd and StremThru runtime succeeds.',
  efa: {},
  tiff: {}
};

const efaDiscovery = await discoverEfaList();
result.efa.discovery = efaDiscovery;
if (efaDiscovery.exact?.href) {
  result.efa.extraction = await extractIdentifier(efaDiscovery.exact.href);
} else {
  const efaCandidateUrls = [
    'https://letterboxd.com/eurofilmacademy/list/european-film-awards-winners-european-film/',
    'https://letterboxd.com/eurofilmacademy/list/european-film-awards-winners-european-film-1/',
    'https://letterboxd.com/eurofilmacademy/list/european-film-awards-winners-european-film-2/',
    'https://letterboxd.com/eurofilmacademy/list/european-film-awards-winners-european-film-3/'
  ];
  result.efa.candidateExtractions = [];
  for (const url of efaCandidateUrls) {
    result.efa.candidateExtractions.push(await extractIdentifier(url));
  }
  result.efa.extraction = result.efa.candidateExtractions.find(x => x.status === 200 && x.identifier) ?? null;
}
result.efa.runtime = await validateStremThru(result.efa.extraction?.identifier);

const tiffUrl = 'https://letterboxd.com/alderwar/list/tiff-peoples-choice-award-winners-runners/';
result.tiff.sourceUrl = tiffUrl;
result.tiff.extraction = await extractIdentifier(tiffUrl);
result.tiff.runtime = await validateStremThru(result.tiff.extraction?.identifier);

await fs.mkdir('research', {recursive:true});
await fs.writeFile(outPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify(result, null, 2));
