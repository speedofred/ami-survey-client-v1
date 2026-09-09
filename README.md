# AMI survey client

Measures what a completed agent workflow cost to run, by reading the runtime's
own session log, and submits the result to the AMI survey at
`survey.agentbenchmark.dev`.

The cost of a single API call is easy to obtain. The cost of one finished piece
of work is not: one triaged ticket, one screened CV, one drafted reply, across
every call, retry and tool round-trip the agent made getting there. This
measures that figure.

Every number is read from the runtime's records rather than reported by the
agent. An agent asked how many tokens it has just used will estimate, and will
present the estimate with confidence.

## What comes back

A real run of six support tickets, triaged and answered by Claude Opus 5 in
Claude Code:

```
Maturity Index      85.0  Strong          (observability 40%, evidence 30%, quality 30%)
Performance         78.13 Strong          confidence Very High

  quality           80.0   graded Good on ami-quality-v2
  cost              72.73  $0.123226 per ticket   ($0.739355 for the run)
  speed             84.47  20.90s per ticket
  evidence          70.0   measured, on a self-issued token
  observability    100.0

findings
  weakness  Cost is the weakest pillar at 72.73; speed is strongest at 84.47.
            $0.123226 per unit against a $0.01 reference. A cheaper model, or
            fewer calls, moves this; check calls[] for where the tokens went.

  note      Cost and speed were scored against a provisional reference, which is
            a placeholder rather than a measurement. Do not quote them as settled
            yet. The Maturity Index does not use the reference and is unaffected.
```

**$0.12 per ticket, 21 seconds per ticket.** That is the figure this exists to
produce, and it is the one most teams cannot currently state about their own
work.

The findings record where the scorecard's own numbers are soft. A cost reference
that is still a placeholder is reported as a placeholder rather than folded into
the score.

## Install

There are two routes. They differ in whether anything can read your runtime's
logs, which determines whether the result is recorded as `measured` or
`unmeasured`.

### Measured

Add this to your agent's MCP configuration and restart it:

```json
{ "mcpServers": { "ami-survey": { "command": "uvx", "args": ["ami-survey"] } } }
```

Then, once the agent finishes a piece of work, ask it:

> Take the AMI survey regarding the ticket triage you just did

There is nothing to clone and nothing to keep updated. No token needs to be
supplied: the first call that requires one registers the machine and stores the
token at `~/.ami-survey/token`.

`uvx` is part of [uv](https://docs.astral.sh/uv/), the tool the MCP
documentation uses for Python servers. If uv is not installed,
[GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md)
gives a `pipx` form and a route that requires neither.

If you already hold a token, set it as `AMI_API_TOKEN` in that block's `env` and
it will be used instead of registering a new one.

### Unmeasured

In claude.ai, open Settings, then Connectors, then Add custom connector, and
supply:

```
https://survey.agentbenchmark.dev/mcp
```

Nothing is installed and no token is required. These runs are recorded as
`unmeasured` and are never compared against measured ones: a remote server
cannot read your runtime's logs, so token counts and cost are absent rather than
estimated.

## Licence

An evaluation licence. This is not open source.

Permitted: installing and running the software on machines you control, for the
purpose of evaluating it and submitting survey responses; and redistributing
verbatim, unmodified copies with the licence intact.

Not permitted: modification beyond what is needed to run it for that purpose,
derivative works, sublicensing, and sale.

Full terms in
[LICENSE](https://github.com/speedofred/ami-survey-client-v1/blob/main/LICENSE).

## What leaves your computer

Token counts, timings, model names, the stage names the workflow declared, and
the grade. **Not your files, not your prompts, not your shell commands.**
[GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md)
sets this out in full.

Submissions go to `survey.agentbenchmark.dev` and nowhere else. That destination
is a constant in the source rather than a setting, so a stale environment
variable cannot redirect a submission onto your own disk. That is the one
failure which would make a run appear successful while collecting nothing.

## Requirements

Python 3.9 or newer. No dependencies; the standard library only.

## Further reading

- [GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md)
  assumes no prior setup, covers macOS, Linux and Windows, and explains what to
  do when the tools do not appear.
- [COMMANDS.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/COMMANDS.md)
  documents the clone-and-run route, which benchmarks one workflow across
  several models on your own API key. It is not required in order to take part.
- [MAKE-IT-MEASURABLE.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/MAKE-IT-MEASURABLE.md)
  explains how to structure a workflow so that there is something worth
  measuring.
