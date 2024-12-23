import json
import os
import sys
import traceback
from datetime import datetime, date

import cfg
import discord
import functions as func
import psutil
import pytz
import utils
from functions import echo
from utils import logger


async def admin_command(cmd, ctx):
    client = ctx["client"]
    message = ctx["message"]
    channel = message.channel
    params = ctx["params"]
    params_str = ctx["params_str"]
    guilds = ctx["guilds"]
    LAST_COMMIT = ctx["LAST_COMMIT"]

    if cmd == "log":
        logfile = "log.txt"
        if not os.path.exists(logfile):
            await channel.send("No log file")
            return
        with open(logfile, "r", encoding="utf8") as f:
            data = f.read()
        data = data[-10000:]  # Drop everything but the last 10k characters to make string ops quicker
        data = data.replace("  Creating channel for ", "  ✅")
        data = data.replace("  Deleting ", "    ❌")
        data = data.replace("  Renaming ⌛  to  ", " ⏩ ")
        data = data.replace("  Renaming ", " 🔄")
        data = data.replace("  to  ", " ⏩ ")
        data = data.replace("  CMD Y: ", "  C✔ ")
        data = data.replace("  CMD F: ", "  C✖ ")
        data = data.replace(" creating channels too quickly", " creating channels too quickly❗❗")
        data = data.replace(" where I don't have permissions", " where I don't have permissions❗❗")
        data = data.replace("Traceback (most recent", "❗❗Traceback (most recent")
        data = data.replace("discord.errors.", "❗❗discord.errors.")
        data = data.replace("Remembering channel ", "❗❗Remembering ")
        data = data.replace("New tickrate is ", "🕐")
        data = data.replace(", seed interval is ", " 🕐")
        data = data.replace("  ", " ")  # Reduce indent to save character space
        today = datetime.now(pytz.timezone(cfg.CONFIG["log_timezone"])).strftime("%Y-%m-%d")
        data = data.replace(today, "T")
        character_limit = 2000 - 17  # 17 for length of ```autohotkey\n at start and ``` at end.
        data = data[character_limit * -1 :]
        data = data.split("\n", 1)[1]
        lines = data.split("\n")
        for i, l in enumerate(lines):
            # Fake colon (U+02D0) to prevent highlighting the line
            if " ⏩" in l:
                lines[i] = l.replace(":", "ː")
            elif l.startswith("T "):
                if "[" in l:
                    s = l.split("[", 1)
                    lines[i] = s[0] + "[" + s[1].replace(":", "ː")
        data = "\n".join(lines)
        data = "```autohotkey\n" + data
        data = data + "```"
        await channel.send(data)

    if cmd == "stats":
        r = await channel.send(". . .")
        t1 = message.created_at
        t2 = r.created_at
        response_time = (t2 - t1).total_seconds()
        num_users = 0
        for g in guilds:
            num_users += len([m for m in g.members if not m.bot])

        lines_of_code = 0
        for f in os.listdir(cfg.SCRIPT_DIR):
            if f.lower().endswith(".py"):
                lines_of_code += utils.count_lines(os.path.join(cfg.SCRIPT_DIR, f))
            elif f == "commands":
                for sf in os.listdir(os.path.join(cfg.SCRIPT_DIR, f)):
                    if sf.lower().endswith(".py"):
                        lines_of_code += utils.count_lines(os.path.join(cfg.SCRIPT_DIR, f, sf))

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        await r.edit(
            content=(
                "Servers: **{tot_servs}** (A:{active_servs} S:{shards}) \t "
                "Users: **{users}** \t Channels: **{channels}** \n"
                "Response time: **{rt}** \t Tick rate: **{tr}** \t Tick time: **{tt}** | **{gtt}**\n"
                "CPU: **{cpu}%** \t MEM: **{memg} ({memp}%)** \t DISK: **{diskg} ({diskp}%)**\n"
                "**Last commit:** {commit}\n"
                "**Lines of code:** {lines}\n"
                "**Timings:** \n{timings}".format(
                    tot_servs=len(guilds),
                    active_servs=utils.num_active_guilds(guilds),
                    shards=utils.num_shards(guilds),
                    users=num_users,
                    channels=utils.num_active_channels(guilds),
                    rt="{0:.2f}s".format(response_time),
                    tr="{0:.1f}s".format(cfg.TICK_RATE),
                    tt="{0:.2f}s".format(cfg.TICK_TIME),
                    gtt="{0:.2f}s".format(cfg.G_TICK_TIME),
                    cpu=cpu,
                    memg="{0:.1f}GB".format(mem.used / 1024 / 1024 / 1024),
                    memp=round(mem.percent),
                    diskg="{0:.1f}GB".format(disk.used / 1024 / 1024 / 1024),
                    diskp=round(disk.percent),
                    commit=LAST_COMMIT,
                    lines=lines_of_code,
                    timings=utils.format_timings(),
                )
            )
        )

    if cmd == "ping":
        r = await channel.send(". . .")
        t1 = message.created_at
        t2 = r.created_at
        response_time = (t2 - t1).total_seconds()
        e = "🔴🔴🔴" if response_time > 5 else ("🟠🟠" if response_time > 1 else "🟢")
        await r.edit(content="**{0} {1:.1f}s**".format(e, response_time))

    if cmd == "top":
        top_guilds = []
        total_users = 0
        mode = utils.strip_quotes(params_str)
        for g in client.guilds:
            num_users = len([m for m in g.members if not m.bot])
            total_users += num_users
            s = func.get_secondaries(g)
            top_guilds.append(
                {"name": g.name, "size": num_users, "num": len(s) if s is not None else 0, "in_guilds": g in guilds}
            )
        if mode in ["users", "members"]:
            top_guilds = sorted(top_guilds, key=lambda x: x["size"], reverse=True)[:10]
        else:
            top_guilds = sorted(top_guilds, key=lambda x: x["num"], reverse=True)[:10]
        r = "**Top Guilds:**"
        for g in top_guilds:
            r += "\n{}`{}` {}: \t**{}**".format(
                "" if g["in_guilds"] else "⚠", g["size"], func.esc_md(g["name"]), g["num"]
            )
        r += "\n\n**{}** channels, **{}** users".format(utils.num_active_channels(guilds), total_users)
        await channel.send(r)

    if cmd == "status":
        g = utils.strip_quotes(params_str)
        if not g:
            await func.react(message, "❌")
            return
        try:
            await client.change_presence(activity=discord.Activity(name=g, type=discord.ActivityType.watching))
            await func.react(message, "✅")
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "settings":
        gid = utils.strip_quotes(params_str)
        try:
            int(gid)
        except ValueError:
            for x in guilds:
                if x.name == gid:
                    gid = str(x.id)
                    break
        fname = gid + ".json"
        fp = os.path.join(cfg.SCRIPT_DIR, "guilds", fname)
        if os.path.exists(fp):
            gid = int(gid)
            g = client.get_guild(gid)
            head = "**{}** `{}`{}".format(g.name, gid, ("✅" if g in func.get_guilds(client) else "❌"))
            s = head
            s += "\n```json\n"
            with open(fp, "r") as f:
                file_content = f.read()
            s += file_content
            s += "```"
            try:
                await channel.send(s)
            except discord.errors.HTTPException:
                # Usually because message is over character limit
                haste_url = await utils.hastebin(file_content)
                await channel.send("{}\n{}".format(head, haste_url))
        else:
            await func.react(message, "❌")

    if cmd == "refetch":
        gid = utils.strip_quotes(params_str)
        try:
            gid = int(gid)
        except ValueError:
            await func.react(message, "❌")
            return

        g = client.get_guild(gid)

        if g is None:
            await func.react(message, "❓")
            return

        utils.get_serv_settings(g, force_refetch=True)
        await func.react(message, "✅")
        return

    if cmd == "disable":
        try:
            g = client.get_guild(int(utils.strip_quotes(params_str)))
            settings = utils.get_serv_settings(g)
            settings["enabled"] = False
            utils.set_serv_settings(g, settings)
            logger(g).info("Force Disabling")
            await func.react(message, "✅")
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "enable":
        try:
            g = client.get_guild(int(utils.strip_quotes(params_str)))
            settings = utils.get_serv_settings(g)
            settings["enabled"] = True
            utils.set_serv_settings(g, settings)
            logger(g).info("Force Enabling")
            await func.react(message, "✅")
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "info":
        cid = utils.strip_quotes(params_str)
        try:
            c = client.get_channel(int(cid))
            members = [m.display_name + " \t {}".format(utils.debug_unicode(m.display_name)) for m in c.members]
            games = []
            for m in c.members:
                if m.activity:
                    games.append(m.activity.name + " \t {}".format(utils.debug_unicode(m.activity.name)))
            s = "**__Server:__** {} `{}`\n**__Name:__** {}\n{}\n\n".format(
                c.guild.name, c.guild.id, c.name, utils.debug_unicode(c.name)
            )
            if c.id in cfg.ATTEMPTED_CHANNEL_NAMES:
                s += "**__Attempted Name:__** {}\n{}\n\n".format(
                    cfg.ATTEMPTED_CHANNEL_NAMES[c.id], utils.debug_unicode(cfg.ATTEMPTED_CHANNEL_NAMES[c.id])
                )
            s += "**__{} Members:__**\n".format(len(members))
            s += "\n".join(members)
            s += "\n\n**__{} Games:__**\n".format(len(games))
            s += "\n".join(games)
            s = s.replace("\n\n\n", "\n\n")
            await channel.send(s)
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "whois":
        uid = utils.strip_quotes(params_str)
        try:
            u = client.get_user(int(uid))
            s = ""

            in_guilds = {}
            for g in client.guilds:
                if u in g.members:
                    m = g.get_member(int(uid))
                    in_guilds[g.id] = {
                        "guild_name": func.esc_md(g.name),
                        "guild_size": g.member_count,
                        "user_name": func.esc_md(m.display_name),
                        "role": m.top_role.name,
                    }
            if in_guilds:
                s += "**{}**".format(func.user_hash(u))
                s += " \t :b: :regional_indicator_o: :regional_indicator_t:" if u.bot else ""
                can_dm = True
                try:
                    await u.create_dm()
                    can_dm = client.user.permissions_in(u.dm_channel).send_messages
                except discord.errors.Forbidden:
                    can_dm = False
                s += " \t Can DM: {}".format("✅" if can_dm else "❌")

                for gid, g in in_guilds.items():
                    s += "\n{}`{}` **{}** (`{}`) \t {} ({})".format(
                        g["patron"], gid, g["guild_name"], g["guild_size"], g["user_name"], g["role"]
                    )
            else:
                s += "¯\\_(ツ)_/¯"

            await echo(s, channel)
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "votekicks":
        try:
            readable = {}
            for k, kv in cfg.VOTEKICKS.items():
                readable[k] = {
                    "initiator": kv["initiator"].display_name,
                    "participants": [m.display_name for m in kv["participants"]],
                    "required_votes": kv["required_votes"],
                    "offender": kv["offender"].display_name,
                    "reason": kv["reason"],
                    "in_favor": [m.display_name for m in kv["in_favor"]],
                    "voice_channel": kv["voice_channel"].id,
                    "message": kv["message"].id,
                    "end_time": datetime.fromtimestamp(kv["end_time"]).strftime("%Y-%m-%d %H:%M"),
                }
            s = "```json\n" + json.dumps(readable, indent=1, sort_keys=True) + "```"
            print(s)
            try:
                await channel.send(s)
            except discord.errors.HTTPException:
                # Usually because message is over character limit
                haste_url = await utils.hastebin(s)
                await channel.send(haste_url)
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "exit":
        attempts = 0
        while attempts < 100:
            attempts += 1
            if not cfg.WRITES_IN_PROGRESS:
                print("Exiting!")
                await client.close()
                sys.exit()
                break
        else:
            print("Failed to close", cfg.WRITES_IN_PROGRESS)
            await func.react(message, "❌")

    if cmd == "loop":
        mode = params[0]
        loop_name = params[1]
        try:
            loop = ctx["loops"][loop_name]
            modes = {  # Dict of possible loop functions/attrs as [fn, arg]
                "current_loop": [loop.current_loop, None],
                "next_iteration": [loop.next_iteration, None],
                "next_run": [loop.next_iteration, None],  # Alias
                "start": [loop.start, client],
                "stop": [loop.stop, None],
                "cancel": [loop.cancel, None],
                "restart": [loop.restart, client],
                "is_being_cancelled": [loop.is_being_cancelled, None],
                "is_running": [loop.is_running, None],
                "failed": [loop.failed, None],
                "last_run": [loop.last_run, None],
            }
            if mode not in modes:
                await func.react(message, "❓")
                return
            fn, arg = modes[mode]
            if callable(fn):
                if arg is None:
                    r = fn()
                else:
                    r = fn(arg)
            else:
                r = fn
            if r is not None:
                if isinstance(r, date):
                    r = r.astimezone(pytz.timezone(cfg.CONFIG["log_timezone"]))
                    await channel.send(r.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    await channel.send(str(r))
            await func.react(message, "✅")
        except:
            await channel.send(traceback.format_exc())
            await channel.send("Loops: \n{}".format("\n".join(ctx["loops"].keys())))
            await func.react(message, "❌")

    if cmd == "rename":
        try:
            cid = utils.strip_quotes(params[0])
            c = client.get_channel(int(cid))
            new_name = " ".join(params[1:])
            if not new_name:
                new_name = "⌛"
            await c.edit(name=new_name)
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")
        else:
            await func.react(message, "✅")
            logger(g).info("%s  Force Renaming to %s", cid[-4:], new_name)

    if cmd == "forget":
        try:
            cid = int(utils.strip_quotes(params[0]))
            c = client.get_channel(cid)
            settings = utils.get_serv_settings(c.guild)
            for p, pv in settings["auto_channels"].items():
                tmp = settings["auto_channels"][p]["secondaries"].copy()
                for s, sv in pv["secondaries"].items():
                    if s == cid:
                        del settings["auto_channels"][p]["secondaries"][s]
                        break
            utils.set_serv_settings(c.guild, settings)
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")
        else:
            await func.react(message, "✅")

    if cmd == "delete":
        try:
            cid = int(utils.strip_quotes(params[0]))
            c = client.get_channel(cid)
            await c.delete()
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")
        else:
            await func.react(message, "✅")

    if cmd == "whisper":
        params_str = utils.strip_quotes(params_str)
        if "\n" not in params_str:
            await func.react(message, "❌")
            return
        uid, msg = params_str.split("\n", 1)
        try:
            u = await client.fetch_user(uid)
        except discord.errors.NotFound:
            await func.react(message, "❌")
            return
        if u.dm_channel is None:
            await u.create_dm()
        try:
            await u.dm_channel.send(msg)
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")
        else:
            await func.react(message, "✅")

    if cmd == "cleanprimaries":
        try:
            n_primaries = 0
            n_real_primaries = 0
            for g in client.guilds:
                settings = utils.get_serv_settings(g)
                tmp = {}
                n_primaries += len(settings["auto_channels"])
                for p, pv in settings["auto_channels"].items():
                    c = g.get_channel(p)
                    if c:
                        tmp[p] = pv
                n_real_primaries += len(tmp)
                if len(settings["auto_channels"]) != len(tmp):
                    settings["auto_channels"] = tmp
                    utils.set_serv_settings(g, settings)
            await channel.send("Cleaned {} of {} primaries".format(n_real_primaries, n_primaries))
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "leaveinactive":
        params_str = utils.strip_quotes(params_str)
        try:
            total_guilds = 0
            inactive_guilds = 0
            cfg.CONFIG["leave_inactive"] = []
            for g in client.guilds:
                total_guilds += 1
                if g and (not utils.guild_is_active(g) or g not in guilds):
                    cfg.CONFIG["leave_inactive"].append(g.id)
                    inactive_guilds += 1
                    if params_str == "go":
                        try:
                            await g.leave()
                        except discord.errors.NotFound:
                            pass
            if params_str == "go":
                await channel.send("Left {} of {} guilds.".format(inactive_guilds, total_guilds))
            else:
                await channel.send(
                    "Will leave {} of {} guilds. "
                    "Rerun command with 'go' at end to actually leave them.".format(inactive_guilds, total_guilds)
                )
            cfg.CONFIG["leave_inactive"] = []
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")

    if cmd == "leaveunauthorized":
        params_str = utils.strip_quotes(params_str)
        try:
            total_guilds = 0
            unauthorized_guilds = 0
            cfg.CONFIG["leave_unauthorized"] = []
            for g in client.guilds:
                total_guilds += 1
                if g not in guilds:
                    print("---", g.id, g.name)
                    cfg.CONFIG["leave_unauthorized"].append(g.id)
                    unauthorized_guilds += 1
                    if params_str == "go":
                        try:
                            await g.leave()
                        except discord.errors.NotFound:
                            pass
            if params_str == "go":
                await channel.send("Left {} of {} guilds.".format(unauthorized_guilds, total_guilds))
            else:
                await channel.send(
                    "Will leave {} of {} guilds. "
                    "Rerun command with 'go' at end to actually leave them.".format(unauthorized_guilds, total_guilds)
                )
            cfg.CONFIG["leave_unauthorized"] = []
        except:
            await channel.send(traceback.format_exc())
            await func.react(message, "❌")
