import numpy as np
import cv2

# Thresholds (Fixed for demo purposes)
MOTION_THRESHOLD = 1.0  # Adjust as needed based on actual video
ENTROPY_THRESHOLD = 3.0 # Adjust as needed based on actual video
PERSISTENCE_N = 10      # Number of consecutive frames for alarm

class FlockTracker:
    def __init__(self):
        self.prev_frame_gray = None
        self.consecutive_breaches = 0
        self.alarm_active = False

    def compute_shannon_entropy(self, boxes, width, height, grid_size=10):
        if not len(boxes):
            return 0.0

        n_cells = grid_size * grid_size
        cell_width = width / grid_size
        cell_height = height / grid_size

        cell_indices = []
        for box in boxes:
            # box format: [x1, y1, x2, y2]
            cx = (box[0] + box[2]) / 2
            cy = (box[1] + box[3]) / 2

            grid_x = int(cx / cell_width)
            grid_y = int(cy / cell_height)
            
            # Ensure within bounds
            grid_x = min(max(grid_x, 0), grid_size - 1)
            grid_y = min(max(grid_y, 0), grid_size - 1)
            
            cell_idx = grid_y * grid_size + grid_x
            cell_indices.append(cell_idx)

        counts = np.bincount(cell_indices, minlength=n_cells)
        probs = counts / counts.sum()
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs))
        return entropy

    def compute_motion(self, curr_frame_gray):
        if self.prev_frame_gray is None:
            self.prev_frame_gray = curr_frame_gray
            return 5.0 # Initial healthy motion dummy value

        # Compute absolute difference
        frame_diff = cv2.absdiff(curr_frame_gray, self.prev_frame_gray)
        # Using a simple mean for motion index
        motion_index = frame_diff.mean()

        self.prev_frame_gray = curr_frame_gray
        return motion_index

    def evaluate_health(self, motion, entropy):
        motion_breach = motion < MOTION_THRESHOLD
        entropy_breach = entropy < ENTROPY_THRESHOLD

        # Dual Signal Fusion
        if motion_breach and entropy_breach:
            self.consecutive_breaches += 1
        else:
            self.consecutive_breaches = 0

        # Persistence Criterion
        if self.consecutive_breaches >= PERSISTENCE_N:
            self.alarm_active = True
        else:
            self.alarm_active = False

        return self.alarm_active

    def reset(self):
        self.prev_frame_gray = None
        self.consecutive_breaches = 0
        self.alarm_active = False
