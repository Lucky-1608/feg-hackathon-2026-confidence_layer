with open("alembic/env.py", "r") as f:
    env = f.read()

env = env.replace(
    "    config.set_main_option(\"sqlalchemy.url\", database_url)",
    "    if database_url.startswith('postgresql://'):\n        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')\n    config.set_main_option(\"sqlalchemy.url\", database_url)"
)

with open("alembic/env.py", "w") as f:
    f.write(env)
