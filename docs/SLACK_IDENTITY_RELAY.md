# Slack Identity Relay v1

Status: **FUTURE_FRONTIER / NOT CURRENT DURABLE COORDINATION / NOT DEPLOYMENT AUTHORITY**

This historical design slice describes how Chat Bus could expose stable logical endpoint identities through Slack without creating fake human Slack accounts. Slack is not the current system of record or an alternate worker coordination bus. Reconnection, app configuration, credentials, provider setup, and deployment require separate explicit authority.

## Addressing

A single Slack relay app receives explicit logical addressing:

- `@Hephaestus review the Project routing model`
- `Masa: inspect the Supabase idempotency path`
- `<@RELAY_BOT> Mune: inspect this GitHub effect`

Unknown or missing logical recipients fail closed. Endpoint aliases are case-insensitive and collision-rejected.

## Outbound identity

The transport may use Slack `chat:write.customize` to render a logical endpoint display name/avatar, but every message is visibly prefixed with a `Chat Bus relay` signpost. Chat Bus endpoint identity remains distinct from Slack human identity.

Slack message metadata contains only routing identifiers and the deterministic envelope digest. Message content is intentionally excluded from metadata because Slack documents metadata as visible to workspace members/apps with access.

## Events and scopes

The intended Slack app transport uses:

- `chat:write` to send messages.
- `chat:write.customize` only when customized relay display names are enabled.
- `app_mentions:read` plus the `app_mention` event for channel addressing.
- `im:history` plus `message.im` for direct messages to the relay app.

HTTP Events API or Socket Mode can carry inbound events. Socket Mode avoids requiring a public request URL.

## Idempotency

`RelayStore` binds each `operation_id` to one exact envelope SHA-256 and message ID. Identical replay returns the existing claim. Divergent reuse fails with `OPERATION_ID_CONFLICT`. Delivery readback is bound to the exact envelope digest and Slack message timestamp; conflicting receipt reuse fails closed.

## Credential boundary

This code does not store or request Slack tokens. Installing/configuring the Slack app and supplying bot/app credentials is a separate user-controlled deployment step.
