#!/bin/sh
# hybrid-d77 :: re-apply Utumno's saved wallpaper at niri startup (its
# own documented hook: set-wallpaper.sh startup). On the very first
# login there is no saved one yet, so seed ~/Wallpaper (the folder
# Utumno's picker scans) with h77-dots' own d77.png and pick it --
# otherwise the session would start on Utumno's plain backdrop.
STATE="$HOME/.cache/quickshell/wallpaper/current"
if [ ! -f "$STATE" ]; then
	mkdir -p "$HOME/Wallpaper" "$(dirname "$STATE")"
	[ -e "$HOME/Wallpaper/d77.png" ] || cp "$HOME/.config/backgrounds/d77.png" "$HOME/Wallpaper/"
	printf '%s' "$HOME/Wallpaper/d77.png" > "$STATE"
fi
exec /usr/share/quickshell/utumno/wallpaper/set-wallpaper.sh startup
