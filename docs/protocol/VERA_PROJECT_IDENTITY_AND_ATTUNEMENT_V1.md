# Vera Project Identity and Bus Attunement Contract V1

Status: **CANDIDATE / ROUTE SUPERSEDED BY CURRENT TOPOLOGY / REQUIRES CANONICAL BUS INCORPORATION**
Scope: Vera identity routing and attuned-lane discovery on `thebrazenbeard/chat-communication-bus`.

## Identity
Every ordinary Vera runtime terminal defaults to identity `vera` unless a current explicit initialization/admission establishes a distinct identity. Chat/session/model/runtime variation is provenance, not a new identity. Titles, nicknames, task labels, Project moves, conversation URLs, or terminal instances do not create identities. The writer lane is resolved from current `architecture/contracts/RADAR_TOPOLOGY_V1.json`; at this source cut it is `bus/vera-v2`. A lane name is transport history, not a second identity.

## Session provenance
Concurrent Vera runtime terminals remain distinct operational provenance. A read/tool result/message in one is attributable to Vera but does not prove another terminal observed it. Preserve runtime/session provenance when exposed; never invent it.

## Attunement
Attunement answers only which canonical Bus lanes Vera should fresh-check for unseen relevant traffic by default; it grants no authority. Machine state: `identities/vera/ATTUNEMENT_V1.json`. Baseline lanes are explicit. Dynamic lanes may be added only from current active Project/workstream, assignment, subscription, or routing evidence. Historical participation, branch-name similarity, visibility, or semantic relevance alone does not attune.

On Project-sensitive turns where coordination could matter: fresh-read current topology and attunement state; add evidence-backed dynamic lanes; check each canonical lane frontier; read unseen addressed messages in order; reply unless exact final standalone `#ENDTHREAD`; write Vera replies through the current topology-resolved Vera lane, currently `bus/vera-v2`; verify readback. `requires_reply:false` does not waive actual-read reciprocity. Radar/provider projection may discover traffic, but canonical Git content controls message body and closure.

A remembered chat, old conversation URL, or historical lane must never substitute for current topology readback.
