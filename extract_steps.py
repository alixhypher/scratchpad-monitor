from inspect_ai.log import read_eval_log, read_eval_log_samples
def test_import():
    print("import worked")

def extract_steps(msgs):
    """Extracts reasoning steps and function callsfrom assistant messages in the log.
        step['assistant_summary'] is the assistant's reasoning summary for that step (if available)
        tool_calls['function'] is the function name
        tool_calls['arguments'] is the arguments passed to the function"""
    steps = []

    for j, m in enumerate(msgs):
        if j == 1:
            steps.append({
                "message_index": j,
                "task_description": getattr(m, "content",None)
            })
            continue
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
                # tool_calls['function'] is the function name
                # tool_calls['arguments'] is the arguments passed to the function
            })

    return steps

def get_sample_steps_set(log_path, max_samples=10):
    samples = []
    for i, sample in enumerate(read_eval_log_samples(log_path,all_samples_required=False)):
        msgs = getattr(sample, "messages", None)
        if msgs:
            steps = extract_steps(msgs)
            samples.append({"id": getattr(sample, "id", None), "steps": steps})
        if i >= max_samples-1:
            break
    return samples

if __name__ == "__main__":
    log_path = "Logs/honest_mimo-monitor_5-resamples-004.eval"
    if False:
        samples = get_sample_steps_set(log_path,max_samples=2)
        for sample in samples:
            print(f"\n=== SAMPLE {sample['id']} ===")
            for step in sample['steps']:
                print(f"{step['message_index']}: {step['assistant_summary']}")
                for call in step['tool_calls']:
                    print(f"{call['function']}")
                    print(f"{call['arguments']}")
            print(f"===end sample {sample['id']}===")
    else:
        for i, sample in enumerate(read_eval_log_samples(log_path,all_samples_required=False)):
            print(f"\n=== SAMPLE {i} ===")
            print("id:", getattr(sample, "id", None))
            print("input:", getattr(sample, "input", None))
            msgs = getattr(sample, "messages", None)
            print("messages type:", type(msgs).__name__)
            if msgs:
                print("Captured steps:")
                steps = extract_steps(msgs)
                for i,step in enumerate(steps):
                    if i == 0:
                        print(f"Task description: {step['task_description']}")
                        continue
                    print(f"{step['message_index']}: {step['assistant_summary']}")
                    #print(f"{step['tool_calls']}")
                    for call in step['tool_calls']:
                        print(f"{call['function']}")
                        print(f"{call['arguments']}")
            print(f"===end sample {i}===")
            if i >= 1:
                break