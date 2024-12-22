class Cmd:
    def __init__(
        self,
        help_text,
        execute,
        help_link=None,
        params_required=0,
        voice_required=False,
        creator_only=False,
        admin_required=False,
    ):
        self.help_text = help_text
        self.help_link = help_link
        self.execute = execute
        self.params_required = params_required
        self.voice_required = voice_required
        self.creator_only = creator_only
        self.admin_required = admin_required

    def print_help(self):
        return True, self.help_text
