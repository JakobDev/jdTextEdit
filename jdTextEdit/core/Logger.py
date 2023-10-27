from typing import Literal
import platform
import logging
import os


_globalLogger: logging.Logger | None = None


class _COLORS:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


class _VerboseLogger(logging.Logger):
    def __init__(self, isVerbose: bool) -> None:
        super().__init__("jdTextEditGlobal")

        self._isVerbose = isVerbose

    def verboseDebug(self, msg: str) -> None:
        if self._isVerbose:
            self.debug(msg, stacklevel=2)

    def verboseInfo(self, msg: str) -> None:
        if self._isVerbose:
            self.info(msg, stacklevel=2)

    def verboseWarning(self, msg: str) -> None:
        if self._isVerbose:
            self.warning(msg, stacklevel=2)

    def verboseError(self, msg: str) -> None:
        if self._isVerbose:
            self.error(msg, stacklevel=2)

    def verboseException(self, ex: Exception) -> None:
        if self._isVerbose:
            self.exception(ex, stacklevel=2)


class _ColorFormatter(logging.Formatter):
    def __init__(self, debug: bool) -> None:
        if debug:
            debug_format= f" {_COLORS.BLUE}%(filename)s:%(lineno)d{_COLORS.END}"
        else:
            debug_format = ""

        self._info_formatter = logging.Formatter(f"[{_COLORS.GREEN}%(levelname)s{_COLORS.END}{debug_format}]%(message)s")
        self._warning_formatter = logging.Formatter(f"[{_COLORS.YELLOW}%(levelname)s{_COLORS.END}{debug_format}]%(message)s")
        self._error_formatter = logging.Formatter(f"[{_COLORS.RED}%(levelname)s{_COLORS.END}{debug_format}]%(message)s")
        self._fallback_formatter = logging.Formatter(f"[%(levelname)s{debug_format}]%(message)s")

    def format(self, record: logging.LogRecord) -> str:
        match record.levelno:
            case logging.DEBUG | logging.INFO:
                return self._info_formatter.format(record)
            case logging.WARNING:
                return self._warning_formatter.format(record)
            case logging.ERROR | logging.CRITICAL:
                return self._error_formatter.format(record)
            case _:
                return self._fallback_formatter.format(record)


def setupLogger(debug: bool, logFormat: Literal["default", "no-color", "unformatted"], verbose: bool, logFile: str | None) -> logging.Logger:
    if platform.system() == "Windows" and logFormat == "default":
        # We need to call this to enable ANSI Colors on Windows - https://stackoverflow.com/questions/16755142/how-to-make-win32-console-recognize-ansi-vt100-escape-sequences-in-c
        os.system("")

    global _globalLogger
    _globalLogger = _VerboseLogger(verbose)

    consoleHandler = logging.StreamHandler()

    match logFormat:
        case "default":
            consoleHandler.setFormatter(_ColorFormatter(debug))
        case "no-color":
            if debug:
                consoleHandler.setFormatter(logging.Formatter(f"[%(levelname)s %(filename)s:%(lineno)d]%(message)s"))
            else:
                consoleHandler.setFormatter(logging.Formatter(f"[%(levelname)s]%(message)s"))
        case "unformatted":
            consoleHandler.setFormatter(logging.Formatter(f"%(message)s"))

    if debug or verbose:
        consoleHandler.setLevel(logging.DEBUG)
    else:
        consoleHandler.setLevel(logging.INFO)

    _globalLogger.addHandler(consoleHandler)

    if logFile:
        fileHandler = logging.FileHandler(logFile, "w", encoding="utf-8")

        if debug:
            fileHandler.setFormatter(logging.Formatter(f"[%(levelname)s %(filename)s:%(lineno)d]%(message)s"))
        else:
            fileHandler.setFormatter(logging.Formatter(f"[%(levelname)s]%(message)s"))

        _globalLogger.addHandler(fileHandler)


def getGlobalLogger() -> _VerboseLogger:
    if _globalLogger is None:
        raise Exception("Logger is not initialized")

    return _globalLogger
