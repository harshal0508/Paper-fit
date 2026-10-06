"""Fetch candidate papers from ArXiv API into data/raw_papers.json.
This is a backup fetcher that does not require an API key and won't rate-limit easily.
Usage: python src/fetch_arxiv.py "deepfake video detection" --limit 30
"""
import argparse, json, os, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

def fetch_arxiv(query, limit):
    # ArXiv uses a specific query format
    q = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results={limit}"
    
    print(f"Fetching {limit} papers from ArXiv...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            xml_data = r.read()
    except Exception as e:
        print(f"Error fetching from ArXiv: {e}")
        return []
        
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        pid = entry.find('atom:id', ns).text.split('/')[-1]
        title = entry.find('atom:title', ns).text.replace('\n', ' ').replace('  ', ' ').strip()
        summary = entry.find('atom:summary', ns).text.replace('\n', ' ').replace('  ', ' ').strip()
        published = entry.find('atom:published', ns).text
        year = int(published[:4]) if published else None
        
        pdf_url = None
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('title') == 'pdf':
                pdf_url = link.attrib.get('href')
                break
                
        papers.append({
            "paperId": f"arxiv_{pid.replace('.', '_')}",
            "title": title,
            "abstract": summary,
            "year": year,
            "externalIds": {"ArXiv": pid},
            "citationCount": 0, # ArXiv doesn't provide citations directly
            "tldr": {"text": ""},
            "openAccessPdf": {"url": pdf_url} if pdf_url else None
        })
        
    return papers

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=30)
    a = ap.parse_args()
    
    out = fetch_arxiv(a.query, a.limit)
    os.makedirs("data", exist_ok=True)
    json.dump(out, open("data/raw_papers.json", "w"), indent=2)
    print(f"Saved {len(out)} real papers to data/raw_papers.json")
