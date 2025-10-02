# Transcript Review Artifacts

This repository now includes an automated review step that aligns transcripts back to their source audio and produces a `*.review.json` file for every transcript that is generated.

## What the review file contains

Each review artifact captures:

- `words`: ordered list of every token from the transcript with:
  - `start` / `end` timestamps (seconds) from the forced alignment pass
  - `confidence` from the Whisper alignment model
  - `flags` so manual reviewers can focus on potential issues
- `flags_summary`: counts of each flag type that was triggered
- `audit`: reserved for downstream workflow integrations (defaults to an empty list)

## Flag types

All flags are deterministic and configurable. The default rules are:

| Flag | Trigger |
| ---- | ------- |
| `low_confidence` | Whisper probability below the configured threshold (`LowConfidenceThreshold`, default `0.85`). |
| `number` | Token contains a numeric digit and should be manually verified. |
| `unknown_lexicon` | Token longer than the configured `MinLexiconWordLength` not found in `config/nouns_to_expect.txt`. |

## Configuration

All review settings live in `config/call_pipeline.ini` under the `[Review]` section:

```ini
[Review]
Enabled = true
AlignmentModel = base
AlignmentDevice = cpu
OutputDirectory =
LowConfidenceThreshold = 0.85
AlignmentMatchThreshold = 0.6
AlignmentSearchWindow = 8
FlagNumbers = true
FlagUnknownLexicon = true
MinLexiconWordLength = 4
ReuseAlignmentModel = true
```

- Setting `OutputDirectory` creates the review file in a custom folder. Leave blank to store it next to the transcript.
- `AlignmentModel`/`AlignmentDevice` control which Whisper model is used for forced alignment.
- `AlignmentMatchThreshold` and `AlignmentSearchWindow` tune how strictly transcript tokens must match Whisper outputs.
- Set `Enabled = false` to skip review generation entirely.

Update the parallel `config/call_pipeline_with_normalization.ini` file if you rely on that profile.

## Dependencies

The review step reuses the existing `openai-whisper` dependency. No new packages are required beyond those already listed in `requirements.txt`.

## Manual review workflow

1. Run the pipeline normally.
2. Inspect the generated `*.review.json` alongside each transcript.
3. Prioritize words with `low_confidence`, `number`, or `unknown_lexicon` flags for human verification.

The review generator keeps the `audit` list empty so other teams can append workflow decisions without altering the automatically produced payload.
