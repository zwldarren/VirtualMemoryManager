from pathlib import Path
from pm import PhysicalMemory
import argparse


class VMManager:
    def __init__(self) -> None:
        self.PM_SIZE = 524288
        self.FRAME_SIZE = 512
        self.pm = PhysicalMemory(self.PM_SIZE)

    def init(self, filename: Path) -> None:
        """Load initialization file. This function will read the
        segment table and page table entries from files into the Physical Memory.

        Args:
            filename (Path): Path to initialization file
        """
        with open(filename, "r") as file:
            lines = file.readlines()

        st_lists = list(map(int, lines[0].strip().split()))
        self.pm.load_segment_table(st_lists)

        if len(lines) > 1:
            pt_lists = list(map(int, lines[1].strip().split()))
            self.pm.load_page_table(pt_lists)

    def translate(self, va) -> int:
        """Translate the virtual address to physical address.

        Args:
            va (int): Virtual address

        Returns:
            int: Physical address
        """
        s = va >> 18
        w = va & 0x1FF
        p = (va >> 9) & 0x1FF
        pw = va & 0x3FFFF

        segment_size = self.pm.read(2 * s)
        f1 = self.pm.read(2 * s + 1)

        if segment_size == 0 or pw >= segment_size:
            return -1  # invalid segment

        # if frame_num < 0, then goto disk
        if f1 < 0:
            f1 = self.pm.get_free_frame()
            self.pm.read_block_from_disk(-self.pm.read(2 * s + 1), f1)
            self.pm.write(2 * s + 1, f1)

        f2 = self.pm.read(f1 * self.FRAME_SIZE + p)
        # page fault: page is not resident
        if f2 < 0:
            f2 = self.pm.get_free_frame()
            self.pm.read_block_from_disk(-self.pm.read(f1 * self.FRAME_SIZE + p), f2)
            # update PT entry
            self.pm.write(f1 * self.FRAME_SIZE + p, f2)

        return f2 * self.FRAME_SIZE + w if f2 >= 0 else -1

    def execute(self, input_file: Path, output_file: Path) -> None:
        """Execute the commands in the input file and write the output to the output file.
        The input file contains the following commands:
        - TA <va>: Translate the virtual address to physical address
        - RP <pa>: Read the content at the physical address
        - NL: Newline

        Args:
            input_file (Path): Path to the input file
            output_file (Path): Path to the output file
        """
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                command = parts[0]

                if command == "TA":
                    va = int(parts[1])
                    pa = self.translate(va)
                    outfile.write(f"{pa} ")
                elif command == "RP":
                    pa = int(parts[1])
                    content = self.pm.read(pa)
                    outfile.write(f"{content} ")
                elif command == "NL":
                    outfile.write("\n")


def main(init_path, input_path, output_path):
    vm_manager = VMManager()
    vm_manager.init(init_path)
    vm_manager.execute(input_path, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtual Memory Manager")
    parser.add_argument(
        "--init", type=str, required=True, help="Path to the init file (init.txt)"
    )
    parser.add_argument(
        "--input", type=str, required=True, help="Path to the input file (input.txt)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.txt",
        help="Path to the output file (default: output.txt in the same directory)",
    )

    args = parser.parse_args()

    init_file = Path(args.init)
    input_file = Path(args.input)
    output_file = Path(args.output)

    main(init_file, input_file, output_file)
