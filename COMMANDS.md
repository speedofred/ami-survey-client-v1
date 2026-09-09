# Commands and the benchmarking runner

Everything here needs a clone of this repository. **None of it is required to
take part** - the one-line install in the [README](https://github.com/speedofred/ami-survey-client-v1/blob/main/README.md) is the whole
of the measured route, and it carries no commands at all.

What this file is for: running the same workflow against several models on your
own API key, so the comparison is between the models rather than between two
afternoons.

## Getting a clone

```bash
git clone https://github.com/speedofred/ami-survey-client-v1
cd ami-survey-client-v1
python3 ami-survey/scripts/install.py --user
```

It asks for your submission token and that is the only thing to supply. Then
restart your agent. [GETTING-STARTED.md](https://github.com/speedofred/ami-survey-client-v1/blob/main/GETTING-STARTED.md) has the
Windows form, the Codex form, and what to do when it does not work.

## What is in here

| | |
|---|---|
| `ami_survey/adapters/` | reads a harness's own session log; one adapter per harness, currently Claude Code and Codex |
| `ami_survey/mcp_server.py` | the `ami_*` tools your agent calls |
| `ami_survey/client.py` | talks to the survey service |
| `skills/` | the procedure, in the skill format Claude Code and Codex both read |
| `ami_survey/runners/` | drives a workflow against a provider's API, with your own key |
| `scripts/install.py` | wires the above into your agent |
| `workflows/` | a sample workflow to practise on |
| `bin/` | the commands below |

The survey service itself, meaning the field definitions, scoring, pricing and
storage, is not in this repository. This half runs on your machine; that half runs on the
server, and the two speak over HTTPS.

Submissions go to **`survey.agentbenchmark.dev`** and nowhere else. That is a
constant in the source, not a setting: there is no local survey to run here, and
a result that never left your machine would not be comparable with anyone
else's, which is the entire point of the exercise. Submitting needs a token,
and the client registers this machine for one by itself the first time it needs
one.

## Commands

In `ami-survey/bin/`. Each is a wrapper that sets `PYTHONPATH` and runs a module,
so they work from a clone with nothing installed. `--help` on any of them prints
its full flags.

### Benchmarking a workflow across models

**`ami-run`** runs a workflow against a provider's API, on your key and your
account. It reads the `usage` block off every real response, and submits the survey. One
agent loop over four sandboxed file tools, identical for every provider, which is
what makes the numbers comparable between them.

```bash
export OPENAI_API_KEY=...

# see what would run, without calling anything
ami-survey/bin/ami-run support-ticket-triage --provider openai --model gpt-4.1 --dry-run

# the real thing
ami-survey/bin/ami-run support-ticket-triage --provider openai    --model gpt-4.1
ami-survey/bin/ami-run support-ticket-triage --provider anthropic --model claude-sonnet-4-5
ami-survey/bin/ami-run support-ticket-triage --provider gemini    --model gemini-2.5-pro

# a workflow someone sent you, kept wherever you put it
ami-survey/bin/ami-run their-workflow --dir ~/Downloads/handover \
    --provider openai --model gpt-4.1

# any OpenAI-compatible endpoint, including a local model
ami-survey/bin/ami-run support-ticket-triage --provider openai --model llama3.3 \
    --base-url http://localhost:11434/v1 --api-key-env OLLAMA_API_KEY
```

Always `--dry-run` first with a workflow you did not write. It resolves the
prompt, shows the sandboxed workspace, names any `---` blocks it is *not*
sending, and calls nothing.

Worth knowing about `--grade`: the default is `auto`, which has the model grade
its own output. That is the one field in the survey nothing can check, so for
anything you intend to stand behind, use `--grade skip` and submit your own
grade afterwards with `--no-reset`.

### Managing workflows

**`ami-workflow`** lists, scaffolds and prepares them. It never runs anything;
that is `ami-run`, and they are separate commands so that printing a prompt and
spending money on an API are not one word apart.

```bash
ami-survey/bin/ami-workflow list
ami-survey/bin/ami-workflow new my-workflow
ami-survey/bin/ami-workflow show support-ticket-triage
ami-survey/bin/ami-workflow show support-ticket-triage --prompt   # just the prompt
ami-survey/bin/ami-workflow list --dir ~/Downloads/handover
```

`show` clears the workflow's `output/` first, because a benchmark is only
comparable if every run starts from the same state, then prints the two messages
to send: the workflow prompt, and the separate request that closes the
measurement window. `--no-reset` prints without clearing.

### The rest

**`ami-session`** reports which session the adapter would measure, and why. The first
thing to run when a survey measured the wrong thing.

```bash
ami-survey/bin/ami-session          # the session this survey would read
ami-survey/bin/ami-session --all    # every session it can see
```

**`ami-skill`** prints the survey procedure and tool schemas, for a runtime that is
not an MCP client.

```bash
ami-survey/bin/ami-skill                          # the procedure
ami-survey/bin/ami-skill --runtime http           # for a plain-HTTP caller
ami-survey/bin/ami-skill --tools openai           # schemas as function defs
```

**`ami-mcp`** is the MCP server your agent launches. `scripts/install.py` writes
it into your agent's configuration; you rarely run it yourself.

Reading the collected results is not here: submissions live on the survey
service, and the dashboard there is where runs are compared.

## Removing it

```bash
python3 ami-survey/scripts/uninstall.py
```
