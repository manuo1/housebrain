import os


def environment_is_development():
    return os.environ.get("ENVIRONMENT", "development") == "development"
