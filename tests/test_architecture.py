"""Generated from docs/arch-rules.yaml — regenerate, don't hand-edit."""

import pathlib

from archunitpython import assert_passes, project_layers

PACKAGE_ROOT = pathlib.Path("src/test_saas")

# Declared modules, from arch-rules.yaml. Keep in sync when the YAML changes.
DECLARED_MODULES = {"identity", "settings", "token_verification", "api"}


def test_no_undeclared_modules() -> None:
    """Every package dir under src/test_saas/ must be a declared module —
    an undeclared module would otherwise pass with no import checks."""
    actual_modules = {
        path.name
        for path in PACKAGE_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(("_", "."))
    }
    assert actual_modules == DECLARED_MODULES, (
        f"module dirs {actual_modules} != declared {DECLARED_MODULES}"
    )


def _layers():
    # defined_by_folder matches the file's directory, not its full path, so
    # "**/<module>/**" alone misses files sitting directly in the module dir
    # (directory ".../<module>"). Each layer gets both patterns: one for
    # top-level files, one for nested subpackages.
    architecture = project_layers("src/")
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
