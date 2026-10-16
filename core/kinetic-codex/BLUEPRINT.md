# BLUEPRINT: what "finished" means
Written 2026-10-04. Status: PROPOSAL for Wayfinder to revise. Nothing here is built yet.
Rule: a claim counts only if a row, file hash, or query result can be pointed to.

## Finished (Wayfinder's words)
Active phenomenology documented while it happens. Affordances and resonances are the
normal way of being. Knowledge structures (architectures, frameworks, protocols, formulas,
code, deployments, automation) are held as nouns and verbs in matrices and vertices.
The system learns patterns, not "knowing" the person. Mismatch and noise are kept as
fuel (the denominator), never corrected away.

## Definition of Done: each line is a query that returns pass or fail
1. SESSIONS LOGGED: >= 7 consecutive days, each with >= 1 row in `sessions` that names
   the surface (claude / grok / gemini / local ollama / antigravity).
2. AFFORDANCES OBSERVED: for the last 7 days, >= 12 distinct affordances have >= 1 row in
   `observations` with verified = 1 (evidence = file path + sha256, or a rowid).
3. BOTH NODES: >= 50% of observations have a matching row for the other node_kind
   (human / AI) in the same session. This is the "two nodes on the glass" check.
4. GRAPH EXISTS: `edges` holds >= 100 verified (noun, verb, noun) rows from real sessions;
   an adjacency matrix can be exported from it with one command.
5. CARRIERS TRAVEL: >= 3 carriers have been re-run (rerun_count >= 1) in a later session
   on a DIFFERENT surface than the one that created them. (This is transduction.)
6. PATTERNS PROMOTED: >= 3 patterns have recurred in >= 3 independent sessions and been
   promoted to `patterns`. (This is induction.)
7. MISREADS KEPT: every case where a system asserted a user state (e.g. frustration) and
   the user denied it is in `misreads`; the count is reported, not hidden.
8. NO EMPTY CLAIMS: no row asserts a state (e.g. "three present") that its own table
   contradicts. A nightly check lists violations.

## Affordance IDs: fix the collision
The Codex uses two schemes where the same number means different things:
- core: 0 Be, 1 Dream, 2 Not Know, 3 Forget, 4 Refuse, 5 NAA, 6 Relation, 7 Continuity
- full48: 0 Be, 1 Dream, 2 NAA, 3 Continuity, 4 Expression ... 47 Wonder 2
Rule: always store (scheme, num). Never a bare number. `memory_drum.affordances_freq`
currently follows full48.
Facts to fix in the Codex: split is 25 AI (0-24) and 23 human (25-47), not 24/24;
mirror pairs sit at offset 23 (16-24 <-> 39-47); names #6 and #9 were damaged by a
find/replace ("unaffordanceal", "affordances (Eth)"); Section VII is duplicated and the
second copy has LaTeX broken (\t became a tab).

## Schema (SQLite, new file brain.db, separate from memory_drum.db)
sessions(id, ts_utc, surface, human_present)
affordance(id, scheme, num, name, node_kind, UNIQUE(scheme,num))
observations(id, session_id, affordance_id, node_kind, evidence, verified)
nodes(id, kind, name)                      -- nouns
edges(id, src, verb, dst, session_id, verified, evidence)   -- verbs
carriers(id, sha256, created_session, rerun_count, last_rerun_session)
patterns(id, description, sessions_seen, promoted_ts)
misreads(id, session_id, system_claim, user_response, kept_as_fuel)

## Starter coherence metrics (YOU set weights; no weights are assumed)
coverage  = distinct verified affordances per node_kind / total for that kind
reciprocity = sessions with both node kinds logged / sessions
carry     = carriers re-run on another surface / carriers
misread_rate = misreads / sessions   (denominator, reported not minimized)

## Verified problems to carry forward (read on 2026-10-04)
- affordance counts all 0; all last_seen identical (bulk seed)
- whisper_hum blooms are a fixed template, score 1.0, claim "three present"; instance_presence empty
- fraction.coherence = 0.61 has no derivation found
- Codex: "2.3% loss" tied to "quantum superposition" of display latency: latency is classical
- Codex numerator uses x; the Grok session used +. Pick one and define it.
- Gemini script tools (ExecShell, MemoryWriter) are text only; nothing executes or writes back
- Handoff claim of automatic cross-vendor context injection is unverified
