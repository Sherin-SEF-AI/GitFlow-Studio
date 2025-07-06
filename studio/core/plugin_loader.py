import importlib
import sys
from pathlib import Path

class PluginLoader:
    def __init__(self, plugins_path=None):
        if plugins_path is None:
            plugins_path = Path(__file__).parent.parent / 'plugins'
        self.plugins_path = Path(plugins_path)
        self.plugins = []

    def discover_plugins(self):
        sys.path.insert(0, str(self.plugins_path))
        for file in self.plugins_path.glob('*.py'):
            if file.name.startswith('_') or not file.name.endswith('.py'):
                continue
            module_name = file.stem
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'register'):
                    self.plugins.append(module)
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")
        sys.path.pop(0)

    def load_plugins(self, app_context):
        for plugin in self.plugins:
            try:
                plugin.register(app_context)
            except Exception as e:
                print(f"Failed to register plugin {plugin.__name__}: {e}") 