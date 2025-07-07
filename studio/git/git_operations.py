import asyncio
from concurrent.futures import ThreadPoolExecutor
import git
from pathlib import Path
import re
import os
import tempfile

class GitOperations:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def _run_git_command(self, *args, env=None):
        """Run a Git command asynchronously, with optional environment variables"""
        loop = asyncio.get_event_loop()
        def run():
            cmd = args[0]
            cmd_args = args[1:]
            return getattr(self.repo.git, cmd)(*cmd_args, env=env) if env else getattr(self.repo.git, cmd)(*cmd_args)
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
        """Delete a local branch"""
        cmd = ['branch']
        if force:
            cmd.append('-D')
        else:
            cmd.append('-d')
        cmd.append(name)
        return await self._run_git_command(*cmd)
    
    async def delete_remote_branch(self, branch_name, remote='origin'):
        """Delete a remote branch"""
        return await self._run_git_command('push', remote, '--delete', branch_name)
    
    async def rename_branch(self, old_name, new_name):
        """Rename a branch"""
        # If renaming current branch, use -m flag
        current_branch = await self.current_branch()
        if current_branch == old_name:
            return await self._run_git_command('branch', '-m', new_name)
        else:
            # For other branches, we need to create new branch and delete old one
            await self._run_git_command('checkout', old_name)
            await self._run_git_command('checkout', '-b', new_name)
            await self._run_git_command('checkout', current_branch)
            return await self._run_git_command('branch', '-d', old_name)
    
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
        except git.GitCommandError:
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
        """Get the current branch name"""
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
    
    # Tag Management
    async def list_tags(self):
        """List all tags"""
        return await self._run_git_command('tag', '-l')

    async def create_tag(self, name, message=None, annotated=False, commit=None):
        """Create a tag (annotated or lightweight)"""
        cmd = ['tag']
        if annotated or message:
            cmd.append('-a')
            cmd.append(name)
            if message:
                cmd.extend(['-m', message])
        else:
            cmd.append(name)
        if commit:
            cmd.append(commit)
        return await self._run_git_command(*cmd)

    async def delete_tag(self, name):
        """Delete a tag by name"""
        return await self._run_git_command('tag', '-d', name)

    async def show_tag_details(self, name):
        """Show details for a tag (annotated or lightweight)"""
        return await self._run_git_command('show', name)

    async def rebase_interactive(self, base):
        """Start an interactive rebase onto a base branch or commit"""
        return await self._run_git_command('rebase', '-i', base)

    async def squash(self, num, message=None):
        """Squash last N commits into one using reset --soft approach."""
        log = await self._run_git_command('rev-list', '--count', 'HEAD')
        commit_count = int(log.strip())
        if num >= commit_count:
            return f"Cannot squash {num} commits: only {commit_count} commits in branch."
        
        try:
            # Soft reset to move HEAD back N commits (keeps changes staged)
            await self._run_git_command('reset', '--soft', f'HEAD~{num}')
            
            # Create a new commit with the provided message or default
            if message:
                result = await self._run_git_command('commit', '-m', message)
            else:
                result = await self._run_git_command('commit', '-m', f'Squash {num} commits')
            
            return f"Successfully squashed last {num} commits into one."
        except Exception as e:
            return f"Error during squash: {e}"

    async def file_log(self, file_path, max_count=50):
        """Show commit log for a specific file"""
        result = await self._run_git_command('log', f'--max-count={max_count}', '--oneline', '--', file_path)
        return f"DEBUG: file_log result type: {type(result)}, value: {result}"

    async def show_commit(self, commit_hash):
        """Show full details for a specific commit"""
        return await self._run_git_command('show', commit_hash)

    # Repository Analytics & Statistics
    async def get_repository_stats(self):
        """Get comprehensive repository statistics"""
        stats = {}
        
        try:
            # Total commits
            total_commits = await self._run_git_command('rev-list', '--count', 'HEAD')
            stats['total_commits'] = int(total_commits.strip())
            
            # Total branches
            branches = await self._run_git_command('branch', '-a', '--format=%(refname:short)')
            stats['total_branches'] = len([b for b in branches.split('\n') if b.strip()])
            
            # Total tags
            tags = await self._run_git_command('tag', '-l')
            stats['total_tags'] = len([t for t in tags.split('\n') if t.strip()])
            
            # Repository size
            repo_size = await self._run_git_command('count-objects', '-vH')
            stats['repo_size'] = repo_size.strip()
            
            # File count
            file_count = await self._run_git_command('ls-files')
            stats['total_files'] = len([f for f in file_count.split('\n') if f.strip()])
            
            # Recent activity (last 30 days)
            recent_commits = await self._run_git_command('log', '--since=30 days ago', '--oneline')
            stats['recent_commits'] = len([c for c in recent_commits.split('\n') if c.strip()])
            
            # Contributors
            contributors = await self._run_git_command('shortlog', '-sn', '--no-merges')
            stats['contributors'] = len([c for c in contributors.split('\n') if c.strip()])
            
            # Current branch
            current_branch = await self.current_branch()
            stats['current_branch'] = current_branch.strip()
            
            # Last commit info
            last_commit = await self._run_git_command('log', '-1', '--format=%H|%an|%ae|%ad|%s')
            if last_commit.strip():
                parts = last_commit.strip().split('|')
                stats['last_commit'] = {
                    'hash': parts[0][:8],
                    'author': parts[1],
                    'email': parts[2],
                    'date': parts[3],
                    'message': parts[4]
                }
            
        except Exception as e:
            stats['error'] = str(e)
            
        return stats

    async def get_commit_activity(self, days=30):
        """Get commit activity over a period of time"""
        try:
            activity = await self._run_git_command('log', f'--since={days} days ago', 
                                                 '--format=%ad', '--date=short')
            dates = [d.strip() for d in activity.split('\n') if d.strip()]
            
            # Count commits per day
            from collections import Counter
            daily_counts = Counter(dates)
            
            return dict(daily_counts)
        except Exception as e:
            return {'error': str(e)}

    async def get_file_changes(self, days=30):
        """Get file change statistics"""
        try:
            # Get files changed in recent commits
            changed_files = await self._run_git_command('log', f'--since={days} days ago',
                                                      '--name-only', '--pretty=format:')
            files = [f.strip() for f in changed_files.split('\n') if f.strip()]
            
            # Count changes per file
            from collections import Counter
            file_counts = Counter(files)
            
            # Get file types
            file_types = {}
            for file_path in files:
                ext = Path(file_path).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            return {
                'most_changed_files': dict(file_counts.most_common(10)),
                'file_types': file_types,
                'total_files_changed': len(files)
            }
        except Exception as e:
            return {'error': str(e)}

    async def get_branch_activity(self):
        """Get branch activity and health metrics"""
        try:
            # Get all branches with last commit info
            branches = await self._run_git_command('for-each-ref', '--format=%(refname:short)|%(committerdate:iso)|%(subject)',
                                                 'refs/heads')
            
            branch_info = []
            for line in branches.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 3:
                        branch_info.append({
                            'name': parts[0],
                            'last_commit_date': parts[1],
                            'last_commit_message': parts[2]
                        })
            
            # Get current branch to use as reference
            current_branch = await self.current_branch()
            if current_branch:
                current_branch = current_branch.strip()
                
                # Get merged/unmerged branches relative to current branch
                try:
                    merged_branches = await self._run_git_command('branch', '--merged', current_branch)
                    unmerged_branches = await self._run_git_command('branch', '--no-merged', current_branch)
                except:
                    # Fallback to HEAD if current branch fails
                    merged_branches = await self._run_git_command('branch', '--merged', 'HEAD')
                    unmerged_branches = await self._run_git_command('branch', '--no-merged', 'HEAD')
            else:
                # Fallback to HEAD
                merged_branches = await self._run_git_command('branch', '--merged', 'HEAD')
                unmerged_branches = await self._run_git_command('branch', '--no-merged', 'HEAD')
            
            return {
                'branches': branch_info,
                'merged_branches': [b.strip() for b in merged_branches.split('\n') if b.strip()],
                'unmerged_branches': [b.strip() for b in unmerged_branches.split('\n') if b.strip()]
            }
        except Exception as e:
            return {'error': str(e)}

    async def get_contributor_stats(self):
        """Get contributor statistics and activity"""
        try:
            # Get contributor summary
            contributors = await self._run_git_command('shortlog', '-sn', '--no-merges')
            
            # Get detailed contributor info
            detailed_contributors = await self._run_git_command('shortlog', '-sn', '--no-merges', '--format=%H|%an|%ae|%ad|%s')
            
            contributor_details = []
            for line in detailed_contributors.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 5:
                        contributor_details.append({
                            'hash': parts[0][:8],
                            'author': parts[1],
                            'email': parts[2],
                            'date': parts[3],
                            'message': parts[4]
                        })
            
            return {
                'summary': contributors.strip(),
                'details': contributor_details
            }
        except Exception as e:
            return {'error': str(e)}

    async def get_repository_health(self):
        """Get repository health indicators"""
        try:
            health = {}
            
            # Check for merge commits
            merge_commits = await self._run_git_command('log', '--merges', '--oneline')
            health['merge_commits'] = len([c for c in merge_commits.split('\n') if c.strip()])
            
            # Check for orphaned branches (use current branch or HEAD)
            try:
                current_branch = await self.current_branch()
                if current_branch:
                    orphaned = await self._run_git_command('branch', '--no-merged', current_branch.strip())
                else:
                    orphaned = await self._run_git_command('branch', '--no-merged', 'HEAD')
            except:
                orphaned = await self._run_git_command('branch', '--no-merged', 'HEAD')
            health['orphaned_branches'] = len([b for b in orphaned.split('\n') if b.strip()])
            
            # Check repository size
            size_info = await self._run_git_command('count-objects', '-vH')
            health['size_info'] = size_info.strip()
            
            # Check for large files (simplified approach)
            try:
                # Get list of all objects
                objects = await self._run_git_command('rev-list', '--objects', '--all')
                health['total_objects'] = len([o for o in objects.split('\n') if o.strip()])
            except:
                health['total_objects'] = 'Unable to count'
            
            return health
        except Exception as e:
            return {'error': str(e)} 