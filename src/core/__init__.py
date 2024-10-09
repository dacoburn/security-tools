import logging
log = logging.getLogger("socket-external-tool")
log.addHandler(logging.NullHandler())


__all__ = [
    "marker",
    "__version__",
    "__author__",
    "log",
    "base_github"
]

__version__ = "0.0.1"
__author__ = "socket.dev"
base_github = "https://github.com"

marker = f"<!--Socket External Tool Runner: REPLACE_ME -->"
#
#
# class Core:
#     @staticmethod
#     def set_log_level(level: int):
#         handler = logging.StreamHandler()
#         # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#         # handler.setFormatter(formatter)
#         global log
#         log.addHandler(handler)
#         log.setLevel(level)
