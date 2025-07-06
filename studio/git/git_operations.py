import asyncio
from concurrent.futures import ThreadPoolExecutor
from git import Repo, GitCommandError, InvalidGitRepositoryError
from pathlib import Path
import re

class GitOperations:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.repo = Repo(repo_path)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def _run_git_command(self, *args):
        """Run a Git command asynchronously"""
        loop = asyncio.get_event_loop()
        def run():
            cmd = args[0]
            cmd_args = args[1:]
            return getattr(self.repo.git, cmd)(*cmd_args)
        return await loop.run_in_executor(self.executor, run)
    
    # Basic Operations
    async def status(self):
        """Get repository status"""
        return await self._run_git_command('status', '--porcelain')
    
    async def log(self, max_count=50, branch=None):
        """Get commit log"""
        cmd = ['log', f'--max-count={max_count}', '--oneline', '--graph']
        if branch:
            cmd.append(branch)
        return await self._run_git_command(*cmd)
    
    async def branches(self):
        """Get all branches"""
        return await self._run_git_command('branch', '-a')
    
    # Branch Management
    async def create_branch(self, name, start_point=None):
        """Create a new branch"""
        cmd = ['checkout', '-b', name]
        if start_point:
            cmd.append(start_point)
        return await self._run_git_command(*cmd)
    
    async def delete_branch(self, name, force=False):
        """Delete a branch"""
        cmd = ['branch']
        if force:
            cmd.append('-D')
        else:
            cmd.append('-d')
        cmd.append(name)
        return await self._run_git_command(*cmd)
    
    async def checkout(self, ref):
        """Checkout a branch or commit"""
        return await self._run_git_command('checkout', ref)
    
    async def merge(self, branch, strategy=None):
        """Merge a branch"""
        cmd = ['merge']
        if strategy:
            cmd.extend(['-s', strategy])
        cmd.append(branch)
        return await self._run_git_command(*cmd)
    
    async def rebase(self, branch, interactive=False):
        """Rebase current branch onto another"""
        cmd = ['rebase']
        if interactive:
            cmd.append('-i')
        cmd.append(branch)
        return await self._run_git_command(*cmd)
    
    # Stash Operations
    async def stash(self, message=None, include_untracked=False):
        """Create a stash"""
        cmd = ['stash', 'push']
        if message:
            cmd.extend(['-m', message])
        if include_untracked:
            cmd.append('-u')
        return await self._run_git_command(*cmd)
    
    async def stash_list(self):
        """List stashes"""
        return await self._run_git_command('stash', 'list')
    
    async def stash_pop(self, stash_ref='stash@{0}'):
        """Pop a stash"""
        return await self._run_git_command('stash', 'pop', stash_ref)
    
    async def stash_apply(self, stash_ref='stash@{0}'):
        """Apply a stash without removing it"""
        return await self._run_git_command('stash', 'apply', stash_ref)
    
    # Commit Operations
    async def commit(self, message, add_all=False):
        """Create a commit"""
        if add_all:
            await self._run_git_command('add', '-A')
        return await self._run_git_command('commit', '-m', message)
    
    async def amend_commit(self, message=None):
        """Amend the last commit"""
        cmd = ['commit', '--amend']
        if message:
            cmd.extend(['-m', message])
        return await self._run_git_command(*cmd)
    
    # Remote Operations
    async def fetch(self, remote=None):
        """Fetch from remote"""
        cmd = ['fetch']
        if remote:
            cmd.append(remote)
        return await self._run_git_command(*cmd)
    
    async def pull(self, remote=None, branch=None):
        """Pull from remote"""
        cmd = ['pull']
        if remote and branch:
            cmd.extend([remote, branch])
        return await self._run_git_command(*cmd)
    
    async def push(self, remote=None, branch=None, force=False):
        """Push to remote"""
        cmd = ['push']
        if force:
            cmd.append('--force')
        if remote and branch:
            cmd.extend([remote, branch])
        return await self._run_git_command(*cmd)
    
    # Submodule Operations
    async def submodule_update(self, init=False, recursive=False):
        """Update submodules"""
        cmd = ['submodule', 'update']
        if init:
            cmd.append('--init')
        if recursive:
            cmd.append('--recursive')
        return await self._run_git_command(*cmd)
    
    async def submodule_add(self, url, path):
        """Add a submodule"""
        return await self._run_git_command('submodule', 'add', url, path)
    
    # Git Flow Operations
    async def gitflow_init(self):
        """Initialize Git Flow"""
        return await self._run_git_command('flow', 'init', '-d')
    
    async def gitflow_feature_start(self, name):
        """Start a feature branch"""
        return await self._run_git_command('flow', 'feature', 'start', name)
    
    async def gitflow_feature_finish(self, name):
        """Finish a feature branch"""
        return await self._run_git_command('flow', 'feature', 'finish', name)
    
    async def gitflow_release_start(self, version):
        """Start a release branch"""
        return await self._run_git_command('flow', 'release', 'start', version)
    
    async def gitflow_release_finish(self, version):
        """Finish a release branch"""
        return await self._run_git_command('flow', 'release', 'finish', version)
    
    # Advanced Operations
    async def cherry_pick(self, commit_hash):
        """Cherry-pick a commit"""
        return await self._run_git_command('cherry-pick', commit_hash)
    
    async def reset(self, ref, mode='--soft'):
        """Reset to a commit"""
        return await self._run_git_command('reset', mode, ref)
    
    async def revert(self, commit_hash):
        """Revert a commit"""
        return await self._run_git_command('revert', commit_hash)
    
    # Repository Information
    async def get_remotes(self):
        """Get remote information"""
        return await self._run_git_command('remote', '-v')
    
    async def get_tags(self):
        """Get all tags"""
        return await self._run_git_command('tag', '-l')
    
    async def get_config(self, key=None):
        """Get Git configuration"""
        cmd = ['config', '--list']
        if key:
            cmd = ['config', '--get', key]
        return await self._run_git_command(*cmd)
    
    # File Operations
    async def add_file(self, file_path):
        """Add a file to staging"""
        return await self._run_git_command('add', file_path)
        
    async def reset_file(self, file_path):
        """Reset a file from staging"""
        return await self._run_git_command('reset', file_path)
        
    async def checkout_file(self, file_path, version="HEAD"):
        """Checkout a specific version of a file"""
        return await self._run_git_command('checkout', version, '--', file_path)
        
    async def write_file_content(self, file_path, content):
        """Write content to a file"""
        file_path = Path(self.repo_path) / file_path
        file_path.write_text(content)
        
    async def get_file_content(self, file_path):
        """Get file content"""
        file_path = Path(self.repo_path) / file_path
        return file_path.read_text()
        
    async def add_files(self, file_paths):
        """Add multiple files to staging"""
        return await self._run_git_command('add', *file_paths)
        
    # Branch Management (enhanced)
    async def checkout_branch(self, branch_name):
        """Checkout a branch"""
        return await self._run_git_command('checkout', branch_name)
        
    async def merge_branch(self, source_branch, target_branch):
        """Merge source branch into target branch"""
        # First checkout target branch
        await self._run_git_command('checkout', target_branch)
        # Then merge source branch
        return await self._run_git_command('merge', source_branch)
        
    async def rebase_branch(self, source_branch, target_branch):
        """Rebase source branch onto target branch"""
        # First checkout source branch
        await self._run_git_command('checkout', source_branch)
        # Then rebase onto target branch
        return await self._run_git_command('rebase', target_branch)
        
    # Stash Operations (enhanced)
    async def create_stash(self, stash_name, message):
        """Create a stash with name and message"""
        cmd = ['stash', 'push']
        if message:
            cmd.extend(['-m', message])
        return await self._run_git_command(*cmd)
        
    async def apply_stash(self, stash_name):
        """Apply a stash"""
        return await self._run_git_command('stash', 'apply', stash_name)
        
    async def pop_stash(self, stash_name):
        """Pop a stash"""
        return await self._run_git_command('stash', 'pop', stash_name)
        
    async def drop_stash(self, stash_name):
        """Drop a stash"""
        return await self._run_git_command('stash', 'drop', stash_name)
        
    async def stash_show(self, stash_name):
        """Show stash contents"""
        return await self._run_git_command('stash', 'show', '-p', stash_name)
        
    # Conflict Resolution
    async def check_merge_conflicts(self, source_branch, target_branch):
        """Check for merge conflicts between branches"""
        try:
            # Try to merge without committing
            await self._run_git_command('merge', '--no-commit', '--no-ff', source_branch)
            # If successful, abort the merge
            await self._run_git_command('merge', '--abort')
            return []
        except GitCommandError:
            # Merge failed, check for conflicted files
            status = await self._run_git_command('status', '--porcelain')
            conflicts = []
            for line in status.split('\n'):
                if line.strip() and line.startswith('UU'):
                    conflicts.append(line[3:].strip())
            # Abort the merge
            await self._run_git_command('merge', '--abort')
            return conflicts
            
    # Current branch
    async def current_branch(self):
        """Get current branch name"""
        return await self._run_git_command('branch', '--show-current')
        
    # Run command (generic)
    async def run_command(self, *args):
        """Run a generic git command"""
        return await self._run_git_command(*args)
    
    async def remove_file(self, file_path, cached=False):
        """Remove a file"""
        cmd = ['rm']
        if cached:
            cmd.append('--cached')
        cmd.append(file_path)
        return await self._run_git_command(*cmd)
    
    async def diff(self, file_path=None, staged=False):
        """Show diff"""
        cmd = ['diff']
        if staged:
            cmd.append('--cached')
        if file_path:
            cmd.append(file_path)
        return await self._run_git_command(*cmd) 