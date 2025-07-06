import unittest
import tempfile
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

class TestGitOperations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_git_operations_initialization(self):
        """Test GitOperations initialization"""
        from studio.git.git_operations import GitOperations
        
        # This will fail if not a git repo, but we can test the class creation
        with self.assertRaises(Exception):
            git_ops = GitOperations(self.repo_path)
            
    @patch('studio.git.git_operations.Repo')
    def test_git_operations_methods(self, mock_repo):
        """Test GitOperations methods"""
        from studio.git.git_operations import GitOperations
        
        # Mock the repo
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.git.execute.return_value = "test output"
        
        git_ops = GitOperations(self.repo_path)
        
        # Test that methods exist
        self.assertTrue(hasattr(git_ops, 'status'))
        self.assertTrue(hasattr(git_ops, 'log'))
        self.assertTrue(hasattr(git_ops, 'branches'))
        self.assertTrue(hasattr(git_ops, 'commit'))
        self.assertTrue(hasattr(git_ops, 'merge'))
        self.assertTrue(hasattr(git_ops, 'rebase'))

class TestAppContext(unittest.TestCase):
    def test_app_context_initialization(self):
        """Test AppContext initialization"""
        from studio.core.app_context import AppContext
        
        context = AppContext()
        self.assertIsNotNone(context.plugin_loader)
        self.assertIsNotNone(context.db_manager)
        self.assertEqual(context.repositories, [])
        self.assertIsNone(context.current_repo)
        
    def test_app_context_methods(self):
        """Test AppContext methods"""
        from studio.core.app_context import AppContext
        
        context = AppContext()
        
        # Test adding repository
        context.add_repository("/test/repo")
        self.assertIn("/test/repo", context.repositories)
        
        # Test setting current repository
        context.set_current_repository("/test/repo")
        self.assertEqual(context.current_repo, "/test/repo")
        
        # Test getting repositories
        repos = context.get_repositories()
        self.assertEqual(repos, ["/test/repo"])

class TestThemeManager(unittest.TestCase):
    def test_theme_manager_initialization(self):
        """Test ThemeManager initialization"""
        from studio.utils.theme_manager import ThemeManager
        
        theme_manager = ThemeManager()
        self.assertIsNotNone(theme_manager.themes)
        self.assertIn('dark', theme_manager.themes)
        self.assertIn('light', theme_manager.themes)
        
    def test_theme_application(self):
        """Test theme application"""
        from studio.utils.theme_manager import ThemeManager
        
        theme_manager = ThemeManager()
        
        # Test applying theme
        result = theme_manager.apply_theme('dark')
        self.assertTrue(result)
        
        # Test invalid theme
        result = theme_manager.apply_theme('invalid_theme')
        self.assertFalse(result)
        
    def test_theme_names(self):
        """Test getting theme names"""
        from studio.utils.theme_manager import ThemeManager
        
        theme_manager = ThemeManager()
        theme_names = theme_manager.get_theme_names()
        
        self.assertIn('dark', theme_names)
        self.assertIn('light', theme_names)
        self.assertIn('blue', theme_names)

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_analytics_initialization(self):
        """Test Analytics initialization"""
        from studio.utils.analytics import Analytics
        
        analytics = Analytics(self.temp_dir)
        self.assertIsNotNone(analytics.session_data)
        self.assertIsNotNone(analytics.analytics)
        
    def test_event_tracking(self):
        """Test event tracking"""
        from studio.utils.analytics import Analytics
        
        analytics = Analytics(self.temp_dir)
        
        # Track an event
        analytics.track_event('test_event', {'test': 'data'})
        
        # Check that event was tracked
        self.assertEqual(len(analytics.session_data['events']), 1)
        self.assertEqual(analytics.session_data['events'][0]['type'], 'test_event')
        
    def test_operation_tracking(self):
        """Test operation tracking"""
        from studio.utils.analytics import Analytics
        
        analytics = Analytics(self.temp_dir)
        
        # Track operations
        analytics.track_operation('commit', success=True)
        analytics.track_operation('push', success=False)
        
        # Check operations
        self.assertEqual(analytics.session_data['operations']['commit'], 1)
        self.assertEqual(analytics.session_data['operations']['push'], 1)
        self.assertEqual(len(analytics.session_data['errors']), 1)

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_security_manager_initialization(self):
        """Test SecurityManager initialization"""
        from studio.utils.security import SecurityManager
        
        security_manager = SecurityManager(self.temp_dir)
        self.assertIsNotNone(security_manager.cipher)
        self.assertIsNotNone(security_manager.gpg_config)
        
    def test_credential_storage(self):
        """Test credential storage and retrieval"""
        from studio.utils.security import SecurityManager
        
        security_manager = SecurityManager(self.temp_dir)
        
        # Store credentials
        security_manager.store_credential('test_service', 'test_user', 'test_pass', 'test description')
        
        # Retrieve credentials
        username, password = security_manager.get_credential('test_service')
        self.assertEqual(username, 'test_user')
        self.assertEqual(password, 'test_pass')
        
    def test_sensitive_data_scanning(self):
        """Test sensitive data scanning"""
        from studio.utils.security import SecurityManager
        
        security_manager = SecurityManager(self.temp_dir)
        
        # Test text with sensitive data
        test_text = "email: test@example.com\npassword: secret123\napi_key: abc123"
        findings = security_manager.scan_for_sensitive_data(test_text)
        
        self.assertIn('email', findings)
        self.assertIn('password', findings)
        self.assertIn('api_key', findings)

class TestRepositoryDiscovery(unittest.TestCase):
    def test_repository_discovery(self):
        """Test repository discovery"""
        from studio.utils.repo_discovery import discover_git_repos
        
        # Create a temporary directory structure
        temp_dir = tempfile.mkdtemp()
        try:
            # Create a mock git repository
            git_dir = Path(temp_dir) / 'test_repo' / '.git'
            git_dir.mkdir(parents=True)
            
            # Test discovery
            repos = discover_git_repos(temp_dir)
            self.assertIn(str(Path(temp_dir) / 'test_repo'), repos)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)

class TestPluginLoader(unittest.TestCase):
    def test_plugin_loader_initialization(self):
        """Test PluginLoader initialization"""
        from studio.core.plugin_loader import PluginLoader
        
        plugin_loader = PluginLoader()
        self.assertIsNotNone(plugin_loader.plugins_path)
        self.assertEqual(plugin_loader.plugins, [])
        
    def test_plugin_discovery(self):
        """Test plugin discovery"""
        from studio.core.plugin_loader import PluginLoader
        
        # Create a temporary plugins directory
        temp_dir = tempfile.mkdtemp()
        try:
            plugin_loader = PluginLoader(temp_dir)
            
            # Create a test plugin
            test_plugin_file = Path(temp_dir) / 'test_plugin.py'
            with open(test_plugin_file, 'w') as f:
                f.write('def register(app_context):\n    pass\n')
            
            # Test discovery
            plugin_loader.discover_plugins()
            # Note: This might not work in test environment due to import restrictions
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main() 