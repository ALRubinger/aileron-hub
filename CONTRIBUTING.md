# Contributing a connector

To list your connector in the Aileron Hub:

1. Fork this repo.
2. Add a YAML file under `connectors/` named `github_<owner>_<repo>.yaml` (lowercase, `/` replaced with `_`). For example, `github_alrubinger_aileron-connector-google.yaml`.
3. Open a PR.
4. CI validates the entry against [`schema/connector-entry.schema.json`](./schema/connector-entry.schema.json).

## Entry format

```yaml
fqn: github://OWNER/REPO
description: One-line description of what the connector does.
publisher_github: OWNER
key_url: https://raw.githubusercontent.com/OWNER/REPO/main/keys/publisher.pub
release_pattern: v*
```

Required fields:

- `fqn` — the canonical FQN where the connector lives. Must be `github://OWNER/REPO` (other VCS schemes may be added later).
- `description` — short, one-line description.
- `publisher_github` — the GitHub user or org name that owns the connector repo.
- `key_url` — public URL of the publisher's ed25519 signing key (typically `keys/publisher.pub` on the connector repo's main branch).
- `release_pattern` — glob matching the release tags Aileron should consider.

## Trust and vetting

The Hub does not vet listed connectors. Listing only means "this connector exists." Aileron users decide for themselves whether to trust the publisher's signing key.

## Filename collisions

Different publishers may ship connectors with the same short name (e.g., two `slack-connector` repos). That's fine — the filename includes the owner (`github_<owner>_<repo>.yaml`), so entries don't collide.
