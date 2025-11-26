from byte.core.exceptions import ByteConfigException


class WebNotEnabledException(ByteConfigException):
    """Raised when attempting to use web commands while web features are disabled.

    Web commands require a Chrome/Chromium binary and must be enabled in settings.
    Usage: `raise WebNotEnabledException()` -> informs user to enable web in config
    """

    def __init__(self):
        super().__init__(
            "Web commands are not enabled. "
            "Please enable web commands in your .byte/config.yaml settings file. "
            "Set 'web.enable' to true and ensure 'web.chrome_binary_location' points to a valid Chrome/Chromium binary. "
            "See docs/reference/settings.md for more information."
        )
