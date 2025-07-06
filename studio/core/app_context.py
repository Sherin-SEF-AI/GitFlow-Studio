import asyncio
import threading
from pathlib import Path
from studio.core.plugin_loader import PluginLoader
from studio.db.sqlite_manager import SQLiteManager
from studio.utils.repo_discovery import discover_git_repos

class AppContext:
    def __init__(self):
        self.plugin_loader = PluginLoader()
        self.db_manager = SQLiteManager()
        self.repositories = []
        self.current_repo = None
        self.event_loop = None
        self.background_tasks = []
        
    async def initialize(self):
        """Initialize the application context"""
        await self.db_manager.init_db()
        self.plugin_loader.discover_plugins()
        self.plugin_loader.load_plugins(self)
        
    def add_repository(self, repo_path):
        """Add a repository to the managed list"""
        if repo_path not in self.repositories:
            self.repositories.append(repo_path)
            
    def set_current_repository(self, repo_path):
        """Set the currently active repository"""
        self.current_repo = repo_path
        
    def get_repositories(self):
        """Get all managed repositories"""
        return self.repositories
        
    def run_background_task(self, task):
        """Run a task in the background"""
        if self.event_loop:
            asyncio.create_task(task)
        else:
            thread = threading.Thread(target=lambda: asyncio.run(task))
            thread.daemon = True
            thread.start()
            self.background_tasks.append(thread)
            
    def cleanup(self):
        """Clean up resources before shutdown"""
        try:
            # Stop background tasks
            for task in self.background_tasks:
                if task.is_alive():
                    task.join(timeout=1.0)
                    
            # Close event loop if running
            if self.event_loop and not self.event_loop.is_closed():
                self.event_loop.close()
                
        except Exception as e:
            import logging
            logging.error(f"Error during cleanup: {e}") 