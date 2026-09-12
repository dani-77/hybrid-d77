#!/usr/bin/env python3
# Waybar custom/media helper -- MPRIS via playerctl.
# deps (hybrid-d77/cports): playerctl, python-gobject (provides the
# `gi` module Python imports below).
# Emits one JSON line ({"text","class","alt"}) on every player change.
import gi
import json
import sys
import signal
import logging
from typing import List

gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl, GLib  # noqa: E402

logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(message)s")


def signal_handler(sig, frame):
    sys.exit(0)


class PlayerManager:
    def __init__(self):
        self.manager = Playerctl.PlayerManager()
        self.loop = GLib.MainLoop()
        self.manager.connect("name-appeared", self.on_player_appeared)
        self.manager.connect("player-vanished", self.on_player_vanished)
        for name in self.manager.props.player_names:
            self.init_player(name)

    def run(self):
        self.loop.run()

    def init_player(self, name):
        player = Playerctl.Player.new_from_name(name)
        player.connect("playback-status", self.on_playback_status_changed, None)
        player.connect("metadata", self.on_metadata_changed, None)
        self.manager.manage_player(player)
        self.on_metadata_changed(player, player.props.metadata)

    def get_players(self) -> List[Playerctl.Player]:
        return self.manager.props.players

    def write_output(self, text, player):
        out = {
            "text": text,
            "class": "custom-" + player.props.player_name,
            "alt": player.props.player_name,
        }
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()

    def clear_output(self):
        sys.stdout.write("\n")
        sys.stdout.flush()

    def on_playback_status_changed(self, player, status, _=None):
        self.on_metadata_changed(player, player.props.metadata)

    def on_metadata_changed(self, player, metadata, _=None):
        artist = player.get_artist()
        title = player.get_title()
        title = title.replace("&", "&amp;") if title else ""
        artist = artist.replace("&", "&amp;") if artist else ""

        track = f"{artist} - {title}" if artist and title else (title or artist)
        if player.props.status == "Playing":
            track = " " + track
        elif player.props.status == "Paused":
            track = " " + track

        current = self.get_players()
        if current and current[-1].props.player_name == player.props.player_name:
            self.write_output(track, player)
        elif not current:
            self.clear_output()

    def on_player_appeared(self, _, name):
        self.init_player(name)

    def on_player_vanished(self, _, player):
        players = self.get_players()
        if players:
            self.on_metadata_changed(players[-1], players[-1].props.metadata)
        else:
            self.clear_output()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    PlayerManager().run()


if __name__ == "__main__":
    main()
