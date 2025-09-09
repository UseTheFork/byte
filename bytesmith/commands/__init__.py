import importlib
import pkgutil

# Auto-import all command modules
for importer, modname, ispkg in pkgutil.iter_modules(__path__):
    if modname not in ['registry', 'processor']:  # Skip utility modules
        importlib.import_module(f"{__name__}.{modname}")
