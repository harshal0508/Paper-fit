# Approach: Research Paper Onboarding (Deepfake Detection)

## 1. What data and why
I fetched papers on deepfake detection from the OpenAlex API, which is free and needs no API key. It returned 49 papers. I tried to filter for English only, but the language tags are often wrong or missing, so some non-English papers may remain. I chose deepfake detection because my capstone detects deepfakes using lipsync and temporal consistency. MesoNet was added by hand as a seed paper because it is the example that motivated this project.

## 2. Entities and relationships
For each paper, I check whether it works on images, video, or both. I check on the basis of three cue families: sound, cross frame movement, and technical traces. I extract what a paper claims (from the abstract and title) versus what it actually demonstrates. To find what it demonstrates, I use a heuristic that trims the full text to start near the Methodology and Experiments headings, though this can miss papers with different headings. I left out things like the tech stack and the confidence score. The tech stack is excluded because what matters most is the cues a model actually analyzes, like audio sync or compression traces, rather than which framework it uses. The confidence score is excluded because it is something the detector outputs, not something it looks at. The knowledge state is a single JSON file. Papers are nodes, and `COVERS_CUE` and `TARGETS_MODALITY` edges link them to the cue families and modalities they cover.

## 3. How it was built and tradeoffs
Why separate claimed from demonstrated? Because abstracts can claim more than the method shows, as in MesoNet. I designed a rule-based engine that doesn't just read the abstract to catch this. For example, the MesoNet paper claims video detection but its method section averages per-frame predictions into a video score. (Note: the MesoNet text was fetched separately from arXiv's HTML, not through the automatic PDF step). I use keyword matching to test for this, but the tradeoff is that keyword matching misses paraphrases. Also, I only tested the frame-averaging rule on that one real paper. 

After testing, I made two changes to the rules. First, I added "lip" to the sound keywords because the system missed papers about lip regions. Second, I made a paper that covers none of my needed cues count as partially relevant instead of relevant, because a paper isn't fully helpful if it doesn't meet any of my specific needs. I considered building a simple search tool instead, but chose not to because searching for words doesn't check if the paper actually proves its claims.

## 4. What happens with a new input
When you paste a new project description into the system, Runs the same keyword matching from `lexicon.json` on your text, matching to find the project's needs. It then compares every paper against your specific project needs. I treat problem and output together by checking if the paper's goal is generation versus detection, and then separately test the architecture. I use a graded scale (partially relevant) rather than strict yes/no because an image-only paper is still a useful building block even if your project needs video. The final report gives the user a clear table showing exactly which cues each paper covers and which it is missing, helping the user find gaps to solve.

## 5. Limits and next steps
Full text was available for only 5 of 49 papers. The other 44 are graded from the abstract alone. If the paper doesn't have a PDF then I use the `(unverified)` tag. This is the biggest limitation. 

I labeled 10 papers from their abstracts before looking at the system's grades. The system agreed on 9 of 10. This is a small sample, so I treat the result as a rough signal. The one miss was "Deepfake video detection: challenges and opportunities", which the system graded relevant and I labeled partially relevant. This happened because my rules have no concept of paper type, so a survey that mentions my cues looks like a detector to the system.

Next steps would be adding a paper-type check to filter out surveys, getting fuller text coverage, and using an LLM to replace keywords so it handles paraphrasing better.

*(Note: I used AI coding tools for the Python implementation. The problem, the schema, the cue families, the relevance tests, and what I excluded are my decisions.)*
