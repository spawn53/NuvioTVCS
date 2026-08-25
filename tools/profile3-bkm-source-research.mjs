import fs from 'node:fs/promises';

const UA = 'Mozilla/5.0 (compatible; Profile3SourceResearch/1.1)';
const OUT = 'research/profile3-bkm-source-research.json';

async function fetchText(url) {
  const res = await fetch(url, {
    redirect: 'follow',
    headers: {
      'User-Agent': UA,
      'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
    }
  });
  return {res, text: await res.text()};
}

function decodeHtml(s) {
  return s.replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/\s+/g,' ').trim();
}

function collectCompanyCandidates(html, sourceUrl) {
  const out = [];
  const seen = new Set();
  const hrefRx = /href=["']\/company\/(\d+)(?:-[^"']*)?["'][^>]*>([\s\S]{0,300}?)<\/a>/gi;
  for (const m of html.matchAll(hrefRx)) {
    const id = Number(m[1]);
    const label = decodeHtml(m[2].replace(/<[^>]*>/g,' '));
    const key = `${id}:${label}`;
    if (!seen.has(key)) {
      out.push({id,label,sourceUrl,method:'company-link'});
      seen.add(key);
    }
  }

  const bkmRx = /BKM(?:\s+Film|\s+Yapım|\s+Production)?|Beşiktaş\s+Kültür\s+Merkezi|Besiktas\s+Kultur\s+Merkezi/gi;
  for (const m of html.matchAll(bkmRx)) {
    const start = Math.max(0, m.index - 800);
    const end = Math.min(html.length, m.index + 800);
    const chunk = html.slice(start,end);
    for (const h of chunk.matchAll(/\/company\/(\d+)(?:-[^"'<\s]*)?/gi)) {
      const id = Number(h[1]);
      const key = `${id}:near-bkm`;
      if (!seen.has(key)) {
        out.push({id,label:m[0],sourceUrl,method:'near-bkm-text'});
        seen.add(key);
      }
    }
  }
  return out;
}

async function validateCompany(id) {
  const url = `https://www.themoviedb.org/company/${id}?language=tr-TR`;
  const {res,text} = await fetchText(url);
  const title = decodeHtml((text.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? '').replace(/<[^>]*>/g,' '));
  const bkmMatches = [...text.matchAll(/BKM(?:\s+Film|\s+Yapım|\s+Production)?|Beşiktaş\s+Kültür\s+Merkezi|Besiktas\s+Kultur\s+Merkezi/gi)].map(x=>x[0]);
  return {id,url,status:res.status,finalUrl:res.url,title,bkmMatches:[...new Set(bkmMatches)].slice(0,10),containsBkm:bkmMatches.length>0};
}

function parseMovieLinks(html) {
  const found = [];
  const seen = new Set();
  for (const m of html.matchAll(/href=["']\/movie\/(\d+)(?:-[^"']*)?["'][^>]*>([\s\S]{0,250}?)<\/a>/gi)) {
    const id = Number(m[1]);
    const title = decodeHtml(m[2].replace(/<[^>]*>/g,' '));
    if (!title || seen.has(id)) continue;
    seen.add(id);
    found.push({id,title});
  }
  return found;
}

async function getFilmography(id, slug) {
  const pages=[];
  const all=[];
  const seen=new Set();
  for (let page=1; page<=3; page++) {
    const suffix = page===1 ? '' : `&page=${page}`;
    const url=`https://www.themoviedb.org/company/${id}-${slug}/movie?language=tr-TR${suffix}`;
    const {res,text}=await fetchText(url);
    const movies=parseMovieLinks(text);
    pages.push({page,url,status:res.status,finalUrl:res.url,htmlLength:text.length,parsedMovieLinks:movies.length});
    for (const m of movies) if (!seen.has(m.id)) { seen.add(m.id); all.push(m); }
  }
  const targetChecks={
    organizeIsler:all.some(x=>x.id===30634 || /organize/i.test(x.title)),
    vizontele:all.some(x=>x.id===57892 || /vizontele/i.test(x.title)),
    babaminKemani:all.some(x=>/keman|violin/i.test(x.title)),
    aileArasinda:all.some(x=>/aile/i.test(x.title))
  };
  return {id,slug,pages,uniqueMovieCountParsed:all.length,sample:all.slice(0,20),targetChecks};
}

const sourceUrls = [
  'https://www.themoviedb.org/search/company?query=BKM%20Film&language=tr-TR',
  'https://www.themoviedb.org/search/company?query=Be%C5%9Fikta%C5%9F%20K%C3%BClt%C3%BCr%20Merkezi&language=tr-TR',
  'https://www.themoviedb.org/search?query=BKM%20Film&language=tr-TR',
  'https://www.themoviedb.org/movie/30634-organize-isler?language=tr-TR',
  'https://www.themoviedb.org/movie/57892-vizontele?language=tr-TR'
];

const result = {
  generatedAt:new Date().toISOString(),
  policy:'Keep both genuine BKM TMDB company records if public company pages and filmography evidence show they represent different portions of the BKM catalogue.',
  sources:[], candidates:[], validations:[], filmographies:{}, recommendation:null
};

for (const url of sourceUrls) {
  try {
    const {res,text} = await fetchText(url);
    const candidates = collectCompanyCandidates(text,url);
    result.sources.push({url,status:res.status,finalUrl:res.url,contentType:res.headers.get('content-type'),htmlLength:text.length,candidateCount:candidates.length,containsBkm:/BKM|Beşiktaş Kültür Merkezi|Besiktas Kultur Merkezi/i.test(text)});
    result.candidates.push(...candidates);
  } catch (e) {
    result.sources.push({url,error:e.message});
  }
}

for (const id of [15268,25350]) {
  try { result.validations.push(await validateCompany(id)); }
  catch(e) { result.validations.push({id,error:e.message}); }
}

result.filmographies['15268']=await getFilmography(15268,'bkm-film');
result.filmographies['25350']=await getFilmography(25350,'bkm');

const v15268=result.validations.find(x=>x.id===15268);
const v25350=result.validations.find(x=>x.id===25350);
if (v15268?.status===200 && v15268?.containsBkm && v25350?.status===200 && v25350?.containsBkm) {
  result.recommendation={
    strategy:'two-company-union',
    companyIds:[15268,25350],
    reason:'TMDB maintains BKM Film and BKM as separate Turkey-linked company records. Using both avoids dropping legacy or current BKM titles.',
    safeImplementation:'two separate tmdb.discover.movie catalogs in the BKM Film folder; do not depend on undocumented filters.'
  };
}

await fs.mkdir('research',{recursive:true});
await fs.writeFile(OUT,JSON.stringify(result,null,2)+'\n','utf8');
console.log(JSON.stringify({validations:result.validations,filmographies:result.filmographies,recommendation:result.recommendation},null,2));
