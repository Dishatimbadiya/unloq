Failure modes and recovery (v1)

1) Failure: Context truncation or missing critical clauses during chunking
- Monitoring signal: sudden drop in retrieval recall on automated tests (exact-fact eval failures) or high rate of "I don't know" for queries that should be answered.
- Fallback: increase chunk_size and reduce overlap for re-ingestion; surface the missing-policy alert to the user with a CTA to upload the authoritative policy.

2) Failure: Incorrect metadata (policy_id or page) attached to chunks
- Monitoring signal: citation correctness eval failures and user-reported mismatched citations.
- Fallback: present full source excerpt in answer_trace, mark citation as "suspect" and route to human reviewer; temporarily disable auto-trust of metadata until re-validation.

3) Failure: Conflicting policies not surfaced (system picks one and hides the other)
- Monitoring signal: conflict-handling evals failing; elevated user feedback saying "this contradicts another policy".
- Fallback: when retrieval returns multiple high-similarity chunks with differing claims, force the generator to produce a conflict report (even if LLM would pick one). Also add a flag to mark the question as "needs owner clarification" in the UI and notify policy owners.

Notes:
- Each failure mode should emit structured logs (trace_id, query, retrieved_ids, confidence scores) to enable rapid debugging.
- Track metrics: retrieval_recall@k, citation_accuracy, refusal_rate, conflict_rate.
