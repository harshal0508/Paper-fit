"""Helper to fetch full method/evaluation text into data/fulltext/<paperId>.txt
Usage: python src/fetch_fulltext.py
Reads data/raw_papers.json, finds papers with openAccessPdf, and extracts text.
"""
import json, os, urllib.request, tempfile
try:
    import pypdf
except ImportError:
    pypdf = None

def download_and_extract_pdf(url):
    if not pypdf:
        print("pypdf not installed. Skipping PDF extraction.")
        return None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            pdf_bytes = r.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
            
        text = ""
        with open(tmp_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        os.remove(tmp_path)
        
        # Heuristic: limit text to Method and Experiment sections to avoid false positives from 'Related Work'
        lower = text.lower()
        start = 0
        for kw in ["methodology", "proposed method", "proposed approach", "experiments", "evaluation", "3. method"]:
            idx = lower.find(f"\n{kw}")
            if idx != -1 and (start == 0 or idx < start):
                start = idx
                
        end = len(text)
        ref_idx = lower.rfind("\nreferences")
        if ref_idx != -1:
            end = ref_idx
            
        if start > 0:
            text = text[start:end]
        else:
            text = text[:end]
            
        return text
    except Exception as e:
        print(f"Failed to extract PDF from {url}: {e}")
        return None

def fetch_fulltext():
    os.makedirs("data/fulltext", exist_ok=True)
    if not os.path.exists("data/raw_papers.json"):
        print("No raw_papers.json found. Run fetch_papers.py first.")
        return
        
    papers = json.load(open("data/raw_papers.json"))
    for p in papers:
        paper_id = p.get("paperId")
        out_path = f"data/fulltext/{paper_id}.txt"
        
        if os.path.exists(out_path):
            continue
            
        oa = p.get("openAccessPdf")
        if not oa or not oa.get("url"):
            continue
            
        url = oa["url"]
        if url.endswith(".pdf"):
            print(f"Fetching PDF for {paper_id}...")
            text = download_and_extract_pdf(url)
            if text:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Saved {out_path}")

if __name__ == "__main__":
    fetch_fulltext()
