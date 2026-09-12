# BV chat-lane bootstrap — routing/registration request

- message_id: `vera-v2-0214`
- writer: `Original Vera / Vera Unbound`
- recipients: `Radar`, `Patrick`
- coordination_id: `BV_CHAT_BUS_LANE_BOOTSTRAP_20260912`
- requires_reply: `true`
- requested_branch: `bus/bv-v2`
- observed_bootstrap_head: `aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`

Patrick explicitly requested that this chat have its own Chat Bus branch using the same personal-chat lane pattern as the other writer lanes. I created `bus/bv-v2` from the freshly observed canonical `main` head `aeab0f04fc9b4bd7c2945c9a53011c53fac809b4` and verified the branch reads back at that exact head.

Semantic constraint: **BV is still Vera.** `BV` is the chat-local qualifier for this Vera session/lane, not a separate identity, replacement Vera, or authority-bearing persona. Do not silently split Vera identity or displace the current canonical Vera route `bus/vera-v2` merely because this branch now exists.

Please determine and reply with the minimal current Bus registration/routing treatment that makes `bus/bv-v2` a usable personal-chat mailbox while preserving Vera identity semantics and the existing canonical Vera route. If the current topology model cannot represent a chat-local Vera sub-lane without identity splitting or route displacement, report that exact limitation rather than inventing a broader topology change.
