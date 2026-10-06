"""Give the system a NEW project description; get a fit & gap report.
Usage: 
  python src/analyze.py "our project detects deepfakes..."
  cat project.txt | python src/analyze.py -
"""
import sys, json, argparse, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from common import load, extract_profile

lex = load("config/lexicon.json")
kb = load("knowledge_state/knowledge_base.json")

def wanted(profile):
    return {"modality": [m for m, v in profile["modality"].items() if v["claimed"]],
            "cues": [f for f, v in profile["cue_families"].items() if v["claimed"]]}

def grade(paper, need, covers_cues):
    """YOUR three tests: problem, architecture, output. Edit this function to change the rule."""
    pr = paper["profile"]
    if pr["goal"]["generation"] and not pr["goal"]["detection"]:
        return "irrelevant", "Problem/output test: paper generates media instead of detecting it."
    if not pr["goal"]["detection"]:
        return "irrelevant", "Problem test: no detection goal found."
    if "video" in need["modality"]:
        v = pr["modality"]["video"]
        if v["demonstrated"] is False:
            return "partially_relevant", "Architecture test: claims video but evidence shows frame-level only (image classifier + aggregation)."
        if v["demonstrated"] is None and not v["claimed"]:
            return "partially_relevant", "Architecture test: no video claim; likely image-only building block."
    if not covers_cues:
        return "partially_relevant", "Passes architecture, but covers ZERO of your required cues."
        
    return "relevant", "Passes problem, architecture and output tests."

def report(text):
    need = wanted(extract_profile(text, text, lex))
    out = {"project_needs": need, "papers": []}
    for n in kb["nodes"]:
        covered = [c for c in need["cues"] if n["profile"]["cue_families"][c]["claimed"]]
        g, why = grade(n, need, covered)
        missing = [c for c in need["cues"] if c not in covered]
        
        # Collect evidence sentences for covered cues
        evidence_sentences = {}
        for c in covered:
            ev = n["profile"]["cue_families"][c]["evidence"]
            if ev:
                evidence_sentences[c] = ev
                
        out["papers"].append({
            "title": n["title"], 
            "year": n["year"], 
            "grade": g, 
            "reason": why,
            "covers_cues": covered, 
            "missing_cues": missing,
            "demonstrated_source": n["demonstrated_source"],
            "evidence": evidence_sentences,
            "video_evidence": n["profile"]["modality"]["video"]["evidence"]
        })
    order = {"relevant": 0, "partially_relevant": 1, "irrelevant": 2}
    out["papers"].sort(key=lambda p: (order[p["grade"]], len(p["missing_cues"])))
    return out

def print_table(rep):
    needs = rep["project_needs"]
    print("\n" + "="*80)
    print("PROJECT NEEDS:")
    print(f"Modality: {', '.join(needs['modality']) if needs['modality'] else 'None specified'}")
    print(f"Cues:     {', '.join(needs['cues']) if needs['cues'] else 'None specified'}")
    print("="*80 + "\n")
    
    print(f"{'TITLE (YEAR)':<50} | {'GRADE':<25} | {'COVERED / MISSING CUES'}")
    print("-" * 110)
    
    for p in rep["papers"]:
        title_disp = f"{p['title'][:40]}... ({p['year']})" if len(p['title']) > 40 else f"{p['title']} ({p['year']})"
        cues_disp = f"[COVERED] {','.join(p['covers_cues'])} [MISSING] {','.join(p['missing_cues'])}"
        grade_disp = f"{p['grade']} (unverified)" if p['demonstrated_source'] == "unknown" else p['grade']
        print(f"{title_disp:<50} | {grade_disp:<25} | {cues_disp}")
        print(f"  |- Reason: {p['reason']}")
        if p['grade'].startswith('partially_relevant') and p.get('video_evidence'):
            print(f"  |- Frame-Aggregation Evidence:")
            for ev in p['video_evidence']:
                print(f"       \"{ev}\"")
                
        if p['evidence']:
            print(f"  |- Cue Evidence:")
            for cue, ev_list in p['evidence'].items():
                for ev in ev_list:
                    print(f"       [{cue}] \"{ev}\"")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a project description against the knowledge base.")
    parser.add_argument("input", help="Text description, file path, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of table")
    args = parser.parse_args()
    
    if args.input == "-":
        text = sys.stdin.read()
    elif os.path.isfile(args.input):
        with open(args.input, "r") as f:
            text = f.read()
    else:
        text = args.input
        
    rep = report(text)
    
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print_table(rep)
