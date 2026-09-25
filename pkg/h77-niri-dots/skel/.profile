# hybrid-d77 :: launch niri automatically on the first virtual terminal.
#
# Same approach as the sway variant (h77-sway-dots' .profile): no
# greeter, plain getty login, /etc/motd documents the credentials.
# Plain `niri`, not `niri --session`: that mode expects a systemd user
# session to import its environment into, and cports' niri ships no
# dinit equivalent yet (its template's own TODO).
if [ -z "$WAYLAND_DISPLAY" ] && [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
	exec niri
fi
