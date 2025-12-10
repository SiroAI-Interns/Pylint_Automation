"""Pylintrc generator module for Autoencoder."""
from pathlib import Path

from .config import Config


class PylintrcGenerator:
    """Generates a .pylintrc file based on configuration."""

    def __init__(self, config: Config):
        """Initialize the generator with configuration."""
        self.config = config

    def generate(self) -> Path:
        """Generate the .pylintrc file and return its path."""
        pylintrc_content = self._build_content()
        pylintrc_path = self.config.codebase_path / ".pylintrc"

        # If codebase_path is a directory, put .pylintrc in parent
        if self.config.codebase_path.is_dir():
            pylintrc_path = self.config.codebase_path.parent / ".pylintrc"

        with open(pylintrc_path, "w", encoding="utf-8") as f:
            f.write(pylintrc_content)

        return pylintrc_path

    def _build_content(self) -> str:
        """Build the .pylintrc content."""
        config = self.config

        return f'''[MAIN]
# Autoencoder Generated Pylintrc
# Naming Convention: {config.naming_convention}

analyse-fallback-blocks=no
clear-cache-post-run=no
extension-pkg-allow-list=
fail-under=10
ignore=CVS
ignore-paths=
ignore-patterns=^\\.#
jobs=1
limit-inference-results=100
persistent=yes
py-version=3.11
recursive=no
unsafe-load-any-extension=no

[BASIC]
# Naming conventions based on: {config.naming_convention}

# Variable names (STRICT camelCase)
variable-rgx={config.get_variable_regex()}

# Argument names (STRICT camelCase)
argument-rgx={config.get_argument_regex()}

# Attribute names (STRICT camelCase)
attr-rgx={config.get_attr_regex()}

# Function names - Accept ANY naming style (disabled check)
function-rgx=.+

# Method names - Accept ANY naming style (disabled check)
method-rgx=.+

# Class attribute names
class-attribute-rgx={config.get_class_attribute_regex()}

# Constant names
const-rgx={config.get_const_regex()}

# Class names (always PascalCase)
class-rgx={config.get_class_regex()}

[CLASSES]
check-protected-access-in-special-methods=no
defining-attr-methods=__init__,__new__,setUp,asyncSetUp,__post_init__
exclude-protected=_asdict,_fields,_replace,_source,_make,os._exit
valid-classmethod-first-arg=cls
valid-metaclass-classmethod-first-arg=mcs

[DESIGN]
max-args=10
max-attributes=15
max-bool-expr=5
max-branches=15
max-locals=25
max-parents=7
max-positional-arguments=10
max-public-methods=30
max-returns=10
max-statements=60
min-public-methods=0

[FORMAT]
expected-line-ending-format=
ignore-long-lines=^\\s*(# )?<?https?://\\S+>?$
indent-after-paren=4
indent-string='    '
max-line-length={config.max_line_length}
max-module-lines=2000
single-line-class-stmt=no
single-line-if-stmt=no

[IMPORTS]
allow-any-import-level=
allow-reexport-from-package=no
allow-wildcard-with-all=no

[MESSAGES CONTROL]
confidence=HIGH,CONTROL_FLOW,INFERENCE,INFERENCE_FAILURE,UNDEFINED

disable=raw-checker-failed,
        bad-inline-option,
        locally-disabled,
        file-ignored,
        suppressed-message,
        useless-suppression,
        deprecated-pragma,
        use-symbolic-message-instead,
        use-implicit-booleaness-not-comparison-to-string,
        use-implicit-booleaness-not-comparison-to-zero,
        import-error,
        duplicate-code,
        missing-module-docstring,
        missing-class-docstring,
        missing-function-docstring,
        too-many-locals,
        too-many-arguments,
        too-many-positional-arguments,
        too-many-instance-attributes,
        too-few-public-methods,
        too-many-return-statements,
        too-many-branches,
        too-many-statements,
        broad-exception-caught,
        logging-fstring-interpolation,
        redefined-outer-name,
        f-string-without-interpolation,
        line-too-long,
        unused-argument,
        unused-variable,
        wrong-import-order,
        wrong-import-position,
        ungrouped-imports,
        import-outside-toplevel,
        reimported,
        no-else-return,
        consider-using-enumerate,
        multiple-statements,
        pointless-string-statement,
        pointless-statement,
        comparison-with-itself,
        protected-access,
        dangerous-default-value,
        attribute-defined-outside-init,
        access-member-before-definition,
        raise-missing-from,
        deprecated-argument,
        c-extension-no-member,
        too-many-boolean-expressions,
        no-self-argument,
        unsubscriptable-object,
        no-member,
        not-an-iterable,
        undefined-variable,
        self-cls-assignment,
        astroid-error,
        invalid-name,
        no-name-in-module,
        unexpected-keyword-arg,
        function-redefined,
        cell-var-from-loop,
        inconsistent-return-statements,
        no-value-for-parameter,
        missing-kwoa,
        expression-not-assigned

[REPORTS]
evaluation=max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10))
reports=no
score=yes

[SIMILARITIES]
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=yes
ignore-signatures=yes
min-similarity-lines=4

[VARIABLES]
allow-global-unused-variables=yes
callbacks=cb_,_cb
dummy-variables-rgx=_+$|(_[a-zA-Z0-9_]*[a-zA-Z0-9]+?$)|dummy|^ignored_|^unused_
ignored-argument-names=_.*|^ignored_|^unused_
init-import=no
'''

