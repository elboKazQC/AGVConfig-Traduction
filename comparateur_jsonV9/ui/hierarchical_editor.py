# Éditeur hiérarchique pour l'application Fault Editor
"""
Ce module contient l'éditeur principal pour la vue hiérarchique des défauts.
Utilisez cette classe pour afficher et éditer les fichiers JSON hiérarchiques.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Optional, Union, Dict, Any, Callable, Tuple
from models.data_models import FileMetadata, SearchResult, FaultData, ApplicationState
from config.constants import Colors

# Configure logging
logger = logging.getLogger(__name__)

try:
    from ui.components import StyledFrame
except ImportError:
    # Fallback if components module doesn't exist
    class StyledFrame(tk.Frame):
        """Extended Frame class that's compatible with Frame type."""
        pass

try:
    from search.search_manager import HierarchicalSearcher as ImportedSearcher
except ImportError:
    ImportedSearcher = None

# Create a utility function for path_to_filename
def path_to_filename(path: List[int], lang: str = "fr") -> str:
    """Convert a path to a filename."""
    return f"faults_{'_'.join(str(p).zfill(3) for p in path)}_{lang}.json"

class SearchBarBuilder:
    """Builder for search bars."""

    def __init__(self, parent: tk.Widget):
        self.parent = parent

    def build(self) -> ttk.Frame:
        """Build and return search bar frame."""
        frame = ttk.Frame(self.parent)
        entry = ttk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        return frame

class HierarchicalSearcher:
    """Search functionality for hierarchical data."""

    def __init__(self, columns: List[Union[tk.Frame, ttk.Frame]]):
        """Initialize with a list of columns."""
        self.columns: List[Union[tk.Frame, ttk.Frame]] = columns
        self.current_results: List[SearchResult] = []
        self.highlight_callback: Optional[Callable[[SearchResult], None]] = None

    def highlight_result(self, column: Union[tk.Frame, ttk.Frame], row: Union[tk.Frame, ttk.Frame]) -> None:
        """Highlight a search result."""
        if hasattr(row, 'configure') and isinstance(row, tk.Frame):
            row.configure(bg=Colors.YELLOW)

    def clear_all_highlights(self) -> None:
        """Clear all highlights."""
        for column in self.columns:
            self._clear_column_highlights(column)

    def _clear_column_highlights(self, column: Union[tk.Frame, ttk.Frame]) -> None:
        """Clear highlights in a specific column."""
        for child in column.winfo_children():
            if hasattr(child, 'configure') and isinstance(child, tk.Frame):
                child.configure(bg=Colors.BG_ROW)

    def search_in_columns(self, query: str) -> List[SearchResult]:
        """Search for query in columns and return results."""
        results = []
        # Implement search logic here
        return results

class HierarchicalEditor:
    """Main hierarchical editor component."""

    def __init__(self, parent: tk.Widget, file_metadata: FileMetadata):
        """Initialize the hierarchical editor."""
        self.parent = parent
        self.file_metadata = file_metadata
        self.searcher: Optional[HierarchicalSearcher] = None
        self.on_item_select: Optional[Callable[[Any], None]] = None
        self.on_item_edit: Optional[Callable[[Any], None]] = None
        self.on_item_save: Optional[Callable[[Any], None]] = None

        # Set up ttk styles
        style = ttk.Style()
        style.configure('Editor.TFrame', background=Colors.BG_MAIN)
        style.configure('Column.TFrame', background=Colors.BG_COLUMN)
        style.configure('Row.TFrame', background=Colors.BG_ROW)

        # Add missing attributes
        self.app_state = ApplicationState()
        self.file_manager = None  # Will be set externally
        self.columns: List[ttk.Frame] = []
        self.main_canvas = tk.Canvas(parent, bg=Colors.BG_MAIN)  # Use tk.Canvas since ttk has no Canvas
        self.main_canvas.pack(fill="both", expand=True)        # Configure scroll region
        self.main_canvas.bind('<Configure>', self._on_frame_configure)

    def create_columns(self) -> List[ttk.Frame]:
        """Create and return column frames."""
        style = ttk.Style()
        style.configure('Column.TFrame', background=Colors.BG_COLUMN)

        columns = []
        for i in range(3):
            frame = ttk.Frame(self.parent, style='Column.TFrame')
            columns.append(frame)
        return columns

    def setup_searcher(self):
        """Setup the searcher with proper column types."""
        columns = self.create_columns()
        # Convert to Union type for searcher
        searcher_columns: List[Union[tk.Frame, ttk.Frame]] = columns
        self.searcher = HierarchicalSearcher(searcher_columns)

        def highlight_result(result: SearchResult):
            """Highlight a search result."""
            if self.searcher and hasattr(self.searcher, 'highlight_result'):
                # Convert result to frame references
                dummy_column = tk.Frame(self.parent)
                dummy_row = tk.Frame(dummy_column)
                self.searcher.highlight_result(dummy_column, dummy_row)

        if self.searcher:
            self.searcher.highlight_callback = highlight_result

    def search_and_highlight(self, query: str):
        """Search and highlight results."""
        if not self.searcher:
            self.setup_searcher()

        # Create sample results for iteration
        results = [            SearchResult(
                query=query,
                file_path="test.json",
                line_number=1,
                context="test",
                column_index=0,
                row_index=0,
                fault_data=FaultData(fault_code="TEST", description="test", severity="info", category="test"),
                match_text="test",
                file_metadata=FileMetadata(
                    filename="test.json",
                    filepath="test.json",
                    language="fr",  # Default language
                    path_components=[0],  # Default path component
                )
            ),
            SearchResult(
                query=query,
                file_path="test2.json",
                line_number=2,
                context="test2",
                column_index=0,
                row_index=1,
                fault_data=FaultData(fault_code="TEST2", description="test2", severity="info", category="test"),
                match_text="test2",
                file_metadata=FileMetadata(
                    filename="test2.json",
                    filepath="test2.json",
                    language="fr",  # Default language
                    path_components=[0],  # Default path component
                )
            )
        ]

        for result in results:
            if self.searcher and self.searcher.highlight_callback:
                self.searcher.highlight_callback(result)

    def clear_highlights(self):
        """Clear all highlights."""
        if self.searcher and hasattr(self.searcher, 'clear_all_highlights'):
            self.searcher.clear_all_highlights()

    def _ensure_result_visible(self, row: tk.Frame):
        """Ensure the result row is visible."""
        if hasattr(row, 'update_idletasks'):
            row.update_idletasks()

    def set_callbacks(self,
                     on_select: Optional[Callable[[Any], None]] = None,
                     on_edit: Optional[Callable[[Any], None]] = None,
                     on_save: Optional[Callable[[Any], None]] = None):
        """Set callback functions."""
        if on_select:
            self.on_item_select = on_select
        if on_edit:
            self.on_item_edit = on_edit
        if on_save:
            self.on_item_save = on_save

    def clear_columns_from(self, level: int):
        """Clear columns from a specific level onwards."""
        try:
            columns_to_remove = self.columns[level:]
            for col in columns_to_remove:
                col.destroy()
            self.columns = self.columns[:level]
            logger.info(f"Cleared columns from level {level}")
        except Exception as e:
            logger.error(f"Error clearing columns: {e}")

    def display_column(self, fault_list: List[Any], path: List[int], filename: str, level: int):
        """Display a column of fault data."""
        try:            # Create column frame
            style = ttk.Style()
            style.configure('Column.TFrame', background=Colors.BG_COLUMN)

            col_frame = ttk.Frame(self.parent, style='Column.TFrame')
            col_frame.pack(side="left", fill="both", expand=False)

            # Add to columns list
            if level >= len(self.columns):
                self.columns.extend([ttk.Frame(self.parent, style='Column.TFrame') for _ in range(level - len(self.columns) + 1)])
            self.columns[level] = col_frame

            # Display fault items
            for i, fault in enumerate(fault_list):
                if isinstance(fault, dict):
                    fault_data = FaultData(
                        fault_code=fault.get("FaultCode", ""),
                        description=fault.get("Description", ""),
                        severity=fault.get("Severity", "info"),
                        category=fault.get("Category", "general")
                    )
                else:
                    fault_data = FaultData(
                        fault_code=str(i),
                        description=str(fault),
                        severity="info",
                        category="general"
                    )

                # Create row widget
                row_frame = tk.Frame(col_frame, bg=Colors.BG_ROW)
                row_frame.pack(fill="x", pady=1)

                # Add fault display
                label = tk.Label(row_frame, text=fault_data.description,
                               bg=Colors.BG_ROW, fg=Colors.FG_TEXT)
                label.pack(side="left", fill="x", expand=True)

            logger.info(f"Displayed column with {len(fault_list)} items")

        except Exception as e:
            logger.error(f"Error displaying column: {e}")

    def _on_frame_configure(self, event):
        """Handle frame configuration changes."""
        if self.main_canvas:
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def load_next_level(self, fault_code: str, level: int):
        """Load the next level in the hierarchy."""
        try:
            # Create new path
            new_path = self.app_state.current_path[:level] + [int(fault_code)]

            # Create filename for the new level
            filename = path_to_filename(new_path, self.app_state.current_language)

            # Create file metadata
            file_metadata = FileMetadata(
                filename=filename,
                filepath=f"{self.app_state.base_directory}/{filename}",
                last_modified="now",
                file_size=0
            )

            # Load the file if file_manager is available
            if self.file_manager and hasattr(self.file_manager, 'load_file'):
                data = self.file_manager.load_file(filename)
                self.app_state.current_path = new_path

                # Display the new level
                fault_list = data.get("FaultDetailList", [])
                self.display_column(fault_list, new_path, filename, level + 1)

        except Exception as e:
            logger.error(f"Error loading next level: {e}")

    def setup_search_interface(self):
        """Setup the search interface."""
        try:
            search_builder = SearchBarBuilder(self.parent)
            search_frame = search_builder.build()
            search_frame.pack(fill="x", padx=5, pady=5)

            # Add to main canvas if available
            if self.main_canvas:
                self.main_canvas.create_window((0, 0), window=search_frame, anchor="nw")

        except Exception as e:
            logger.error(f"Error setting up search interface: {e}")

    def perform_search(self, query: str):
        """Perform a search operation."""
        try:
            if not self.searcher:
                self.setup_searcher()

            # Clear previous highlights
            if self.app_state and hasattr(self.app_state, 'current_language'):
                logger.info(f"Searching for: {query}")

            # Perform search
            if self.searcher and hasattr(self.searcher, 'search_in_columns'):
                results = self.searcher.search_in_columns(query)

                # Process results
                for result in results:
                    # Create fault data from result
                    fault_data = FaultData(
                        fault_code="SEARCH",
                        description=result.context,
                        severity="info",
                        category="search"
                    )

                    # Highlight if needed
                    if self.app_state:
                        logger.debug(f"Found result: {result.context}")

        except Exception as e:
            logger.error(f"Error performing search: {e}")

    def navigate_to_result(self, result: SearchResult):
        """Navigate to a specific search result."""
        try:
            # Parse file path to determine navigation path
            file_path = result.file_path

            # Update application state
            if self.app_state:
                self.app_state.selected_files = [file_path]

            # Navigate to the appropriate level
            # This would implement the logic to navigate to the specific result
            logger.info(f"Navigating to result: {result.file_path}:{result.line_number}")

        except Exception as e:
            logger.error(f"Error navigating to result: {e}")

    def highlight_search_result(self, column_index: int, row_index: int,
                              fault_data: FaultData, match_text: str,
                              file_metadata: FileMetadata):
        """Highlight a specific search result."""
        try:
            if column_index < len(self.columns) and self.columns[column_index]:
                column = self.columns[column_index]

                # Find the row widget
                children = column.winfo_children()
                if row_index < len(children):
                    row = children[row_index]
                    if hasattr(row, 'configure'):
                        row.configure(bg=Colors.YELLOW)                    # Ensure result is visible
                    if self.main_canvas and hasattr(row, 'winfo_y'):
                        # Get relative position of row and scroll to it
                        y_position = row.winfo_y()
                        canvas_height = self.main_canvas.winfo_height()
                        if canvas_height > 0:  # Avoid division by zero
                            # Convert to relative position (0.0 to 1.0)
                            relative_position = max(0.0, min(1.0, y_position / canvas_height))
                            self.main_canvas.yview_moveto(relative_position)

        except Exception as e:
            logger.error(f"Error highlighting search result: {e}")

    def scroll_to_result(self, result: SearchResult):
        """Scroll to make a search result visible."""
        try:
            if self.main_canvas:
                # Calculate position based on result
                y_position = result.line_number * 25  # Approximate row height

                # Scroll to position
                canvas_height = self.main_canvas.winfo_height()
                total_height = self.main_canvas.bbox("all")[3] if self.main_canvas.bbox("all") else canvas_height

                if total_height > canvas_height:
                    fraction = y_position / total_height
                    self.main_canvas.yview_moveto(fraction)

        except Exception as e:
            logger.error(f"Error scrolling to result: {e}")

    def clear_search_highlights(self):
        """Clear all search highlights."""
        try:
            if self.app_state and hasattr(self.app_state, 'current_language'):
                logger.info("Clearing search highlights")

            if self.searcher and hasattr(self.searcher, 'clear_all_highlights'):
                self.searcher.clear_all_highlights()

        except Exception as e:
            logger.error(f"Error clearing search highlights: {e}")

    def save_current_state(self):
        """Save the current editor state."""
        try:
            if self.app_state:
                self.app_state.last_modified = __import__('datetime').datetime.now()
                logger.info("Current state saved")

        except Exception as e:
            logger.error(f"Error saving current state: {e}")

    def restore_state(self, state: ApplicationState):
        """Restore editor state from saved state."""
        try:
            self.app_state = state

            # Restore file manager if available
            if self.file_manager and hasattr(self.file_manager, 'set_base_directory'):
                if state.base_directory:
                    self.file_manager.set_base_directory(state.base_directory)

            # Restore columns for current path
            if state.current_path and len(state.current_path) > 0:
                # Rebuild columns for the saved path
                for level in range(len(state.current_path)):
                    if state.current_path[level] != 255:  # Valid level
                        path = state.current_path[:level+1]
                        filename = path_to_filename(path, state.current_language)

                        # Load and display if file manager is available
                        if self.file_manager and hasattr(self.file_manager, 'load_file'):
                            try:
                                data = self.file_manager.load_file(filename)
                                fault_list = data.get("FaultDetailList", [])
                                self.display_column(fault_list, path, filename, level)
                            except Exception:
                                logger.warning(f"Could not restore level {level}")
                                break

            logger.info("State restored successfully")

        except Exception as e:
            logger.error(f"Error restoring state: {e}")
