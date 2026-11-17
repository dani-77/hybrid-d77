# Bug: janelas de abrir/guardar ficheiros não abrem (portais sem ecrã)

Diagnosticado e corrigido no sistema instalado a 2026-11-17. Correção aplicada
às ISOs no mesmo dia (`h77-niri-dots` r2, `h77-sway-dots` r3); falta testar
com cbuild e numa ISO arrancada.

## Sintoma

Em várias aplicações, os botões que deviam abrir uma janela para escolher
ficheiros não fazem nada e não mostram erro. Caso concreto: Thunderbird 159 →
Definições de conta → Encriptação ponta-a-ponta → "Importar chave OpenPGP
existente" não abre nada. O mesmo deve acontecer com anexos, downloads, etc.

## Causa

- O hybrid-d77 usa **dinit**, não systemd. O D-Bus de sessão
  (`dbus-daemon --session --dinit`, serviço `dbus-daemon.user`) arranca
  **antes** do compositor e por isso fica sem `WAYLAND_DISPLAY`/`DISPLAY` no
  ambiente de ativação.
- Em sessões com systemd, o niri importa estas variáveis para o
  systemd/D-Bus. Aqui isso não acontece, e nada na ISO o faz.
- Quando uma app pede o FileChooser, o `xdg-desktop-portal` ativa o backend
  (`xdg-desktop-portal-gtk`, ou o `-gnome`) por D-Bus. O backend herda o
  ambiente sem ecrã e termina logo:
  ```
  Gtk-WARNING **: cannot open display:
  ```
  No log do `xdg-desktop-portal -v -r`:
  ```
  Failed to create file chooser proxy: Error calling StartServiceByName for
  org.freedesktop.impl.portal.desktop.gtk: Process ... exited with status 1
  ```
  Também falham os proxies de settings, notification, inhibit, email…
- Reprodução: `env -u WAYLAND_DISPLAY -u DISPLAY /usr/lib/xdg-desktop-portal-gtk`
  → exit 1. Com as variáveis definidas, arranca normalmente.

Nota: o `/usr/share/xdg-desktop-portal/niri-portals.conf` (do niri) prefere
`gnome;gtk`. O FileChooser do portal-gnome pode ainda depender do Nautilus,
que a ISO não traz. Mas esta **não** era a causa principal: com as variáveis
de ecrã passadas ao D-Bus, a janela abriu.

## Correção aplicada no sistema (manual)

1. Sessão atual:
   ```sh
   dbus-update-activation-environment WAYLAND_DISPLAY DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE=wayland
   # depois matar os portais (o D-Bus volta a lançá-los quando forem precisos)
   ```
2. Linha acrescentada a `~/.config/niri/config.kdl`, **antes** dos outros
   `spawn-at-startup`:
   ```kdl
   // Passa as variáveis do ecrã ao D-Bus (sem systemd), senão os portais (ex.: janela de abrir ficheiros) não arrancam
   spawn-at-startup "dbus-update-activation-environment" "WAYLAND_DISPLAY" "DISPLAY" "XDG_CURRENT_DESKTOP" "XDG_SESSION_TYPE=wayland"
   ```
3. Ficheiro extra (opcional, mantido): `~/.config/xdg-desktop-portal/niri-portals.conf`
   = cópia do ficheiro do sistema com mais esta linha:
   ```
   org.freedesktop.impl.portal.FileChooser=gtk;
   ```
   Força o FileChooser GTK e evita a dependência do Nautilus no portal-gnome.

## O que fazer na ISO

- [x] `pkg/h77-niri-dots/skel/.config/niri/config.kdl`: acrescentar o
      `spawn-at-startup "dbus-update-activation-environment" ...` acima, como
      primeira linha de autostart (antes de `pipewire`, ~linha 203).
- [x] `pkg/h77-sway-dots/skel/.config/sway/config`: o sway também não importa
      as variáveis sem systemd. Acrescentar antes dos outros `exec`:
      ```
      exec dbus-update-activation-environment WAYLAND_DISPLAY DISPLAY XDG_CURRENT_DESKTOP=sway XDG_SESSION_TYPE=wayland
      ```
      (Confirmar primeiro se já existe algo equivalente, p. ex. em `autostart.d/`.)
- [x] Decidir sobre o FileChooser (feito: skel `~/.config/xdg-desktop-portal/niri-portals.conf`
      com `FileChooser=gtk`; o portal-gnome 51 depende do Nautilus): a) enviar
      `/usr/share/xdg-desktop-portal/niri-portals.conf`, ou melhor o override em
      `/etc/xdg/xdg-desktop-portal/niri-portals.conf`, com
      `FileChooser=gtk`; ou b) garantir que o portal-gnome funciona sem
      Nautilus. `xdg-desktop-portal-gtk` já vem na ISO (ver `docs/NOTES.md`
      ~linha 636). No sway, ver qual `sway-portals.conf` e qual backend
      (`-wlr` + `-gtk`) ficam ativos.
- [x] Subir o `pkgrel` dos pacotes alterados e anotar em `docs/NOTES.md`.
- [ ] Testar na live ISO:
      ```sh
      gdbus call --session --dest org.freedesktop.portal.Desktop \
        --object-path /org/freedesktop/portal/desktop \
        --method org.freedesktop.portal.FileChooser.OpenFile "" "Teste" "{}"
      ```
      Tem de aparecer uma janela. `ps | grep xdg-desktop-portal-gtk` deve
      mostrar o processo vivo. Testar também uma janela real (Thunderbird ou
      Firefox → abrir ficheiro).

## Contexto do sistema

- hybrid-d77 (Chimera Linux, `ID_LIKE=chimera`), init dinit, sessão niri
  (`XDG_CURRENT_DESKTOP=niri`), Wayland + Xwayland (`DISPLAY=:0`).
- O skel vive em `/usr/share/hybrid-d77/skel` e o `mklive` copia-o para
  `/etc/skel` da imagem.
- Utilizadores que já instalaram o sistema não recebem o skel novo. Para eles,
  o `h77-welcome` ou o "Update hybrid-d77 packages" teria de aplicar a linha
  no `config.kdl` do utilizador (ou documentar a correção manual acima).
