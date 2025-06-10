import redis
import logging

# Подключение к Redis
r = redis.Redis(host="redis", port=6379, decode_responses=True)


def confirm_medicine(user_id: int, time_str: str, medicine: str, is_confirm: bool):
    key = f"{user_id}:{time_str}:{medicine}"
    if is_confirm:
        r.set(key, "true", ex=86400)
        logging.info(f"[CONFIRM] Подтверждено: {key}")
    else:
        r.delete(key)
        logging.info(f"[UNCONFIRM] Сброшено подтверждение: {key}")


def is_confirmed(user_id: int, time_str: str, medicine: str) -> bool:
    key = f"{user_id}:{time_str}:{medicine}"
    confirmed = r.get(key) == "true"
    logging.info(f"[CHECK] Подтверждено ли {key}? {confirmed}")
    return confirmed
