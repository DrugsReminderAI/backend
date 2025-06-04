from collections import defaultdict

chat_memory = defaultdict(list)

def get_history(user_id: int):
    return chat_memory[user_id]

def append_to_history(user_id: int, role: str, content: str):
    chat_memory[user_id].append({
        "role": role,
        "content": content
    })

def clear_history(user_id: int):
    chat_memory[user_id].clear()
