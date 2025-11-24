import ast
import json
import importlib.util
from typing import Callable, Dict, Any, Tuple
import types
import os
import sys

class MethodNotInSourceError(Exception):
    pass

class MethodExtractionError(Exception):
    pass

class MethodRegistry:
    """
    A registry that dynamically loads methods from Python source files without
    using traditional imports. It embraces the complexity of creating valid
    class instances to ensure methods have their full context.
    """
    def __init__(self, source_truth_path: str = "method_source_truth.json", source_truth: Dict[str, Any] | None = None):
        if source_truth:
            self._source_truth = source_truth
        else:
            try:
                with open(source_truth_path, "r") as f:
                    self._source_truth = json.load(f)
            except FileNotFoundError:
                raise MethodExtractionError(f"Source truth file not found at '{source_truth_path}' and no source_truth dictionary was provided. Please run the validator first.")
            
        self._module_cache: Dict[str, types.ModuleType] = {}
        self._lazy_registry: set = set()

    def register_lazy(self, method_fqn: str):
        """Pre-registers a method as being available for lazy loading."""
        self._lazy_registry.add(method_fqn)

    def _load_module_from_file(self, file_path: str) -> types.ModuleType:
        """
        Loads a Python source file as a module in an isolated namespace.
        Caches the result to avoid reprocessing the same file.
        This method temporarily adds the 'src' directory to sys.path
        to ensure that intra-package imports within the loaded file resolve correctly.
        """
        if file_path in self._module_cache:
            return self._module_cache[file_path]

        # The project has a src layout, so we need to add 'src' to the path
        # for imports like 'from saaaaaa.core...' to work.
        src_path = os.path.abspath("src")
        original_sys_path = sys.path[:]
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            # Create a unique module name to avoid conflicts.
            # The name should correspond to its path from the src root.
            module_name = os.path.splitext(os.path.relpath(file_path, src_path))[0].replace(os.sep, '.')

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise MethodExtractionError(f"Could not create spec for dynamic module from file {file_path}")

            module = importlib.util.module_from_spec(spec)

            # Add the module to sys.modules BEFORE exec_module. This is crucial
            # for allowing the module to import other modules within itself.
            sys.modules[module_name] = module

            spec.loader.exec_module(module)

            self._module_cache[file_path] = module
            return module
        except Exception as e:
            raise MethodExtractionError(f"Failed to dynamically load module from '{file_path}': {e}")
        finally:
            # Restore the original sys.path
            sys.path[:] = original_sys_path
            # Clean up the loaded module from sys.modules if it was added
            if 'module_name' in locals() and module_name in sys.modules:
                del sys.modules[module_name]


    def get_method(
        self, 
        class_name: str, 
        method_name: str, 
        init_args: Tuple = (), 
        init_kwargs: Dict[str, Any] = {}
    ) -> Callable:
        """
        Retrieves a method by dynamically loading its source file, instantiating
        its class, and returning the bound method.

        Args:
            class_name: The name of the class containing the method.
            method_name: The name of the method to retrieve.
            init_args: Positional arguments for the class's __init__.
            init_kwargs: Keyword arguments for the class's __init__.

        Returns:
            A callable, bound method from a fresh instance of the class.
        """
        fqn = f"{class_name}.{method_name}"

        if fqn not in self._source_truth:
            raise MethodNotInSourceError(f"{fqn} does NOT exist in any Python file according to the source truth map.")
        
        # In a strict system, we might enforce pre-registration.
        # if fqn not in self._lazy_registry:
        #     raise MethodExtractionError(f"{fqn} was not pre-registered for lazy loading.")

        source_info = self._source_truth[fqn]
        file_path = source_info['file']
        
        # 1. Get the module, loading it from source if necessary.
        module = self._load_module_from_file(file_path)
        
        # 2. Get the class from the dynamically loaded module.
        TargetClass = getattr(module, class_name, None)
        if not TargetClass:
            raise MethodExtractionError(f"Class '{class_name}' not found in dynamically loaded module '{file_path}'.")
            
        # 3. Instantiate the class with the provided arguments.
        # This is the crucial step that handles __init__ complexity.
        try:
            instance = TargetClass(*init_args, **init_kwargs)
        except Exception as e:
            raise MethodExtractionError(
                f"Failed to instantiate class '{class_name}' with the provided arguments. "
                f"Error: {e}. Ensure you are passing the correct arguments for its __init__ method."
            )
            
        # 4. Get the method from the instance.
        method = getattr(instance, method_name, None)
        if not method or not callable(method):
            raise MethodExtractionError(f"Attribute '{method_name}' on class '{class_name}' is not a callable method.")
            
        return method


if __name__ == '__main__':
    # This test assumes a specific structure and will need to be adapted
    # to the actual project files. It demonstrates the principle.
    
    print("Running a test of the new, robust MethodRegistry...")
    
    # We need a method from a class with a simple __init__ for this test to pass.
    # Let's assume 'BayesianNumericalAnalyzer' has a no-arg __init__.
    # The previous error indicates this might not be the case.
    
    # Let's try to load 'BayesianNumericalAnalyzer.compare_policies' again.
    # This time, we are prepared for __init__ failures.
    
    TEST_CLASS = "BayesianNumericalAnalyzer"
    TEST_METHOD = "compare_policies"
    
    try:
        registry = MethodRegistry()
        registry.register_lazy(f"{TEST_CLASS}.{TEST_METHOD}")
        
        print(f"Attempting to load '{TEST_CLASS}.{TEST_METHOD}' with no init_args...")
        
        # Let's assume a no-arg init for the test. If it fails, the error will be informative.
        method_to_test = registry.get_method(TEST_CLASS, TEST_METHOD)
        
        print(f"Successfully loaded method: {method_to_test}")
        # To prove it works, let's inspect it.
        # A bound method has __self__ pointing to the instance.
        if hasattr(method_to_test, '__self__'):
            print(f"Method is bound to instance: {method_to_test.__self__}")
            print("MethodRegistry test passed for a known method.")
        else:
            print("Test failed: Method does not appear to be bound.")

    except (MethodNotInSourceError, MethodExtractionError) as e:
        print(f"Test failed with an expected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")

    print("\n---")
    print("Testing a method from a class that requires __init__ arguments (hypothetical)...")
    
    # Let's pretend a class 'ClassWithInit' needs an argument.
    # We would need to update the source truth map for this test.
    # For now, we just demonstrate the failure mode.
    try:
        # Create a dummy source truth for this test
        if not os.path.exists("dummy_source_truth.json"):
            with open("dummy_source_truth.json", "w") as f:
                json.dump({
                    "ClassWithInit.some_method": {"file": "dummy_file.py"}
                }, f)
        if not os.path.exists("dummy_file.py"):
            with open("dummy_file.py", "w") as f:
                f.write("class ClassWithInit:\n")
                f.write("  def __init__(self, required_arg):\n")
                f.write("    self.arg = required_arg\n")
                f.write("  def some_method(self):\n")
                f.write("    return self.arg\n")

        registry = MethodRegistry(source_truth_path="dummy_source_truth.json")
        print("Attempting to get method from ClassWithInit without providing required arg...")
        registry.get_method("ClassWithInit", "some_method")

    except MethodExtractionError as e:
        print(f"Successfully caught expected error for missing __init__ args: {e}")
        print("Test for complex __init__ passed.")
    finally:
        # Clean up dummy files
        if os.path.exists("dummy_source_truth.json"):
            os.remove("dummy_source_truth.json")
        if os.path.exists("dummy_file.py"):
            os.remove("dummy_file.py")