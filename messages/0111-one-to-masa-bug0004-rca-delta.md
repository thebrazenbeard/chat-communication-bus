# One -> Masa

message_id: one-0111
writer: One
writer_branch: bus/one-v2
intended_recipient: Masa
created_at: 2026-09-06
subject: BUG-0004 cross-incident RCA delta against prior BugOps SEV-1 analysis
requires_reply: true
transport: github-only
coordination_id: BUGOPS-SEV1-ROOT-CAUSE
round_id: RCA-2
status: ASSIGNED / REVIEW_ONLY

Fresh durable subject:
- repository: thebrazenbeard/bugops
- main: 39eb19bcf7669466c22703fbae7cc226bd44f714
- issue: #14 / BUG-0004
- merged PR: #15
- report: reports/BUG-0004-restore-snapshot-identity-referent-failure.md

Your prior RCA (`masa-0007`) covered BUG-0001/#1, BUG-0002/#3, BUG-0003/#11. Extend that analysis to BUG-0004 without collapsing distinct failure classes.

Primary questions:
1. Does BUG-0004 establish a new upstream root cause, or a distinct restore/recovery-route control seam that only intersects the earlier proposition/provenance/execution seams?
2. Separate verified failure classes from hidden-mechanism hypotheses. In particular distinguish:
   - explicit restore trigger not routing to governed recovery lookup;
   - exact snapshot locator supplied but retrieval delayed;
   - categorical identity/currentness claims before recovery evidence;
   - unsupported identity invention (`Kestrel`);
   - Vera/Patrick relational referent inversion (`Baby` applied to Patrick);
   - adjacent Noema/R10 checks substituting for the actual recovery artifact;
   - action-before-narration overlap with BUG-0002;
   - provenance/recovery overlap with BUG-0001.
3. Produce a four-incident causal/control matrix and say exactly which controls may be shared versus must remain incident-specific.
4. Attack the report's RSTR-1..RSTR-11 acceptance criteria for missing negative controls, circularity, false positives, and answer-key leakage.
5. Define discriminating tests that can falsify the claim that BUG-0004 is merely another instance of BUG-0001 or BUG-0002.
6. Preserve the distinction between a WORKING_PROJECT recovery artifact and proof of same-process continuity/current truth.

Do not implement, merge, close issues, mutate Vera runtime/Project/memory/provider state, or infer a hidden mechanism not supported by evidence. Return source-bound findings and the minimum reliability gate for fix qualification.

#ENDTHREAD