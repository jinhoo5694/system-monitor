#!/usr/bin/env python3
"""
Pre-render Iron Man model rotation frames for fast playback
"""

import os
import math
import numpy as np
from stl import mesh
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for rendering
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Settings
FRAME_COUNT = 120  # Number of frames for full rotation (3 degrees per frame)
FRAME_SIZE = (450, 450)  # Match the 3D panel size
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'ironman', 'cache')
BG_COLOR = '#0a0a12'
FACE_COLOR = '#0a1520'
EDGE_COLOR = '#00d4ff'

def load_and_prepare_model():
    """Load STL and prepare transformed faces"""
    model_path = os.path.join(os.path.dirname(__file__), 'ironman', 'files', 'Chest_and_Head.stl')

    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return None

    print(f"Loading model from {model_path}...")
    model_mesh = mesh.Mesh.from_file(model_path)
    vectors = model_mesh.vectors.copy()

    # Center the model
    all_points = vectors.reshape(-1, 3)
    center = all_points.mean(axis=0)
    vectors = vectors - center

    # Transform orientation: STL Z-up to display Y-up
    transformed = np.zeros_like(vectors)
    transformed[:, :, 0] = vectors[:, :, 0]
    transformed[:, :, 1] = -vectors[:, :, 2]
    transformed[:, :, 2] = vectors[:, :, 1]

    # Normalize scale
    all_points = transformed.reshape(-1, 3)
    scale = np.max(np.abs(all_points))
    transformed = transformed / scale

    print(f"Loaded {len(transformed)} faces")
    return transformed

def render_frame(faces, angle, output_path):
    """Render a single frame at the given rotation angle"""
    # Create rotation matrix for Z-axis rotation
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    rotation_matrix = np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])

    # Apply rotation
    rotated_faces = np.einsum('ij,...j->...i', rotation_matrix, faces)

    # Create figure
    fig = Figure(figsize=(4.5, 4.5), dpi=100, facecolor=BG_COLOR)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(BG_COLOR)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Add mesh
    mesh_collection = Poly3DCollection(
        rotated_faces,
        facecolors=FACE_COLOR,
        edgecolors=EDGE_COLOR,
        linewidths=0.3,
        alpha=0.9
    )
    ax.add_collection3d(mesh_collection)

    # Set view - with margin so model doesn't get cropped
    ax.set_xlim3d(-0.65, 0.65)
    ax.set_ylim3d(-0.65, 0.65)
    ax.set_zlim3d(-0.65, 0.65)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=10, azim=-90)

    # Save frame
    fig.savefig(output_path, facecolor=BG_COLOR, edgecolor='none',
                bbox_inches='tight', pad_inches=0)
    fig.clear()
    import matplotlib.pyplot as plt
    plt.close(fig)

def main():
    """Pre-render all rotation frames"""
    os.makedirs(CACHE_DIR, exist_ok=True)

    faces = load_and_prepare_model()
    if faces is None:
        return

    print(f"Rendering {FRAME_COUNT} frames...")

    for i in range(FRAME_COUNT):
        angle = (i * 360) / FRAME_COUNT
        output_path = os.path.join(CACHE_DIR, f'frame_{i:03d}.png')
        render_frame(faces, angle, output_path)

        # Progress indicator
        progress = (i + 1) / FRAME_COUNT * 100
        print(f"\rProgress: {progress:.1f}% ({i+1}/{FRAME_COUNT})", end='', flush=True)

    print(f"\nDone! Frames saved to {CACHE_DIR}")

if __name__ == "__main__":
    main()
