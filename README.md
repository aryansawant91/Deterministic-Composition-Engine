# Deterministic Composition Engine

A dependency-graph-based composition engine that accepts reusable modules,
validates their configuration and version compatibility, resolves execution
order deterministically, and generates a runtime configuration.

## Architecture Overview

The engine is a pipeline of pure, isolated stages. Each stage takes explicit
input and returns an explicit `Result` (success or a list of structured
errors) — nothing is thrown, nothing depends on hidden or global state.