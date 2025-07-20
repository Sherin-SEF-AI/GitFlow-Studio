"""
Theme customization system for GitFlow Studio
Allows users to personalize the interface with different color schemes and styles
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.theme import Theme
from rich.style import Style

console = Console()

class ThemeManager:
    """Manages themes for GitFlow Studio interface"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.themes_file = Path(self.config_dir) / "themes.json"
        self.current_theme = "default"
        self.themes: Dict[str, Dict[str, Any]] = {}
        self._ensure_config_dir()
        self._load_themes()
        self._load_default_themes()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_themes(self):
        """Load themes from JSON file"""
        try:
            if self.themes_file.exists():
                with open(self.themes_file, 'r') as f:
                    data = json.load(f)
                    self.themes = data.get("themes", {})
                    self.current_theme = data.get("current_theme", "default")
            else:
                self.themes = {}
                self._save_themes()
        except Exception as e:
            console.print(f"[red]Error loading themes: {e}[/]")
            self.themes = {}
    
    def _save_themes(self):
        """Save themes to JSON file"""
        try:
            data = {
                "themes": self.themes,
                "current_theme": self.current_theme
            }
            with open(self.themes_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving themes: {e}[/]")
    
    def _load_default_themes(self):
        """Load built-in default themes"""
        default_themes = {
            "default": {
                "name": "Default",
                "description": "Default GitFlow Studio theme",
                "colors": {
                    "primary": "cyan",
                    "secondary": "yellow",
                    "success": "green",
                    "error": "red",
                    "warning": "yellow",
                    "info": "blue",
                    "text": "white",
                    "dim": "dim white",
                    "border": "blue",
                    "header": "bold magenta",
                    "highlight": "bold cyan"
                },
                "styles": {
                    "banner_border": "cyan",
                    "panel_border": "blue",
                    "table_header": "bold magenta",
                    "table_border": "blue",
                    "progress_bar": "cyan",
                    "spinner": "cyan"
                }
            },
            "dark": {
                "name": "Dark Theme",
                "description": "Dark theme for low-light environments",
                "colors": {
                    "primary": "bright_cyan",
                    "secondary": "bright_yellow",
                    "success": "bright_green",
                    "error": "bright_red",
                    "warning": "bright_yellow",
                    "info": "bright_blue",
                    "text": "bright_white",
                    "dim": "dim white",
                    "border": "bright_blue",
                    "header": "bold bright_magenta",
                    "highlight": "bold bright_cyan"
                },
                "styles": {
                    "banner_border": "bright_cyan",
                    "panel_border": "bright_blue",
                    "table_header": "bold bright_magenta",
                    "table_border": "bright_blue",
                    "progress_bar": "bright_cyan",
                    "spinner": "bright_cyan"
                }
            },
            "light": {
                "name": "Light Theme",
                "description": "Light theme for bright environments",
                "colors": {
                    "primary": "blue",
                    "secondary": "magenta",
                    "success": "green",
                    "error": "red",
                    "warning": "yellow",
                    "info": "cyan",
                    "text": "black",
                    "dim": "dim black",
                    "border": "blue",
                    "header": "bold blue",
                    "highlight": "bold blue"
                },
                "styles": {
                    "banner_border": "blue",
                    "panel_border": "blue",
                    "table_header": "bold blue",
                    "table_border": "blue",
                    "progress_bar": "blue",
                    "spinner": "blue"
                }
            },
            "ocean": {
                "name": "Ocean Blue",
                "description": "Ocean-inspired blue theme",
                "colors": {
                    "primary": "bright_blue",
                    "secondary": "cyan",
                    "success": "bright_green",
                    "error": "bright_red",
                    "warning": "yellow",
                    "info": "bright_cyan",
                    "text": "white",
                    "dim": "dim white",
                    "border": "bright_blue",
                    "header": "bold bright_blue",
                    "highlight": "bold cyan"
                },
                "styles": {
                    "banner_border": "bright_blue",
                    "panel_border": "bright_blue",
                    "table_header": "bold bright_blue",
                    "table_border": "bright_blue",
                    "progress_bar": "bright_blue",
                    "spinner": "bright_blue"
                }
            },
            "forest": {
                "name": "Forest Green",
                "description": "Nature-inspired green theme",
                "colors": {
                    "primary": "bright_green",
                    "secondary": "green",
                    "success": "bright_green",
                    "error": "bright_red",
                    "warning": "yellow",
                    "info": "cyan",
                    "text": "white",
                    "dim": "dim white",
                    "border": "green",
                    "header": "bold bright_green",
                    "highlight": "bold green"
                },
                "styles": {
                    "banner_border": "bright_green",
                    "panel_border": "green",
                    "table_header": "bold bright_green",
                    "table_border": "green",
                    "progress_bar": "bright_green",
                    "spinner": "bright_green"
                }
            },
            "sunset": {
                "name": "Sunset Orange",
                "description": "Warm sunset-inspired theme",
                "colors": {
                    "primary": "bright_yellow",
                    "secondary": "bright_red",
                    "success": "bright_green",
                    "error": "bright_red",
                    "warning": "yellow",
                    "info": "cyan",
                    "text": "white",
                    "dim": "dim white",
                    "border": "bright_yellow",
                    "header": "bold bright_yellow",
                    "highlight": "bold bright_red"
                },
                "styles": {
                    "banner_border": "bright_yellow",
                    "panel_border": "bright_yellow",
                    "table_header": "bold bright_yellow",
                    "table_border": "bright_yellow",
                    "progress_bar": "bright_yellow",
                    "spinner": "bright_yellow"
                }
            }
        }
        
        # Only add default themes if they don't exist
        for theme_id, theme_data in default_themes.items():
            if theme_id not in self.themes:
                self.themes[theme_id] = theme_data
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Get the current theme configuration"""
        return self.themes.get(self.current_theme, self.themes.get("default", {}))
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name not in self.themes:
            console.print(f"[red]Theme '{theme_name}' not found![/]")
            return False
        
        self.current_theme = theme_name
        self._save_themes()
        console.print(f"[green]✅ Theme changed to '{theme_name}'[/]")
        return True
    
    def list_themes(self, show_current: bool = True):
        """List all available themes"""
        if not self.themes:
            console.print(Panel("[yellow]No themes found.[/]", 
                              title="[blue]Themes", border_style="blue"))
            return
        
        table = Table(
            title="[bold blue]Available Themes[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Theme", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("Description", style="green")
        table.add_column("Status", style="yellow")
        
        for theme_id, theme_data in self.themes.items():
            name = theme_data.get("name", theme_id)
            description = theme_data.get("description", "")
            status = "✓ Current" if theme_id == self.current_theme else ""
            
            table.add_row(theme_id, name, description, status)
        
        console.print(table)
    
    def create_theme(self, name: str, description: str = "", colors: Dict[str, str] = None, 
                    styles: Dict[str, str] = None) -> bool:
        """Create a new custom theme"""
        if not name:
            console.print("[red]Theme name is required![/]")
            return False
        
        if name in self.themes:
            console.print(f"[yellow]Theme '{name}' already exists![/]")
            return False
        
        # Start with default theme as base
        base_theme = self.themes.get("default", {}).copy()
        
        self.themes[name] = {
            "name": name.title(),
            "description": description,
            "colors": {**base_theme.get("colors", {}), **(colors or {})},
            "styles": {**base_theme.get("styles", {}), **(styles or {})}
        }
        
        self._save_themes()
        console.print(f"[green]✅ Theme '{name}' created successfully![/]")
        return True
    
    def delete_theme(self, name: str) -> bool:
        """Delete a custom theme"""
        if name in ["default", "dark", "light"]:
            console.print(f"[red]Cannot delete built-in theme '{name}'![/]")
            return False
        
        if name not in self.themes:
            console.print(f"[red]Theme '{name}' not found![/]")
            return False
        
        del self.themes[name]
        
        # If we deleted the current theme, switch to default
        if name == self.current_theme:
            self.current_theme = "default"
        
        self._save_themes()
        console.print(f"[green]✅ Theme '{name}' deleted successfully![/]")
        return True
    
    def export_theme(self, theme_name: str, file_path: Optional[str] = None) -> bool:
        """Export a theme to JSON file"""
        if theme_name not in self.themes:
            console.print(f"[red]Theme '{theme_name}' not found![/]")
            return False
        
        if not file_path:
            file_path = f"{theme_name}_theme.json"
        
        try:
            theme_data = self.themes[theme_name]
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=2)
            
            console.print(f"[green]✅ Theme exported to {file_path}[/]")
            return True
        except Exception as e:
            console.print(f"[red]Error exporting theme: {e}[/]")
            return False
    
    def import_theme(self, file_path: str, theme_name: Optional[str] = None) -> bool:
        """Import a theme from JSON file"""
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
            
            if not theme_name:
                theme_name = theme_data.get("name", Path(file_path).stem).lower()
            
            self.themes[theme_name] = theme_data
            self._save_themes()
            console.print(f"[green]✅ Theme '{theme_name}' imported successfully![/]")
            return True
        except Exception as e:
            console.print(f"[red]Error importing theme: {e}[/]")
            return False
    
    def get_rich_theme(self) -> Theme:
        """Get Rich theme object for console styling"""
        current_theme = self.get_current_theme()
        colors = current_theme.get("colors", {})
        
        theme_dict = {}
        for key, value in colors.items():
            theme_dict[f"theme.{key}"] = value
        
        return Theme(theme_dict)
    
    def preview_theme(self, theme_name: str):
        """Preview a theme with sample output"""
        if theme_name not in self.themes:
            console.print(f"[red]Theme '{theme_name}' not found![/]")
            return
        
        # Temporarily set theme
        original_theme = self.current_theme
        self.current_theme = theme_name
        
        theme_data = self.themes[theme_name]
        
        console.print(Panel(
            f"[bold]Theme Preview: {theme_data.get('name', theme_name)}[/]\n"
            f"[dim]{theme_data.get('description', '')}[/]\n\n"
            f"[theme.primary]Primary Color[/]\n"
            f"[theme.secondary]Secondary Color[/]\n"
            f"[theme.success]Success Color[/]\n"
            f"[theme.error]Error Color[/]\n"
            f"[theme.warning]Warning Color[/]\n"
            f"[theme.info]Info Color[/]",
            title="[theme.header]Theme Preview[/]",
            border_style="theme.border"
        ))
        
        # Restore original theme
        self.current_theme = original_theme
    
    def get_theme_stats(self) -> Dict[str, Any]:
        """Get statistics about themes"""
        total_themes = len(self.themes)
        built_in_themes = len([t for t in self.themes.keys() if t in ["default", "dark", "light", "ocean", "forest", "sunset"]])
        custom_themes = total_themes - built_in_themes
        
        return {
            "total_themes": total_themes,
            "built_in_themes": built_in_themes,
            "custom_themes": custom_themes,
            "current_theme": self.current_theme,
            "available_themes": list(self.themes.keys())
        } 