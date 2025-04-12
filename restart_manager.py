import threading
from typing import Dict, Callable, List, Optional
import time

class RestartManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RestartManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._modules: Dict[str, Callable] = {}
        self._restart_lock = threading.Lock()
        self._restart_thread: Optional[threading.Thread] = None
        self._initialized = True
        
    def register_module(self, module_name: str, restart_func: Callable) -> None:
        """Register a module with its restart function."""
        self._modules[module_name] = restart_func
        
    def restart_modules(self, module_names: List[str] = None) -> None:
        """
        Restart specified modules or all modules if none specified.
        This is non-blocking and will start a new thread to handle the restarts.
        """
        # If no specific modules are provided, restart all registered modules
        if module_names is None:
            module_names = list(self._modules.keys())
            
        # Don't start a new restart if one is already in progress
        with self._restart_lock:
            if self._restart_thread and self._restart_thread.is_alive():
                print("A restart is already in progress. Please wait.")
                return
                
            self._restart_thread = threading.Thread(
                target=self._restart_modules_thread,
                args=(module_names,)
            )
            self._restart_thread.start()
    
    def _restart_modules_thread(self, module_names: List[str]) -> None:
        """Thread function to restart modules."""
        with self._restart_lock:
            for module_name in module_names:
                if module_name in self._modules:
                    print(f"Restarting module: {module_name}")
                    try:
                        self._modules[module_name]()
                        # Small delay between module restarts
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error restarting module {module_name}: {e}")
                else:
                    print(f"Unknown module: {module_name}")