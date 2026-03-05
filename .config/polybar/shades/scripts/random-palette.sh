#!/usr/bin/env bash

SDIR="$HOME/.config/polybar/shades/scripts"

palettes=(
	amber blue blue-gray brown cyan deep-orange deep-purple green gray indigo
	light-blue light-green lime orange pink purple red teal yellow
)

modes=(light dark)

case "${1:-}" in
	--light) mode="light" ;;
	--dark)  mode="dark" ;;
	*)       mode="${modes[RANDOM % ${#modes[@]}]}" ;;
esac

palette="${palettes[RANDOM % ${#palettes[@]}]}"

"$SDIR/colors-${mode}.sh" "--${palette}"
