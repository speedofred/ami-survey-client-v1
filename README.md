# AMI — what did that workflow actually cost?

You can find out what a single API call costs. Almost nobody can say what one
finished piece of work costs — one triaged ticket, one screened CV, one drafted
reply — across every call, retry and tool round-trip the agent made getting
there.

This measures it, by reading your runtime's own session log after the fact. Ask
your agent to run it when it finishes something, and you get a scorecard back.

Every number comes from the log, not from the agent. An agent asked how many
tokens it just used will guess, and guess confidently.

## What comes back

A real run — six support tickets triaged and answered by Claude Opus 5 in Claude
Code:

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

**$0.12 per ticket, 21 seconds per ticket.** That is the number this exists to
produce, and it is the one most teams cannot currently state about their own
work.

The findings are worth reading twice: the scorecard says out loud where its own
numbers are soft. A cost reference that is still a placeholder is a placeholder
in your report too, not quietly folded into a score.

## Install

Two ways in. The difference between them is whether anything can read your
runtime's logs, and that decides whether your numbers are **measured** or
**unmeasured**.

### Measured — one line

Add this to your agent's MCP configuration and restart it:

```json
{ "mcpServers": { "ami-survey": { "command": "uvx", "args": ["ami-survey"] } } }
```

Then ask your agent, after it finishes a piece of work:

> Take the AMI survey regarding the ticket triage you just did

That is the whole setup. Nothing to clone, nothing to keep updated, and no token
to paste — the first call that needs one registers this machine and stores it at
`~/.ami-survey/token`.

**`uvx` comes from [uv](https://docs.astral.sh/uv/)** — the same tool the MCP
docs use for Python servers, so if you have installed one before you already
have it. If you would rather not, [GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md)
has a `pipx` form and a route that needs neither.

Already have a token? Put it in that block's `env` as `AMI_API_TOKEN` and it is
used instead of registering a new one.

### Unmeasured — a remote connector, nothing installed

In claude.ai: Settings → Connectors → Add custom connector, and give it

```
https://survey.agentbenchmark.dev/mcp
```

Nothing to install and no token. These runs are recorded as `unmeasured` and are
never compared against measured ones — a server on the other side of the
internet cannot read your runtime's logs, so the token counts and cost are
simply absent rather than guessed.

Install the client above when you want those numbers too.

## Licence, up front

**This is not open source.** It is an evaluation licence: run it on machines you
control, redistribute it verbatim if you like, but it may not be modified, sold
or built upon. Full terms in
[LICENSE](https://github.com/speedofred/ami-survey-client-v1/blob/main/LICENSE).

Said here rather than at the bottom, because finding it at the bottom after
reading everything else is worse than being told now.

## What leaves your computer

Token counts, timings, model names, the stage names your workflow declared, and
the grade. **Not your files, not your prompts, not your shell commands.**
[GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md)
sets this out in full.

Submissions go to `survey.agentbenchmark.dev` and nowhere else. That destination
is a constant in the source rather than a setting: a stale environment variable
cannot redirect your submission onto your own disk, which is the one failure that
would make a run look successful while collecting nothing.

## Requirements

Python 3.9 or newer. No dependencies — the standard library only.

## Everything else

- [GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md)
  — assumes no prior setup; macOS, Linux and Windows, and what to do when it does
  not work.
- [COMMANDS.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/COMMANDS.md)
  — the clone-and-run route: benchmarking one workflow across several models on
  your own API key. Not needed to take part.
- [MAKE-IT-MEASURABLE.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/MAKE-IT-MEASURABLE.md)
  — how to structure a workflow so there is something worth measuring.
