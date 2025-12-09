#!/bin/bash

COLOURS=(1 0 0 0 1 0 0 0 1 0 1 1 1 0 1 1 1 0)

M=${#COLOURS[@]}
N=$((M / 3))
for (( I=0; I<$N; ++I )); do
  echo $I
  R=${COLOURS[$(($I * 3))]}
  G=${COLOURS[$(($I * 3 + 1))]}
  B=${COLOURS[$(($I * 3 + 2))]}
  
  sed 's/\(<color sid="diffuse">\).*\(<\/color>\)/\1'"$R $G $B"' 1\2/' agv.dae > agv$I.dae
done
