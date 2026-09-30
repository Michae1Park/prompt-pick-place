"""Vision pipeline, one module per stage: detect (1, YOLOE), pose (2, FoundationPose), spatial (3, table plane +
occupancy), grasp (4), place (5, shelf supports + rest poses). Shared: transforms, viz."""
import os

import numpy as np
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    with open(os.path.join(REPO, 'config.yaml')) as f:
        return yaml.safe_load(f)


def read_obj_vertices(path):
    """Vertices (N, 3) of a Wavefront OBJ (no mesh library needed)."""
    with open(path) as f:
        return np.array([[float(v) for v in line.split()[1:4]] for line in f if line.startswith('v ')])
