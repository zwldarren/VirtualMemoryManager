import numpy as np


class PhysicalMemory:
    def __init__(self, size: int):
        # Physical memory
        self._memory = np.zeros(size, dtype=int)
        # Initialize free frames, True means free, False means occupied
        self._free_frames = [True] * (size // 512)
        # Disk for paging, 1024 blocks of 512 words each
        self._paging_disk = np.zeros((1024, 512), dtype=int)

    def get_free_frame(self) -> int:
        """Get a free frame from the list of free frames.

        Returns:
            int: Free frame index
        """
        for i in range(len(self._free_frames)):
            if self._free_frames[i]:
                self._free_frames[i] = False
                return i
        return -1

    def read(self, index: int) -> int:
        """Get the value from the Physical Memory at the given index.

        Args:
            index (int): Index to read from memory

        Returns:
            int: Value in the memory
        """
        if index < 0 or index >= len(self._memory):
            return -1
        return self._memory[index]

    def write(self, index: int, value: int):
        """Write the value to the Physical Memory at the given index.

        Args:
            index (int): Index to write to memory
            value (int): Value to write
        """
        if index < 0 or index >= len(self._memory):
            return
        self._memory[index] = value

    def read_block_from_disk(self, b: int, m: int):
        """Copy block D[b] into PM frame starting at location PM[m].

        Args:
            b (int): Block number
            m (int): Frame number
        """
        start = m * 512
        end = start + 512
        self._memory[start:end] = self._paging_disk[b]

    def load_segment_table(self, st_lists: list):
        """Load the segment table into the Physical Memory.
        Each entry is 3 words long: <s, z, f>

        Args:
            st_lists (list): List of segment table entries
        """
        for i in range(0, len(st_lists), 3):
            s, z, f = st_lists[i : i + 3]
            self.write(2 * s, z)
            self.write(2 * s + 1, f)
            if f >= 0:
                self._free_frames[f] = False

    def load_page_table(self, pt_lists: list):
        """Load the page table into the Physical Memory.
        Each entry is 3 words long: <s, p, f>
        if f >= 0, then f is the frame number, else it is the block number on disk.

        Args:
            pt_lists (list): List of page table entries
        """
        for i in range(0, len(pt_lists), 3):
            s, p, f = pt_lists[i : i + 3]
            pt_start = self.read(2 * s + 1) * 512
            if self.read(2 * s + 1) >= 0:
                self.write(pt_start + p, f)
            else:
                block_index = -self.read(2 * s + 1)
                free_index = self.get_free_frame()
                self._paging_disk[block_index, free_index] = f
            if f >= 0:
                self._free_frames[f] = False
