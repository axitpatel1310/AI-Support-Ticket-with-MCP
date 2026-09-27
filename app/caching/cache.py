import redis
import hashlib

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

CACHE_EXPIRY = 600

def generate_cache_key(message:str) -> str:
    norm_message = message.strip().lower()
    hash_message = hashlib.sha256(
        norm_message.encode()
    ).hexdigest()
    return f"chat:{hash_message}"

def get_cached_response(message: str):
    key = generate_cache_key(message)
    return redis_client.get(key)

def cache_response(message: str, response: str):
    key = generate_cache_key(message)
    redis_client.setex(
        key, CACHE_EXPIRY, response
    )