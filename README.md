# НТИ 2021 — Передовые Производственные Технологии

The source code of the "Hsudu" team of the 2021 NTI Olympiad in the direction of
Advanced production technologies

## Task description

The task consisted of two parts:

1. Engineering (not in this repo): Design a nozzle for the arm of a robot
   manipulator, which should prevent damage to parts and the environment by
   detaching at a certain load in case of wrong movements.
2. Programming: Create a program, which accepts 2 inputs:
   - JSON file containing the description of the building (blocks, their types
     and coordinates)
   - Image of the current field state (ArUco markers on the corners, positions
     of blocks)

   Program should generate the program for a robot manipulator, which will move
   blocks on the field to create a building described in the JSON file.

   Example inputs and demo can be found in the `resources/` directory.

## Demo

Example of the execution of the generated program by the robot manipulator:

https://github.com/evermake/PPT-NTI-2021/assets/53311479/c28e8f94-9ab3-4096-aebd-70543ee0f0cc
