from services.cache_service import cache

print(cache.exists("Fatal Push"))

cache.save("Fatal Push", {"name": "Fatal Push", "mana_cost": "{B}"})

print(cache.exists("Fatal Push"))

print(cache.load("Fatal Push"))

