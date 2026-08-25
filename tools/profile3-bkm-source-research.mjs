import fs from 'node:fs/promises';

const UA = 'Mozilla/5.0 (compatible; Profile3SourceResearch/1.0)';
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
    const jsonPatterns = [
      /"id"\s*:\s*(\d+)[\s\S]{0,500}?"name"\s*:\s*"([^"]*BKM[^"]*)"/gi,
      /"name"\s*:\s*"([^"]*BKM[^"]*)"[\s\S]{0,500}?"id"\s*:\s*(\d+)/gi
    ];
    for (let pi=0; pi<jsonPatterns.length; pi++) {
      for (const j of chunk.matchAll(jsonPatterns[pi])) {
        const id = Number(pi===0 ? j[1] : j[2]);
        const label = pi===0 ? j[2] : j[1];
        const key = `${id}:${label}`;
        if (!seen.has(key)) {
          out.push({id,label,sourceUrl,method:'embedded-json'});
          seen.add(key);
        }
      }
    }
  }
  return out;
}

async function validateCompany(id) {
  const url = `https://www.themoviedb.org/company/${id}?language=tr-TR`;
  const {res,text} = await fetchText(url);
  const title = (text.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? '').replace(/<[^>]*>/g,' ').trim();
  const bkmMatches = [...text.matchAll(/BKM(?:\s+Film|\s+Yapım|\s+Production)?|Beşiktaş\s+Kültür\s+Merkezi|Besiktas\s+Kultur\s+Merkezi/gi)].map(x=>x[0]);
  return {id,url,status:res.status,finalUrl:res.url,title,bkmMatches:[...new Set(bkmMatches)].slice(0,10),containsBkm:bkmMatches.length>0};
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
  policy:'Accept only a numeric TMDB company ID found on public TMDB HTML near BKM identity and validated by a public TMDB company page.',
  sources:[], candidates:[], validations:[], resolved:null
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

const uniqueIds=[...new Set(result.candidates.map(x=>x.id).filter(Number.isFinite))];
for (const id of uniqueIds) {
  try { result.validations.push(await validateCompany(id)); }
  catch(e) { result.validations.push({id,error:e.message}); }
}

const strong = result.validations.filter(v=>v.status===200 && v.containsBkm);
if (strong.length===1) {
  const id=strong[0].id;
  result.resolved={id,evidence:result.candidates.filter(c=>c.id===id),validation:strong[0]};
} else if (strong.length>1) {
  result.ambiguous=strong;
}

await fs.mkdir('research',{recursive:true});
await fs.writeFile(OUT,JSON.stringify(result,null,2)+'\n','utf8');
console.log(JSON.stringify(result,null,2));
