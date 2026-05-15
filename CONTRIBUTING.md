# Contributing to the Aileron Hub

The Hub catalogs three entry types per [ADR-0013](https://github.com/ALRubinger/aileron/blob/main/docs/src/content/docs/adr/0013-connector-hub-and-trust-distribution.md):

- **Connectors** under `connectors/` — sandboxed adapters that talk to a third-party service.
- **Actions** under `actions/` — reusable action templates ([ADR-0003](https://github.com/ALRubinger/aileron/blob/main/docs/src/content/docs/adr/0003-action-templates.md)) that depend on exactly one connector.
- **Action suites** under `suites/` — bundles of actions, optionally spanning multiple connectors.

All three are **discovery pointers**. The Hub stores no binaries, no action bodies, and no suite manifests; those live at the publisher's repo at the canonical FQN. CI validates every entry against the JSON Schemas under [`schema/`](./schema/), which mirror the `HubConnectorEntry` / `HubActionEntry` / `HubSuiteEntry` shapes in Aileron's [`internal/api/openapi.yaml`](https://github.com/ALRubinger/aileron/blob/main/internal/api/openapi.yaml).

To add an entry: fork, add the YAML file under the appropriate directory, and open a PR.

---

## Connectors

**Filename:** `connectors/github_<owner>_<repo>.yaml` (lowercase, `/` replaced with `_`). Example: `github_alrubinger_aileron-connector-google.yaml`.

**Schema:** [`schema/connector-entry.schema.json`](./schema/connector-entry.schema.json).

```yaml
fqn: github://OWNER/REPO
description: One-line description of what the connector does.
publisher_github: OWNER
key_url: https://raw.githubusercontent.com/OWNER/REPO/main/keys/publisher.pub
release_pattern: v*
```

Required fields:

- `fqn` — canonical FQN. Must be `github://OWNER/REPO`.
- `description` — short, one-line description (≤200 chars).
- `publisher_github` — GitHub user or org that owns the connector repo.
- `key_url` — public URL of the publisher's ed25519 signing key (typically `keys/publisher.pub` on the connector repo's main branch).
- `release_pattern` — glob matching the release tags Aileron should consider.

**Surfaces as:** `aileron hub list connectors` in the CLI and the **Connectors** tab in the webapp; clicking through opens the connector detail page with publisher footprint and risk indicators. See the publisher guide in the Aileron repo for end-to-end packaging steps.

---

## Actions

**Filename:** `actions/github_<owner>_<repo>_actions_<name>.yaml` (lowercase, `/` replaced with `_`). Example: `github_alrubinger_aileron-connector-google_actions_draft-email.yaml`.

**Schema:** [`schema/action-entry.schema.json`](./schema/action-entry.schema.json).

```yaml
fqn: github://OWNER/REPO/actions/NAME
description: One-line description of what the action does.
publisher_github: OWNER
connector_fqn: github://OWNER/REPO
intents:
  - draft email
  - compose gmail
category: communication
```

Required fields:

- `fqn` — canonical FQN. Must be `github://OWNER/REPO/actions/NAME`.
- `description` — short, one-line description (≤200 chars).
- `publisher_github` — GitHub user or org that owns the action's repo.
- `connector_fqn` — FQN of the connector this action depends on. Drives Hub-side filtering by provider and the install-decision dependency closure.

Optional fields:

- `intents` — informational phrases describing what users would ask their agent to do to trigger this action.
- `category` — discovery grouping (e.g. `communication`, `productivity`).

**Surfaces as:** `aileron hub list actions` in the CLI and the **Actions** tab in the webapp; clicking through opens the action detail page (intents, depended-on connector, install button). The action template body itself (TOML frontmatter + Markdown per ADR-0003) is fetched from the publisher's repo at install time. See the publisher action-template guide in the Aileron repo.

---

## Action suites

**Filename:** `suites/github_<owner>_<repo>_suite.yaml` for the single-suite form, or `suites/github_<owner>_<repo>_suites_<name>.yaml` for named/nested suites. Example: `suites/github_alrubinger_aileron-connector-google_suite.yaml`.

**Schema:** [`schema/suite-entry.schema.json`](./schema/suite-entry.schema.json).

```yaml
fqn: github://OWNER/REPO/suite
description: One-line description of what the suite bundles.
publisher_github: OWNER
member_actions:
  - github://OWNER/REPO/actions/A
  - github://OWNER/REPO/actions/B
connectors_required:
  - github://OWNER/REPO
category: communication
```

Required fields:

- `fqn` — canonical FQN. Must be `github://OWNER/REPO/suite` (single-suite form) or `github://OWNER/REPO/suites/NAME` (named).
- `description` — short, one-line description (≤200 chars).
- `publisher_github` — GitHub user or org that owns the suite's repo.
- `member_actions` — non-empty array of action FQNs bundled in this suite. Every entry must resolve to a YAML under `actions/` (CI checks this).

Optional fields:

- `connectors_required` — array of connector FQNs the suite's actions transitively depend on. **CI-computed:** if you include this list, CI verifies it equals the union of `member_actions[].connector_fqn` exactly. If you omit it, the daemon derives the closure from `member_actions` at query time, so leaving it out is fine and avoids drift when actions are added or removed.
- `category` — discovery grouping.

**Surfaces as:** `aileron hub list suites` in the CLI and the **Suites** tab in the webapp; the suite detail page shows member actions and the connector closure (with each connector's trust state) before install. The authoritative `suite.toml` (per Aileron #564) lives in the publisher's repo; the Hub entry is the discovery pointer.

---

## Trust and vetting

The Hub does not vet listed connectors, actions, or suites. Listing only means "this entry exists." Aileron users decide for themselves whether to trust the underlying publisher's signing key.

## Filename collisions

Filenames include `<scheme>_<owner>_<repo>_<subpath>` so different publishers shipping similarly named connectors, actions, or suites do not collide.
