from byte.core.exceptions import ByteConfigException


class LintConfigException(ByteConfigException):
    """Raised when lint configuration is invalid or incomplete.

    This exception is raised when linting cannot proceed due to configuration
    issues such as linting being disabled or no commands configured.
    Usage: `raise LintConfigException("Linting is disabled")` -> inform user of config issue
    """

    pass
