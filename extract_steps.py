from inspect_ai.log import read_eval_log, read_eval_log_samples
def test_import():
    print("import worked")
def extract_steps(msgs):
    steps = []

    for j, m in enumerate(msgs):
        if getattr(m, "role", None) != "assistant":
            continue

        summary = None
        if getattr(m, "content", None):
            first = m.content[0]
            if getattr(first, "type", None) == "reasoning":
                summary = getattr(first, "summary", None)

        tool_calls = []
        for call in getattr(m, "tool_calls", []) or []:
            tool_calls.append({
                "function": getattr(call, "function", None),
                "arguments": getattr(call, "arguments", None),
            })

        if summary or tool_calls:
            steps.append({
                "message_index": j,
                "assistant_summary": summary,
                "tool_calls": tool_calls,
            })

    return steps