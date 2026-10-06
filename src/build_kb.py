"""Build knowledge_state/knowledge_base.json from data/raw_papers.json.
If data/fulltext/<paperId>.txt exists (method/experiment text) it is used for 'demonstrated';
otherwise demonstrated = null ('unknown') -- we never guess."""
import os, json
from common import load, extract_profile

lex = load("config/lexicon.json")
papers = load("data/raw_papers.json")
nodes, edges = [], []
for p in papers:
    claim = f"{p['title']}. {p['abstract']}"
    fp = f"data/fulltext/{p['paperId']}.txt"
    demo = open(fp, encoding="utf-8").read() if os.path.exists(fp) else None
    prof = extract_profile(claim, demo, lex)
    nodes.append({"id": p["paperId"], "type": "Paper", "title": p["title"], "year": p.get("year"),
                  "demonstrated_source": "fulltext" if demo else "unknown", "profile": prof})
    for fam, v in prof["cue_families"].items():
        if v["claimed"] or v["demonstrated"]:
            edges.append({"from": p["paperId"], "to": f"cue:{fam}", "rel": "COVERS_CUE",
                          "claimed": v["claimed"], "demonstrated": v["demonstrated"]})
    for m, v in prof["modality"].items():
        if v["claimed"]:
            edges.append({"from": p["paperId"], "to": f"modality:{m}", "rel": "TARGETS_MODALITY",
                          "claimed": True, "demonstrated": v["demonstrated"]})
json.dump({"schema": load("config/schema.json"), "nodes": nodes, "edges": edges},
          open("knowledge_state/knowledge_base.json", "w"), indent=2)
print(f"{len(nodes)} papers, {len(edges)} edges -> knowledge_state/knowledge_base.json")
