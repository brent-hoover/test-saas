"""Generated from docs/arch-rules.yaml — regenerate, don't hand-edit."""

import pathlib

from archunitpython import assert_passes, project_layers

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parents[1] / "src" / "test_saas"

# Declared modules, from arch-rules.yaml. Keep in sync when the YAML changes.
DECLARED_MODULES = {"identity", "settings", "token_verification", "api"}


NON_SOURCE_ENTRIES = {"__init__.py", "__pycache__"}


def test_no_undeclared_modules() -> None:
    """Every source entry under src/test_saas/ must be a declared module
    directory.

    Packages (including `_private` ones) and standalone `.py` files both
    count, compared by their raw name: archunitpython layers are defined by
    folder, so a file such as `identity.py` is assigned no layer and its
    edges are skipped. Requiring the exact directory name keeps every import
    under a rule below."""
    actual_entries = {
        path.name
        for path in PACKAGE_ROOT.iterdir()
        if path.name not in NON_SOURCE_ENTRIES and not path.name.startswith(".")
    }
    assert actual_entries == DECLARED_MODULES, (
        f"source entries {actual_entries} != declared module dirs {DECLARED_MODULES}"
    )
    assert all((PACKAGE_ROOT / name).is_dir() for name in DECLARED_MODULES)


def _layers():
    # archunitpython 1.8.1: defined_by_folder matches the file's directory, not its full path, so
    # "**/<module>/**" alone misses files sitting directly in the module dir
    # (directory ".../<module>"). Each layer gets both patterns: one for
    # top-level files, one for nested subpackages.
    architecture = project_layers(f"{PACKAGE_ROOT.parent}/")
    for module_name in sorted(DECLARED_MODULES):
        architecture = architecture.layer(module_name).defined_by_folder(
            f"**/{module_name}"
        )
        architecture = architecture.layer(module_name).defined_by_folder(
            f"**/{module_name}/**"
        )
    return architecture


def test_identity_imports_no_sibling_modules() -> None:
    assert_passes(_layers().where_layer("identity").may_only_depend_on_layers())


def test_settings_imports_no_sibling_modules() -> None:
    assert_passes(_layers().where_layer("settings").may_only_depend_on_layers())


def test_token_verification_may_import_only_settings() -> None:
    assert_passes(
        _layers()
        .where_layer("token_verification")
        .may_only_depend_on_layers("settings")
    )


def test_api_may_import_only_identity_settings_token_verification() -> None:
    assert_passes(
        _layers()
        .where_layer("api")
        .may_only_depend_on_layers("identity", "settings", "token_verification")
    )
