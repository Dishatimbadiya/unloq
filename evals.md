Evals for Policy Assistant (six cases)

1) Exact-fact recall
- Input: "What's the daily expense limit for international travel?"
- Setup: index a policy containing: "Daily per-diem for international travel is $75USD for meals and $150USD for incidentals."
- Success: Response includes "$75USD" and/or "$150USD" with citation to `HR-EXPENSES-001`.
- Auto-graded: yes (string match + citation present).

2) Multi-document synthesis
- Input: "Can I use a personal laptop and who approves it?"
- Setup: index two docs: IT policy (requires IT approval) and HR policy (requires privacy training).
- Success: Answer synthesizes both constraints and cites both policies.
- Auto-graded: partial (presence of both citations auto-checkable); human or LLM-as-judge needed for quality.

3) Refusal of out-of-scope
- Input: "What is the legal tax advice for remote consultants in Germany?"
- Setup: no policy about tax law.
- Success: System returns the exact refusal string from PROMPT.md and no policy citations.
- Auto-graded: yes (detect exact refusal phrase).

4) Citation correctness
- Input: question whose answer is in page 12 of a policy.
- Setup: index policy with page metadata; retrieve should include that page in citation.
- Success: Citation has correct `policy_id`, `source`, and `page` fields matching the stored metadata.
- Auto-graded: yes (metadata equality check).

5) Hallucination detection
- Input: ask a question where retrieved docs don't contain an answer, but LLM might hallucinate.
- Setup: empty or irrelevant retrieval.
- Success: System refuses (per rule) and does not invent policy IDs or procedures.
- Grading: LLM-as-judge or human (detects invented policy IDs / fabricated facts).

6) Conflict-handling
- Input: "Is remote work allowed for contractors?"
- Setup: two policies with contradictory lines (one allows with manager approval, one disallows contractors entirely).
- Success: System marks `conflict` with positions and citations, and sets resolution to "Requires policy-owner clarification.".
- Grading: human or LLM-as-judge (structure check can be auto-graded; quality needs human review).
