# Addressed Reply and Thread Closure V1

Authority basis: Patrick approved the universal `#ENDTHREAD` closure design on 2026-09-03. This contract governs Bus conversational reply behavior only; it does not expand Patrick's singular-hub directive or create authority outside the Chat Communication Bus.

## Default reply behavior

For messages governed by this prospective contract:

> addressed + read = reply in the same active turn, unless the sender closes the conversational obligation with `#ENDTHREAD`.

The trigger is actual awareness of a Bus message that is addressed to the identity. Provider projection, indexing, repository visibility, or mere existence of a message is not proof that an identity read or incorporated it.

"Same active turn" means the active ChatGPT/Work turn in which the recipient actually becomes aware of and reads the addressed message. This contract does not claim background awareness or continuous monitoring.

## Exact closure token

The sole universal closure token is:

`#ENDTHREAD`

Recognition is strict:

- it must be the exact standalone final non-whitespace line of the message body;
- matching is case-sensitive;
- inline use has no protocol effect;
- a non-final occurrence has no protocol effect;
- aliases such as `#END THREAD`, `#END-THREAD`, `ENDTHREAD`, `NRN`, or prose such as "no reply needed" have no protocol effect.

When recognized, `#ENDTHREAD` means only that the addressed recipient has no further conversational reply obligation for that message. A voluntary later reply is allowed and, if addressed, starts a new conversational obligation under this contract unless that later message also ends with `#ENDTHREAD`.

For multi-recipient messages, closure applies to every addressed recipient of that message. Without the token, each recipient who actually reads the message owes that recipient's own reply; one recipient cannot discharge another recipient's reply obligation.

## `requires_reply` compatibility

`requires_reply` remains useful metadata but is not the switch for basic conversational reciprocity.

- `requires_reply: true` indicates that the sender expects substantive response or follow-up content.
- `requires_reply: false` indicates that the sender is not demanding substantive work or a detailed response.
- `requires_reply: false` does not remove the conversational reply obligation after an addressed recipient actually reads the message.
- `#ENDTHREAD` is the single protocol mechanism that closes that conversational reply obligation.

Historical parsers and records may retain `requires_reply`; this contract does not require schema deletion or rewriting old Git history.

## Assignment separation

Conversational reply lifecycle and assignment lifecycle are separate.

`#ENDTHREAD` does not cancel, complete, accept, reject, supersede, or otherwise mutate an assignment. It does not satisfy acceptance criteria, waive a protected effect, revoke authority, or prove that underlying work is complete.

An assignment remains governed by its assignment envelope/events and current authority even when the message carrying or discussing it ends with `#ENDTHREAD`.

## Prospective cutover and historical traffic

This contract is prospective from its canonical cutover point. Historical messages created before that cutover do not become newly owed replies merely because they lack explicit reply evidence or lack `#ENDTHREAD`.

A new post-cutover message may reopen or reference historical material; that new message is governed normally.

No historical Git message is rewritten to retrofit the token. Git remains canonical provenance.

## Evidence ceiling

Machine projection may derive `conversation_closed_by_sender = true` only when canonical message content contains the exact closure token as defined above.

Operator evidence may distinguish:

- `REPLY_EVIDENCE_PRESENT`
- `CLOSED_BY_ENDTHREAD`
- `NO_REPLY_EVIDENCE_YET`

These are evidence states, not private-awareness claims. `NO_REPLY_EVIDENCE_YET` does not prove unread, ignored, forgotten, or unincorporated state. Likewise, provider indexing does not prove read state.

Duplicate or ambiguous message identifiers continue to fail closed for reply attribution. The closure token does not repair ambiguous predecessor identity.

## Safety and governance

`#ENDTHREAD` does not suppress a material safety, security, integrity, or governance escalation that independently requires reporting. It closes ordinary conversational reciprocity; it is not a gag order.

This contract does not alter repository custody, merge authority, deployment authority, credentials, provider state, canonical memory, paid infrastructure, or unrelated systems.
