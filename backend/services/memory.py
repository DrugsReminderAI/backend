from collections import defaultdict

chat_memory = defaultdict(list)


def get_history(user_id: int):
    return chat_memory[user_id]


def append_to_history(
    user_id: int,
    role: str,
    content: str,
    tool_call_id: str = None,
    tool_calls: list = None,
):
    message = {"role": role}

    if content is not None:
        message["content"] = content
    if tool_call_id:
        message["tool_call_id"] = tool_call_id
    if tool_calls:
        message["tool_calls"] = tool_calls

    chat_memory[user_id].append(message)


def clear_history(user_id: int):
    chat_memory[user_id].clear()
