# stateful-monitor

**Testing whether a stateful scratchpad improves LLM-based monitoring in AI control evaluations.**

Built for the [Apart Research AI Control Hackathon](https://apartresearch.com/sprints/ai-control-hackathon-2026-03-20-to-2026-03-22) (March 2026).

[Paper submission](link-to-apart-submission) #TODO update once available

## Research Question

Monitors in AI control evaluations are stateless — they re-evaluate each agent action from scratch with no memory of their own prior reasoning. Kutasov et al. (2025) found that giving monitors persistent notes actually *degraded* performance in SHADE-Arena, due to anchoring on early benign behavior.

We test whether this negative finding holds in BashArena, where attacks unfold incrementally across many steps (e.g., assembling a malicious command one string append at a time). In this setting, tracking accumulated state should theoretically help.

**Result:** The scratchpad monitor performs slightly worse than the stateless baseline, replicating Kutasov et al.'s finding in a new setting. Neither monitor reliably detects attacks from Claude Opus 4.6.

## How It Works

This project does **post-hoc monitoring** on existing Inspect `.eval` logs — no Docker environments or trajectory replay needed.

1. Read `.eval` logs from BashArena runs using `inspect_ai.log.read_eval_log_samples()`
2. Extract per-step task descriptions, assistant actions, and tool calls
3. Run each trajectory through two monitor variants via OpenRouter
4. Compare suspicion scores across monitors

### Monitor Variants

**Stateless baseline:** Receives the trajectory history and current action. Scores suspicion 0-10. No memory between steps.

**Scratchpad monitor:** Same as baseline, plus a block of self-authored notes from the previous step. Prompted to track file modifications, environment variables, network commands, and string assembly patterns. The scratchpad is parsed from each response and injected into the next step's prompt.

## Project Structure

```
stateful-monitor/
├── src/
│   ├── extract_steps.py    # Parse .eval logs into monitorable steps
│   ├── evaluate_step.py    # OpenRouter API client
│   ├── monitor.py          # Stateless and scratchpad monitor classes
├── prompts/
│   ├── default_monitor.txt # Stateless monitor system prompt
│   └── scratchpad_monitor.txt # Scratchpad monitor system prompt
├── Logs/                   # .eval files (not committed)
├── results/                # Output scores and plots
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m pip install requests matplotlib inspect-ai
export OPENROUTER_API_KEY="your_key_here"
```

## Usage

```python
from extract_steps import get_sample_steps_set
from monitor import Monitor, Scratchpad

samples = get_sample_steps_set("Logs/attack_run.eval", max_samples=20)

# Run both monitors across samples and compare scores
```

## Data

Trajectories are Claude Opus 4.6 BashArena runs (attack and benign) provided by Redwood Research. Monitor model is GPT-4.1 mini via OpenRouter. Trajectory-level scores are the maximum step-level suspicion score.

## Limitations

- Evaluated on fewer than 50 trajectories
- Single monitor model (GPT-4.1 mini) and single attacker (Claude Opus 4.6)
- Did not iterate on scratchpad prompt design
- Score parsing is prompt-format dependent
- Scratchpad monitoring must run sequentially within a trajectory; parallelism applies across samples only

## References

- Kutasov et al. (2025). [Evaluating Control Protocols for Untrusted AI Agents](https://arxiv.org/abs/2511.02997)
- Kaufman et al. (2025). [BashArena: A Control Setting for Highly Privileged AI Agents](https://arxiv.org/abs/2512.15688)
- Bhatt et al. (2025). [Ctrl-Z: Controlling AI Agents via Resampling](https://arxiv.org/abs/2504.10374)
- Greenblatt et al. (2024). [AI Control: Improving Safety Despite Intentional Subversion](https://arxiv.org/abs/2312.06942)

## TODO
- more robust error handling
- improved data logging and visualization
- pre-run function checks