import subprocess
cmd = '. $CONDA_PREFIX/etc/profile.d/conda.sh && conda activate paramak_env' 
subprocess.call(cmd, shell=True, executable='/bin/bash')
import os
os.system("conda activate paramak_env")
import paramak
rotated_circle = paramak.ExtrudeCircleShape(
    points=[(0, 0),], radius=0.95, distance=1.2, workplane="XZ", name="part0.stl",
)

grey_part = paramak.ExtrudeStraightShape(
    points=[
        (-1.15, -1.25),
        (1.15, -1.25),
        (1.15, 1.75),
        (-1.15, 1.75),
    ],
    distance=1.2,
    color=(0.5, 0.5, 0.5),
    cut=rotated_circle,
    name="grey_part",
)

red_part = paramak.RotateStraightShape(
    points=[
        (0.75, -0.6),
        (0.95, -0.6),
        (0.95, 0.6),
        (0.75, 0.6),
    ],
    color=(0.5, 0, 0),
    workplane="XY",
    rotation_angle=360,
    name="red_part",
)

blue_part = paramak.RotateStraightShape(
    points=[
        (0.6, -0.6),
        (0.75, -0.6),
        (0.75, 0.6),
        (0.6, 0.6),
    ],
    color=(0, 0, 0.5),
    workplane="XY",
    rotation_angle=360,
    name="blue_part",
)

my_reactor = paramak.Reactor([grey_part, red_part, blue_part])
