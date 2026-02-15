import asyncio

from app.api.jobs.runner import run_worker


if __name__ == "__main__":
    asyncio.run(run_worker())
