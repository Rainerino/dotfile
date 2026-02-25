#!/bin/sh
# Shows GPU Util % and Temp
nvidia-smi --query-gpu=utilization.gpu,temperature.gpu --format=csv,noheader,nounits | awk -F', ' '{print $1"%" " ("$2"°C)"}'
