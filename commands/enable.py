import utils
from commands.base import Cmd
from utils import logger

help_text = [
    [
        ("Usage:", "<PREFIX><COMMAND>"),
        (
            "Description:",
            "Turn me on. If I'm not enabled, I won't create any new voice channels, rename, or delete them.",
        ),
    ]
]


async def execute(ctx, params):
    settings = ctx["settings"]
    guild = ctx["guild"]
    if settings["enabled"]:
        return False, "Already enabled. Use '{}disable' to turn off.".format(ctx["print_prefix"])
    else:
        logger(guild).info("Enabling")
        settings["enabled"] = True
        utils.set_serv_settings(guild, settings)
        return True, "Enabling auto voice channels. Turn off with '{}disable'.".format(ctx["print_prefix"])


command = Cmd(
    execute=execute,
    help_text=help_text,
    params_required=0,
    admin_required=True,
)
