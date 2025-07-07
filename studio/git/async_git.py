import asyncio
from concurrent.futures import ThreadPoolExecutor
import git

class AsyncGit:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def status(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.repo.git.status)

    async def log(self, max_count=20):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: self.repo.git.log(f'--oneline', f'-{max_count}'))

    async def branches(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: self.repo.git.branch()) 