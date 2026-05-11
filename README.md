# Aileron Connectors Hub

Discovery layer for [Aileron](https://github.com/ALRubinger/aileron) connectors. Each entry in `connectors/` points at a connector hosted at its canonical `github://OWNER/REPO` FQN. The Hub stores no binaries.

## What this repo is

- A public, community-maintained index of Aileron connectors.
- Pointers to connectors at `github://OWNER/REPO` FQNs — not a binary registry.
- Discovery only. Discovery and trust are decoupled: a connector appearing here is **not** an endorsement by Aileron.

## What this repo is not

- A registry that hosts connector binaries (they stay at their source repos).
- A vetting service. Aileron does not perform editorial review of listed connectors.
- A trust anchor. Users still verify trust via the Aileron keyring or the install-time prompt.

## Publishing a connector

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Background

- [ADR-0013: Connector Hub and Trust Distribution](https://github.com/ALRubinger/aileron/blob/main/docs/src/content/docs/adr/0013-connector-hub-and-trust-distribution.md)
- Umbrella issue: [aileron#488](https://github.com/ALRubinger/aileron/issues/488)

## License

Apache-2.0. See [LICENSE](./LICENSE).
