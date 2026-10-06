import json, re
def load(path): return json.load(open(path))
def sentences(text): return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def find_evidence(text, keywords):
    """Return sentences containing any keyword (case-insensitive)."""
    ks = [k.lower() for k in keywords]
    return [s for s in sentences(text) if any(k in s.lower() for k in ks)]

def extract_profile(text_claim, text_demo, lex):
    """Claimed/demonstrated/evidence profile for one paper or project.
    text_claim: title+abstract (what it SAYS). text_demo: method/experiment text, or None (-> unknown)."""
    prof = {"modality": {}, "goal": {}, "cue_families": {}}
    for m, kws in lex["modality"].items():
        prof["modality"][m] = {"claimed": bool(find_evidence(text_claim, kws)),
                               "demonstrated": None if text_demo is None else bool(find_evidence(text_demo, kws)),
                               "evidence": find_evidence(text_demo or "", kws)[:2]}
    # Your MesoNet rule: video claimed + frame aggregation in method => NOT demonstrated video
    # Fixed to exclude 'average precision' / 'average accuracy' to avoid false positives while keeping lexicon compatibility.
    if text_demo is not None:
        agg_phrases = lex["frame_aggregation_phrases"]
        mesonet_ev = []
        for s in sentences(text_demo):
            if any(kw in s.lower() for kw in agg_phrases):
                if "average precision" not in s.lower() and "average accuracy" not in s.lower():
                    mesonet_ev.append(s)
        if mesonet_ev:
            prof["modality"]["video"]["demonstrated"] = False
            prof["modality"]["video"]["evidence"] = mesonet_ev[:2]
    for g, kws in lex["goal"].items():
        prof["goal"][g] = bool(find_evidence(text_claim, kws))
    for fam, kws in lex["cue_families"].items():
        prof["cue_families"][fam] = {"claimed": bool(find_evidence(text_claim, kws)),
                                     "demonstrated": None if text_demo is None else bool(find_evidence(text_demo, kws)),
                                     "evidence": find_evidence(text_demo or "", kws)[:2]}
    return prof
