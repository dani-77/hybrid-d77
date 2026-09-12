# hybrid-d77 :: launch sway automatically on the first virtual terminal.
#
# Deliberately no greeter here, even though greetd IS packaged in
# cports (confirmed 2026-09-12, under the `user` repo tier) -- the
# user's own call: Void's and Chimera's own convention is a plain getty
# login: prompt, with /etc/motd (see h77-dots) documenting the anon/
# chimera and root/chimera credentials. This file is what turns that
# plain login into a sway session once someone actually logs in.
if [ -z "$WAYLAND_DISPLAY" ] && [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
	exec sway
fi
