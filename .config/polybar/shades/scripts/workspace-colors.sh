#!/usr/bin/env bash

PFILE="$HOME/.config/polybar/shades/colors.ini"
MFILE="$HOME/.config/polybar/shades/modules.ini"

get_color() {
	awk -F ' = ' -v key="$1" '$1==key {print $2}' "$PFILE"
}

shade0="$(get_color "shade0")"
shade1="$(get_color "shade1")"
shade2="$(get_color "shade2")"
shade3="$(get_color "shade3")"
shade4="$(get_color "shade4")"
shade5="$(get_color "shade5")"
shade6="$(get_color "shade6")"
shade7="$(get_color "shade7")"

if [[ -z "$shade0" || -z "$shade1" || -z "$shade2" || -z "$shade3" || -z "$shade4" || -z "$shade5" || -z "$shade6" || -z "$shade7" ]]; then
	exit 1
fi

# Match the right-side palette order
c0="$shade7"
c1="$shade6"
c2="$shade5"
c3="$shade4"
c4="$shade3"
c5="$shade3"
c6="$shade2"
c7="$shade2"
cdef="$shade2"

sed -i \
	-e "s|^icon-0 = .*|icon-0 = 1;%{B${c0}}|" \
	-e "s|^icon-1 = .*|icon-1 = 2;%{B${c1}}|" \
	-e "s|^icon-2 = .*|icon-2 = 3;%{B${c2}}|" \
	-e "s|^icon-3 = .*|icon-3 = 4;%{B${c3}}|" \
	-e "s|^icon-4 = .*|icon-4 = 5;%{B${c4}}|" \
	-e "s|^icon-5 = .*|icon-5 = 6;%{B${c5}}|" \
	-e "s|^icon-6 = .*|icon-6 = 7;%{B${c6}}|" \
	-e "s|^icon-7 = .*|icon-7 = 8;%{B${c7}}|" \
	-e "s|^icon-default = .*|icon-default = %{B${cdef}}|" \
	"$MFILE"
