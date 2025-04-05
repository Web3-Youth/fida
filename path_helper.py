import os
from rich.console import Console
from rich.prompt import Prompt, IntPrompt

console = Console()

class PathHelper:
    @staticmethod
    def get_current_directory():
        """Get the current working directory."""
        return os.getcwd()

    @staticmethod
    def list_directories(path="."):
        """List all directories in the given path."""
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    @staticmethod
    def select_directory():
        """Interactive directory selection."""
        current_dir = PathHelper.get_current_directory()
        console.print(f"\n[bold cyan]Current Directory:[/bold cyan] {current_dir}")
        
        while True:
            console.print("\n[bold yellow]Available Options:[/bold yellow]")
            console.print("1. Use current directory")
            console.print("2. List subdirectories")
            console.print("3. Enter custom path")
            console.print("4. Go up one level")
            
            choice = IntPrompt.ask("\n[cyan]Select an option[/cyan]", choices=["1", "2", "3", "4"])
            
            if choice == 1:
                return current_dir
            elif choice == 2:
                dirs = PathHelper.list_directories(current_dir)
                if not dirs:
                    console.print("[yellow]No subdirectories found.[/yellow]")
                    continue
                
                console.print("\n[bold cyan]Subdirectories:[/bold cyan]")
                for i, dir_name in enumerate(dirs, 1):
                    console.print(f"{i}. {dir_name}")
                
                dir_choice = IntPrompt.ask("\n[cyan]Select a directory (or 0 to go back)[/cyan]", 
                                         choices=[str(i) for i in range(len(dirs) + 1)])
                
                if dir_choice == 0:
                    continue
                current_dir = os.path.join(current_dir, dirs[dir_choice - 1])
            elif choice == 3:
                custom_path = Prompt.ask("\n[cyan]Enter the full path[/cyan]")
                if os.path.exists(custom_path):
                    current_dir = custom_path
                else:
                    console.print("[red]Path does not exist![/red]")
            elif choice == 4:
                parent_dir = os.path.dirname(current_dir)
                if parent_dir != current_dir:
                    current_dir = parent_dir
                else:
                    console.print("[yellow]Already at root directory.[/yellow]") 