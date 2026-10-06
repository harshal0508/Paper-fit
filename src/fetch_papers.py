"""Fetch candidate papers from Semantic Scholar into data/raw_papers.json.
Usage: python src/fetch_papers.py "deepfake video detection" --limit 60
Optional env var: S2_API_KEY (higher rate limits)."""
import argparse, json, os, time, urllib.parse, urllib.request
from urllib.error import HTTPError, URLError

FIELDS = "paperId,title,abstract,year,externalIds,citationCount,tldr,openAccessPdf"
URL = "https://api.semanticscholar.org/graph/v1/paper/search?"

def fetch(query, limit):
    papers, offset = [], 0
    headers = {"x-api-key": os.environ["S2_API_KEY"]} if os.getenv("S2_API_KEY") else {}
    
    while len(papers) < limit:
        q = urllib.parse.urlencode({"query": query, "limit": min(50, limit - len(papers)),
                                    "offset": offset, "fields": FIELDS})
        req = urllib.request.Request(URL + q, headers=headers)
        
        retries = 5
        data = None
        backoff = 2
        while retries > 0:
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.load(r)
                break
            except HTTPError as e:
                if e.code == 429:
                    print(f"Rate limited. Sleeping for {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                    retries -= 1
                else:
                    print(f"HTTPError: {e.code}")
                    break
            except URLError as e:
                print(f"URLError: {e.reason}")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
        if not data:
            break
            
        batch = data.get("data", [])
        if not batch:
            break
            
        # Filter papers to ensure they have an abstract and a title before proceeding
        valid_papers = [p for p in batch if p.get("abstract") and p.get("title")]
        papers += valid_papers
        offset += len(batch)
        print(f"Fetched {len(papers)}/{limit} papers...")
        time.sleep(1.5)  # be polite
        
    return papers[:limit]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=60)
    a = ap.parse_args()
    out = fetch(a.query, a.limit)
    os.makedirs("data", exist_ok=True)
    json.dump(out, open("data/raw_papers.json", "w"), indent=2)
    print(f"Saved {len(out)} papers to data/raw_papers.json")
