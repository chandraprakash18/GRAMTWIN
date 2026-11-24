"""
GRAMTWIN - Satellite Data Augmentations
Geometrically valid transformations preserving spectral physical consistency.
"""

import random
import numpy as np

class SatelliteAugmentation:
    def __init__(self, p_flip=0.5, p_rot=0.5, p_noise=0.3):
        self.p_flip = p_flip
        self.p_rot = p_rot
        self.p_noise = p_noise

    def __call__(self, image, mask):
        # image: (H, W, C) float32 in [0, 1]
        # mask: (H, W) uint8 in [0, 5]

        # Horizontal flip
        if random.random() < self.p_flip:
            image = np.fliplr(image)
            mask = np.fliplr(mask)

        # Vertical flip
        if random.random() < self.p_flip:
            image = np.flipud(image)
            mask = np.flipud(mask)

        # Random 90 deg rotation
        if random.random() < self.p_rot:
            k = random.choice([1, 2, 3])
            image = np.rot90(image, k)
            mask = np.rot90(mask, k)

        # Subtle sensor noise
        if random.random() < self.p_noise:
            noise = np.random.normal(0, 0.02, image.shape).astype(np.float32)
            image = np.clip(image + noise, 0.0, 1.0)

        return np.ascontiguousarray(image), np.ascontiguousarray(mask)
