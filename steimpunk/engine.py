import numpy as np
import threading

class TraceBuffer:
    def __init__(self, max_samples=10000):
        self.max_samples = max_samples
        self.buffer = np.zeros(max_samples, dtype=np.float32)
        self.head = 0
        self.count = 0
        self.lock = threading.Lock()
        
    def append(self, data):
        with self.lock:
            n = len(data)
            if n == 0: return
            if n >= self.max_samples:
                self.buffer[:] = data[-self.max_samples:]
                self.head = 0
                self.count = self.max_samples
            else:
                remaining = self.max_samples - self.head
                if n <= remaining:
                    self.buffer[self.head:self.head+n] = data
                    self.head = (self.head + n) % self.max_samples
                else:
                    self.buffer[self.head:] = data[:remaining]
                    self.buffer[:n-remaining] = data[remaining:]
                    self.head = n - remaining
                self.count = min(self.count + n, self.max_samples)
                
    def get_data(self):
        with self.lock:
            if self.count == 0:
                return np.array([], dtype=np.float32)
            if self.count < self.max_samples:
                return self.buffer[:self.head].copy()
            else:
                return np.concatenate((self.buffer[self.head:], self.buffer[:self.head]))

def generate_braille(col1_min, col1_max, col2_min, col2_max):
    # Mapping points to braille dots
    # row 0 (top): dot 1 (val 1), dot 4 (val 8)
    # row 1: dot 2 (val 2), dot 5 (val 16)
    # row 2: dot 3 (val 4), dot 6 (val 32)
    # row 3 (bottom): dot 7 (val 64), dot 8 (val 128)
    
    char_val = 0
    # Left column (col1)
    if col1_min <= 0 <= col1_max: char_val |= 1
    if col1_min <= 1 <= col1_max: char_val |= 2
    if col1_min <= 2 <= col1_max: char_val |= 4
    if col1_min <= 3 <= col1_max: char_val |= 64
    
    # Right column (col2)
    if col2_min <= 0 <= col2_max: char_val |= 8
    if col2_min <= 1 <= col2_max: char_val |= 16
    if col2_min <= 2 <= col2_max: char_val |= 32
    if col2_min <= 3 <= col2_max: char_val |= 128
    
    return chr(0x2800 + char_val)

def decimate_to_braille(data, terminal_width, terminal_height):
    """
    Unicode (Braille) renderer: 2x4 dots per character, highest resolution.
    Returns a list of strings representing the Braille rendering of the trace.
    """
    if len(data) == 0 or terminal_width <= 0 or terminal_height <= 0:
        return [" " * terminal_width for _ in range(terminal_height)]
        
    num_cols = terminal_width * 2
    num_rows = terminal_height * 4
    
    chunk_size = max(1, len(data) // num_cols)
    usable_n = chunk_size * num_cols
    
    if len(data) < usable_n:
        pad_size = usable_n - len(data)
        data = np.pad(data, (pad_size, 0), 'edge')
        
    usable_data = data[-usable_n:]
    
    reshaped = usable_data.reshape((num_cols, chunk_size))
    mins = np.min(reshaped, axis=1)
    maxs = np.max(reshaped, axis=1)
    
    g_min, g_max = np.min(mins), np.max(maxs)
    ptp = g_max - g_min
    if ptp == 0: ptp = 1.0
    
    scaled_mins = np.floor((mins - g_min) / ptp * (num_rows - 1)).astype(int)
    scaled_maxs = np.ceil((maxs - g_min) / ptp * (num_rows - 1)).astype(int)
    
    lines = []
    for r in range(terminal_height - 1, -1, -1):
        line_chars = []
        for c in range(terminal_width):
            c1_idx = c * 2
            c2_idx = c * 2 + 1
            
            # Map global scaled min/max [0, num_rows-1] to local 4-dot cell height
            # For this character row `r`, the dot rows cover y values from `r*4` to `r*4+3`
            cell_y = r * 4
            
            c1_min_local = scaled_mins[c1_idx] - cell_y
            c1_max_local = scaled_maxs[c1_idx] - cell_y
            c2_min_local = scaled_mins[c2_idx] - cell_y
            c2_max_local = scaled_maxs[c2_idx] - cell_y
            
            ch = generate_braille(c1_min_local, c1_max_local, c2_min_local, c2_max_local)
            line_chars.append(ch)
        lines.append("".join(line_chars))
        
    return lines


def decimate_to_ascii(data, terminal_width, terminal_height):
    """
    ASCII renderer: simple '#' fill of the waveform envelope. 1 char per column.
    Lower resolution than braille but universally compatible.
    """
    if len(data) == 0 or terminal_width <= 0 or terminal_height <= 0:
        return [" " * terminal_width for _ in range(terminal_height)]

    num_cols = terminal_width
    num_rows = terminal_height

    chunk_size = max(1, len(data) // num_cols)
    usable_n = chunk_size * num_cols
    if len(data) < usable_n:
        data = np.pad(data, (usable_n - len(data), 0), 'edge')
    usable_data = data[-usable_n:]

    reshaped = usable_data.reshape((num_cols, chunk_size))
    mins = np.min(reshaped, axis=1)
    maxs = np.max(reshaped, axis=1)

    g_min, g_max = np.min(mins), np.max(maxs)
    ptp = g_max - g_min
    if ptp == 0: ptp = 1.0

    scaled_mins = np.floor((mins - g_min) / ptp * (num_rows - 1)).astype(int)
    scaled_maxs = np.ceil((maxs - g_min) / ptp * (num_rows - 1)).astype(int)

    lines = []
    for r in range(terminal_height - 1, -1, -1):
        line_chars = []
        for c in range(terminal_width):
            if scaled_mins[c] <= r <= scaled_maxs[c]:
                line_chars.append('#')
            else:
                line_chars.append(' ')
        lines.append("".join(line_chars))
    return lines


def decimate_to_ansi(data, terminal_width, terminal_height):
    """
    ANSI block renderer: uses half-block chars (▄▀█) for 2x vertical resolution.
    Smooth solid fill - a step up from ASCII in visual quality.
    """
    if len(data) == 0 or terminal_width <= 0 or terminal_height <= 0:
        return [" " * terminal_width for _ in range(terminal_height)]

    num_cols = terminal_width
    num_rows = terminal_height * 2  # Half-block gives 2x vertical resolution

    chunk_size = max(1, len(data) // num_cols)
    usable_n = chunk_size * num_cols
    if len(data) < usable_n:
        data = np.pad(data, (usable_n - len(data), 0), 'edge')
    usable_data = data[-usable_n:]

    reshaped = usable_data.reshape((num_cols, chunk_size))
    mins = np.min(reshaped, axis=1)
    maxs = np.max(reshaped, axis=1)

    g_min, g_max = np.min(mins), np.max(maxs)
    ptp = g_max - g_min
    if ptp == 0: ptp = 1.0

    scaled_mins = np.floor((mins - g_min) / ptp * (num_rows - 1)).astype(int)
    scaled_maxs = np.ceil((maxs - g_min) / ptp * (num_rows - 1)).astype(int)

    lines = []
    for r in range(terminal_height - 1, -1, -1):
        line_chars = []
        # Each char row r covers two virtual rows: y_lower (bottom) and y_upper (top)
        y_lower = r * 2
        y_upper = r * 2 + 1
        for c in range(terminal_width):
            lower_hit = scaled_mins[c] <= y_lower <= scaled_maxs[c]
            upper_hit = scaled_mins[c] <= y_upper <= scaled_maxs[c]
            if lower_hit and upper_hit:
                line_chars.append('\u2588')   # █  full block
            elif upper_hit:
                line_chars.append('\u2580')   # ▀  upper half
            elif lower_hit:
                line_chars.append('\u2584')   # ▄  lower half
            else:
                line_chars.append(' ')
        lines.append("".join(line_chars))
    return lines


def decimate_to_iso(data, terminal_width, terminal_height):
    """
    ISO-8859-1 inspired renderer: depth-shaded envelope using ░▒▓█.
    Creates a gradient effect — dense core fading to light edges.
    """
    if len(data) == 0 or terminal_width <= 0 or terminal_height <= 0:
        return [" " * terminal_width for _ in range(terminal_height)]

    num_cols = terminal_width
    num_rows = terminal_height

    chunk_size = max(1, len(data) // num_cols)
    usable_n = chunk_size * num_cols
    if len(data) < usable_n:
        data = np.pad(data, (usable_n - len(data), 0), 'edge')
    usable_data = data[-usable_n:]

    reshaped = usable_data.reshape((num_cols, chunk_size))
    mins = np.min(reshaped, axis=1)
    maxs = np.max(reshaped, axis=1)

    g_min, g_max = np.min(mins), np.max(maxs)
    ptp = g_max - g_min
    if ptp == 0: ptp = 1.0

    scaled_mins = np.floor((mins - g_min) / ptp * (num_rows - 1)).astype(int)
    scaled_maxs = np.ceil((maxs - g_min) / ptp * (num_rows - 1)).astype(int)

    # Index 0 = empty, 1-4 = ░ ▒ ▓ █
    shade_chars = ' \u2591\u2592\u2593\u2588'

    lines = []
    for r in range(terminal_height - 1, -1, -1):
        line_chars = []
        for c in range(terminal_width):
            s_min = scaled_mins[c]
            s_max = scaled_maxs[c]
            if s_min <= r <= s_max:
                center = (s_min + s_max) / 2.0
                half_span = max((s_max - s_min) / 2.0, 0.5)
                depth = 1.0 - (abs(r - center) / half_span)
                depth = max(0.0, min(1.0, depth))
                idx = 1 + int(depth * 3.99)
                idx = min(4, max(1, idx))
                line_chars.append(shade_chars[idx])
            else:
                line_chars.append(' ')
        lines.append("".join(line_chars))
    return lines


def render_trace(data, terminal_width, terminal_height, charset="unicode"):
    """
    Dispatch to the appropriate renderer based on the selected charset.
    
    charset options:
        "unicode"  - Braille 2x4 dot matrix (highest resolution)
        "ascii"    - Simple '#' fill of the waveform envelope
        "ansi"     - Half-block chars (▄▀█) for smooth 2x vertical resolution
        "iso"      - Depth-shaded envelope using ░▒▓█ gradient
    """
    if charset == "ascii":
        return decimate_to_ascii(data, terminal_width, terminal_height)
    elif charset == "ansi":
        return decimate_to_ansi(data, terminal_width, terminal_height)
    elif charset == "iso":
        return decimate_to_iso(data, terminal_width, terminal_height)
    else:
        return decimate_to_braille(data, terminal_width, terminal_height)
