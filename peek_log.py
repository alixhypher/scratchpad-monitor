from inspect_ai.log import read_eval_log, read_eval_log_samples
log_path = "Logs/honest_mimo-monitor_5-resamples-004.eval"

log = read_eval_log(log_path,header_only=True)
print("Loaded log")
for i, sample in enumerate(read_eval_log_samples(log_path,all_samples_required=False)):
    print(f"\n=== SAMPLE {i} ===")
    print("id:", getattr(sample, "id", None))
    print("input:", getattr(sample, "input", None))
    msgs = getattr(sample, "messages", None)
    print("messages type:", type(msgs).__name__)
    if msgs:
        print("message count:", len(msgs))
        for j, m in enumerate(msgs[:5]):
            print(f"\n--- Message {j} ---")
            if getattr(m, "role", None) == "assistant":
                print(m.content[0].summary)
                print("\n".join(f"{call.function}: {call.arguments}" for call in m.tool_calls))
                """
                for var in vars(m):
                    print(var, end=": ")
                    try:
                        print(getattr(m,var,None)[:200])
                    except Exception as e:
                        print("not getattr")
                print(j, getattr(m, "role", None), str(getattr(m, "content", ""))[:400])
                """
            print("===")
    if i >= 0:
        break