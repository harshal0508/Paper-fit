"""Validate the grading engine against hand-labeled papers.
Usage: python src/validate.py <labeled_data.json>
Example JSON format:
[
  {"paperId": "1234", "expected_grade": "relevant"},
  {"paperId": "5678", "expected_grade": "irrelevant"}
]
"""
import sys, json, os
from common import load
from analyze import grade, wanted, extract_profile

def validate(labeled_path, project_description):
    lex = load("config/lexicon.json")
    if not os.path.exists("knowledge_state/knowledge_base.json"):
        print("Knowledge base not found. Run build_kb.py first.")
        return
    
    kb = load("knowledge_state/knowledge_base.json")
    labeled = load(labeled_path)
    
    # Create quick lookup from KB
    nodes = {n["id"]: n for n in kb["nodes"]}
    
    need = wanted(extract_profile(project_description, project_description, lex))
    
    correct = 0
    total = len(labeled)
    
    print(f"{'Paper ID':<45} | {'Expected':<20} | {'Predicted':<20} | {'Match'}")
    print("-" * 100)
    
    for item in labeled:
        pid = item["paperId"]
        expected = item["expected_grade"]
        
        if pid not in nodes:
            print(f"{pid:<45} | {expected:<20} | {'NOT IN KB':<20} | FAIL")
            continue
            
        n = nodes[pid]
        covered = [c for c in need["cues"] if n["profile"]["cue_families"][c]["claimed"]]
        predicted, reason = grade(n, need, covered)
        
        match = (expected == predicted)
        if match:
            correct += 1
            
        print(f"{pid:<45} | {expected:<20} | {predicted:<20} | {'PASS' if match else 'FAIL'}")
        if not match:
            print(f"  Reasoning: {reason}")
            
    acc = (correct / total) * 100 if total > 0 else 0
    print("-" * 100)
    print(f"Accuracy: {correct}/{total} ({acc:.1f}%)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/validate.py data/labeled_papers.json")
        sys.exit(1)
        
    test_desc = "our project detects deepfakes in videos and images using lipsync, analyzing face consistency across frames, and checking for lighting and compression artefacts."
    validate(sys.argv[1], test_desc)
