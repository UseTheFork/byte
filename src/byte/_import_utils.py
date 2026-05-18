from importlib import import_module

# Credits to https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/_import_utils.py


def import_attr(
    attr_name: str,
    module_name: str | None,
    package: str | None,
) -> object:
    """Import an attribute from a module located in a package.

    This utility function is used in custom __getattr__ methods within __init__.py
    files to dynamically import attributes.

    Args:
        attr_name: The name of the attribute to import.
        module_name: The name of the module to import from. If `None`, the attribute
            is imported from the package itself.
        package: The name of the package where the module is located.

    Raises:
        ImportError: If the module cannot be found.
        AttributeError: If the attribute does not exist in the module or package.

    Returns:
        The imported attribute.
    """
    if module_name == "__module__" or module_name is None:
        try:
            result = import_module(f".{attr_name}", package=package)
        except ModuleNotFoundError as err:
            target = f"{package}.{attr_name}"
            if err.name and err.name == target:
                msg = f"module '{package}' has no attribute '{attr_name}'"
            else:
                msg = f"Failed to import '{attr_name}' from '{package}': transitive import error — {err}"
            raise AttributeError(msg) from None

    else:
        try:
            module = import_module(f".{module_name}", package=package)
        except ModuleNotFoundError as err:
            target = f"{package}.{module_name}"
            # If the missing module IS the one we tried to import, it's a direct failure.
            # Otherwise it's a transitive dependency that failed during import.
            if err.name and err.name == target:
                msg = f"module '{target}' not found"
            else:
                msg = f"Failed to import '{attr_name}' from '{target}': transitive import error — {err}"
            raise ImportError(msg) from None
        result = getattr(module, attr_name)
    return result
