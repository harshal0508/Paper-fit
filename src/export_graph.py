"""Export knowledge base to a visual HTML graph using Mermaid.js."""
import json, os

def export_html():
    if not os.path.exists("knowledge_state/knowledge_base.json"):
        print("Run build_kb.py first.")
        return
        
    kb = json.load(open("knowledge_state/knowledge_base.json"))
    
    html = [
        "<!DOCTYPE html>",
        "<html><head><script type='module'>",
        "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';",
        "mermaid.initialize({ startOnLoad: true, maxTextSize: 90000 });",
        "</script></head><body>",
        "<h2>PaperFit Knowledge Graph</h2>",
        "<div class='mermaid'>",
        "graph LR;"
    ]
    
    # Add nodes
    # Using safe IDs (replace - with _)
    for n in kb["nodes"]:
        safe_id = n["id"].replace("-", "_")
        title = n["title"].replace("\"", "'")
        if len(title) > 30: title = title[:27] + "..."
        html.append(f'  {safe_id}["{title}"]:::paper;')
        
    # Gather unique cue and modality nodes from edges
    meta_nodes = set()
    for e in kb["edges"]:
        meta_nodes.add(e["to"])
        
    for m in meta_nodes:
        safe_m = m.replace(":", "_").replace("-", "_")
        html.append(f'  {safe_m}["{m}"]:::meta;')
        
    # Add edges
    for e in kb["edges"]:
        safe_from = e["from"].replace("-", "_")
        safe_to = e["to"].replace(":", "_").replace("-", "_")
        style = "-->" if e["demonstrated"] else "-.->" 
        label = "demonstrated" if e["demonstrated"] else "claimed"
        html.append(f'  {safe_from} {style}|{label}| {safe_to};')
        
    html.append("  classDef paper fill:#f9f,stroke:#333,stroke-width:2px;")
    html.append("  classDef meta fill:#bbf,stroke:#333,stroke-width:2px;")
    html.append("</div></body></html>")
    
    with open("knowledge_state/graph.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print("Exported to knowledge_state/graph.html")

if __name__ == "__main__":
    export_html()
