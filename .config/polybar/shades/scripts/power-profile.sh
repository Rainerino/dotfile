#!/bin/sh

# Get the current profile
current_profile=$(powerprofilesctl get)

# Handle the toggle argument
if [ "$1" = "--toggle" ]; then
    case $current_profile in
        performance)
            powerprofilesctl set balanced
            ;;
        balanced)
            powerprofilesctl set power-saver
            ;;
        power-saver)
            # Check if performance is available before switching to it
            if powerprofilesctl list | grep -q "performance"; then
                powerprofilesctl set performance
            else
                powerprofilesctl set balanced
            fi
            ;;
    esac
else
    # Output the full text label based on the current profile
    case $current_profile in
        performance)
            # Red text for Performance
            echo "%{F#ff5555} Performance%{F-}"
            ;;
        balanced)
            # Yellow text for Balanced
            echo "%{F#f1fa8c} Balanced%{F-}"
            ;;
        power-saver)
            # Green text for Power Saver
            echo "%{F#50fa7b} Power Saver%{F-}"
            ;;
        *)
            echo "Unknown"
            ;;
    esac
fi
