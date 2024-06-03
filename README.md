# Virtual Memory Manager

This project implements a virtual memory manager that translates virtual addresses to physical addresses and handles paging. The manager reads segment and page tables from an initialization file and processes commands from an input file, writing the results to an output file.

## Files

- `main.py`: The main script to run the virtual memory manager.
- `pm.py`: Contains the `PhysicalMemory` class that simulates the physical memory.


## Usage

To run the virtual memory manager, use the following command:

```bash
python main.py --init <init_file> --input <input_file> [--output <output_file>]
```

Example:
python main.py --input init-dp.txt --input input-dp.txt
