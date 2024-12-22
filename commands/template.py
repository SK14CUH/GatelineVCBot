import functions as func
from commands.base import Cmd

help_text = [
    [
        ("Usage:", "<PREFIX><COMMAND> `TEMPLATE`"),
        (
            "Description:",
            "Change the name template for secondary channels using dynamic variables. "
            "The default is `## [@@game_name@@]`.\n\n"
            "First join a voice channel, then run the command to set the template for that channel and all other "
            'secondary channels created by the same primary ("+ New Session") channel.',
        ),
    ],
    [
        ("title", "You can use the following variables:"),
        (
            " ·  `##`",
            "The channel number with a `#` in front. The first channel created will be '#1', the next '#2', etc. "
            "If the people from the first channel leave and it's deleted, channel #2 will be renamed to #1.",
        ),
        (
            " ·  `$#`",
            "The channel number just like `##`, but without a `#` in front. e.g. '1', '2', '3' "
            "instead of '#1', '#2', '#3'.",
        ),
        (" ·  `$0#`, `$00#`, `$000#`, etc.", "Just like `$#` above but with padded zeros (e.g. '001', '002', etc.)."),
        (" ·  `+#`", "The channel number just like `##`, but with roman number. e.g. 'I', 'II', 'V' "),
        (
            " ·  `@@game_name@@`",
            "replaced with the game that most people in the channel are playing, "
            'or "General" if no one is playing anything/there is too much variety. '
            'Use `<PREFIX>general` to use a different word than "General".',
        ),
        (
            " ·  `@@creator@@`",
            "The person who first joined the channel. "
            "If they leave, the person at the top of the channel (alphabetically) becomes the creator.",
        ),
        (
            " ·  `@@stream_name@@`",
            "If the creator is streaming to Twitch and have their Twitch account connected to Discord (purple status), "
            "this is replaced with their stream name. If they are not streaming, it's simply removed.",
        ),
        (" ·  `@@num@@`", "The number of users in the channel."),
        (" ·  `@@num_others@@`", "The number of users in the channel excluding the creator."),
        (
            " ·  `<<singular/plural>>`",
            "Use the singular word if `@@num@@` is 1, or plural word if it's not 1.\n"
            "Use a back-slash (`\\`) instead of a forward-slash if you want it to use "
            "`@@num_others@@` instead of `@@num@@`.",
        ),
        (
            ' ·  `""operation:Text to manipulate""`',
            "Basic string manipulation - supported operations are:\n"
            '  ·  `""caps: Text""` ⇾ `TEXT`\n'
            '  ·  `""lower: Text""` ⇾ `text`\n'
            '  ·  `""title: text""` ⇾ `Text`\n'
            '  ·  `""swap: Text""` ⇾ `tEXT`\n'
            '  ·  `""rand: Hmmmmmmm""` ⇾ `hmMmMmMM`\n'
            '  ·  `""acro: Text to Manipulate""` ⇾ `TtM`\n'
            '  ·  `""remshort: Text to Manipulate""` ⇾ `Text Manipulate`\n'
            '  ·  `""1w: Text to Manipulate""` ⇾ `Text`\n'
            '  ·  `""2w: Text to Manipulate""` ⇾ `Text to`\n'
            '  ·  `""3w: Text to Manipulate""` ⇾ `Text to Manipulate`\n'
            '  ·  `""spaces:   Text   to   Manipulate ""` ⇾ `Text to Manipulate`\n'
            '  ·  `""uwu: Surprise!""` ⇾ `Suwpwise!`\n'
            "Multiple operations can be used at once by adding `+` between them. E.g:\n"
            '`""remshort+3w+acro+caps: It\'s a small world after all""` ⇾ `ISW`\n'
            "You can use any other template variables inside the text, E.g:\n"
            '`""3w+caps: @@game_name@@""` ⇾ `WORLD OF WARCRAFT`\n'
            '`""acro: @@game_name@@""` ⇾ `WoW`',
        ),
        (" ·  `@@nato@@`", "Use the NATO Phonetic Alphabet (Alpha, Bravo, Charlie...) as the channel number."),
        (
            " ·  `[[random/word or phrase/selection]]`",
            "Pick a random word or phrase between the slashes when the channel is created. Use a back-slash (`\\`) "
            "instead of a forward-slash if you want it to select a random word every few minutes instead of only "
            "when the channel is created.",
        ),
        (
            " ·  `{{EXPRESSION ?? TRUE // FALSE}}`",
            "Advanced nestable conditional expressions. Use `<PREFIX>help expressions` for more info.",
        ),
        (
            " ·  `@@num_playing@@`",
            "The number of users playing in the same game session. Uses the game's Rich Presence info if it's available, "
            "otherwise it makes a guess from the game activity of users in the voice chat.",
        ),
        (
            " ·  `@@party_size@@`",
            "The maximum number of players allowed in the game. Uses the game's Rich Presence info if it's available, "
            "otherwise it uses the channel's user limit. Defaults to `0` if no size is found. "
            "You may want to use the `{{RICH}}` expression to check if the current game uses Rich Presence.",
        ),
        (
            " ·  `@@party_details@@`",
            "The party details provided by Rich Presence if it's available, varies by game, "
            "usually the game mode, difficulty and/or mission name.\n"
            "Use `<PREFIX>channelinfo` to check your current party details.",
        ),
        (
            " ·  `@@party_state@@`",
            "The party state information provided by Rich Presence if it's available, varies by game, "
            "may be character played, team info, game mode, etc.\n"
            "Use `<PREFIX>channelinfo` to check your current party state.",
        ),
    ],
    [
        ("title", "Examples:"),
        (" ·  `<PREFIX><COMMAND> ## [@@game_name@@]`", '"#1 [Skyrim]", "#2 [Apex Legends]"\n'),
        (" ·  `<PREFIX><COMMAND> @@num@@ blind <<mouse/mice>>`", '"1 blind mouse", "3 blind mice"\n'),
        (
            " ·  `<PREFIX><COMMAND> @@creator@@ and the @@num_others@@ <<Dwarf\\Dwarves>>`",
            '"Snow White and the 7 Dwarves", "pewdiepie and the 1 Dwarf"',
        ),
        (" ·  `<PREFIX><COMMAND> @@nato@@ [[Squad/Team/Party/Noobs]]`", '"Alpha Team", "Charlie Squad"\n'),
        (
            " ·  `<PREFIX><COMMAND> @@game_name@@ {{GAME:Left 4 Dead ?? [@@num_playing@@/4]}}`",
            '"Left 4 Dead 2 [3/4]", "PUBG"\n',
        ),
        (
            " ·  `<PREFIX><COMMAND> @@game_name@@ {{ROLE:601025860614750229 ?? {{ROLE:615086491235909643??[UK] // "
            "{{ROLE:607913610139664444??[DE] // [EU]}}}}}}`",
            '"PUBG [UK]", "PUBG [EU]"',
        ),
    ],
]


async def execute(ctx, params):
    params_str = ctx["clean_paramstr"]
    guild = ctx["guild"]
    vc = ctx["voice_channel"]
    template = params_str.replace("\n", " ")  # Can't have newlines in channel name.
    template = template.strip()
    if template:
        func.set_template(guild, vc.id, template)
        return True, (
            "Done! From now on, voice channels like the one you're in now will be named "
            "according to your template. You should see it update in a few seconds."
        )
    else:
        return False, (
            "You need to specify a new name template for this channel, e.g. '{0}template <new name>'.\n"
            "Run '{0}help template' for a full list of variables you can use like "
            "`@@game_name@@`, `@@creator@@` and `@@num_others@@`.\n"
            "The default is `## [@@game_name@@]`.".format(ctx["print_prefix"])
        )


command = Cmd(
    execute=execute,
    help_text=help_text,
    params_required=1,
    admin_required=True,
    voice_required=True,
)
