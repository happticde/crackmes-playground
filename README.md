# Crackmes Development Environment

Welcome to your personal reverse engineering lab! This environment is designed to give you a secure, isolated space to practice your skills on "crackmes" without any risk to your host machine.

## Getting Started

1.  **Build the Docker Image:**
    Open your terminal in this directory and run:
    ```bash
    docker compose build
    ```

2.  **Run the Container:**
    To start the container and get a shell inside it, run:
    ```bash
    docker compose run --rm crackme-dev
    ```
    You will be dropped into a `bash` shell as the `user` inside the container. The `--rm` flag is good practice as it will automatically remove the container when you exit.

3.  **Your Workspace:**
    The `crackmes` directory in this project is mounted inside the container at `/home/user/crackmes`. Any files you put in the local `crackmes` directory will be available inside the container, and any changes you make inside the container will be reflected on your host machine.

## Tools Included

*   **`gdb`**: The GNU Debugger. Essential for dynamic analysis (running the program and inspecting its state).
*   **`radare2`**: A powerful suite of tools for static and dynamic analysis. It has a steeper learning curve but is incredibly versatile.
*   **`hexedit`**: A simple command-line hex editor for patching binaries.
*   **`gcc`, `nasm`, `build-essential`**: Compilers and tools to write and build your own C and assembly programs.
*   **`wget`, `curl`**: For downloading more crackmes from the web.

## First Steps

This environment now includes a convenient `get-crackme` command to automatically download crackmes and their details from [crackmes.one](https://crackmes.one).

1.  **Use the `get-crackme` command:**
    Inside the container, you can use the `get-crackme` command followed by the crackme's ID. For example, to download the crackme from `https://crackmes.one/crackme/685048992b84be7ea7743940`:
    ```bash
    get-crackme 685048992b84be7ea7743940
    ```
    This will create a new directory (e.g., `crackmes/CrackMe_Title`) containing the downloaded binary and a `README.md` file with all the scraped information (details, description, comments).

    You can also specify a different output directory using the `-o` or `--output` flag:
    ```bash
    get-crackme -o my_challenges 685048992b84be7ea7743940
    ```

2.  **Start Analyzing:**
    Once downloaded, navigate into the newly created crackme directory and start analyzing using the tools in this environment. Remember to identify the binary type (Linux ELF or Windows PE) using the `file` command as described in the "Working with Multiple Architectures" section.

## Documentation & Resources

Here are some resources to help you on your journey.

### Assembly Language

*   **Intel x86 Assembly Reference:** [https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) (This is the official, very dense, but complete reference).
*   **A more friendly guide:** [https://www.cs.virginia.edu/~evans/cs216/guides/x86.html](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html)

### GDB

*   **GDB Cheat Sheet:** [https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf)
*   **Full GDB Documentation:** [https://www.gnu.org/software/gdb/documentation/](https://www.gnu.org/software/gdb/documentation/)

### Radare2

*   **The Radare2 Book:** [https://book.radare.org/](https://book.radare.org/)
*   **Radare2 Cheatsheet:** [https://github.com/radareorg/radare2/blob/master/doc/cheatsheet.md](https://github.com/radareorg/radare2/blob/master/doc/cheatsheet.md)

### Objdump

`objdump` is a command-line utility for displaying information from object files. It's part of the GNU Binutils, and it's invaluable for static analysis of binaries, especially when you want to inspect the assembly code without executing the program.

#### Common Options:

*   `-d` or `--disassemble`: Disassemble executable sections. This is perhaps the most commonly used option, showing the assembly code.
    ```bash
    objdump -d <binary_file>
    ```
*   `-M intel` or `-M att`: Specify the assembly syntax (Intel or AT&T). Intel syntax is often preferred for readability.
    ```bash
    objdump -d -M intel <binary_file>
    ```
*   `-S` or `--source`: Intermix source code with disassembly. Requires the binary to be compiled with debugging information (`-g`).
    ```bash
    objdump -S <binary_file>
    ```
*   `-D` or `--disassemble-all`: Disassemble all sections, not just those expected to contain instructions. Useful for finding hidden code or data.
    ```bash
    objdump -D <binary_file>
    ```
*   `-j <section_name>` or `--section=<section_name>`: Disassemble only the specified section. For example, `.text` for code, `.data` for initialized data.
    ```bash
    objdump -d -j .text <binary_file>
    ```
*   `-t` or `--syms`: Display the symbol table entries of the file. Shows functions, global variables, etc.
    ```bash
    objdump -t <binary_file>
    ```
*   `-T` or `--dynamic-syms`: Display the dynamic symbol table entries. Useful for dynamically linked executables to see imported/exported functions.
    ```bash
    objdump -T <binary_file>
    ```
*   `-x` or `--all-headers`: Display all headers (full information).
    ```bash
    objdump -x <binary_file>
    ```
*   `-f` or `--file-headers`: Display the contents of the overall file header.
    ```bash
    objdump -f <binary_file>
    ```
*   `-h` or `--section-headers`: Display the contents of the section headers.
    ```bash
    objdump -h <binary_file>
    ```

#### Best Practices:

1.  **Start with `-d -M intel`:** This gives you a clear view of the assembly code in a readable format.
2.  **Use `grep` for filtering:** `objdump` output can be very verbose. Pipe its output to `grep` to search for specific function names, addresses, or patterns.
    ```bash
    objdump -d -M intel <binary> | grep "main"
    ```
3.  **Combine with `c++filt`:** If you're analyzing C++ binaries, function names are often "mangled." Use `c++filt` to demangle them for readability.
    ```bash
    objdump -t <binary> | c++filt
    ```
4.  **Understand Sections:** Pay attention to sections like `.text` (code), `.data` (initialized data), `.rodata` (read-only data), and `.bss` (uninitialized data).
5.  **Look for System Calls/API Calls:** In disassembly, identify calls to common library functions (e.g., `printf`, `strcpy` on Linux; `MessageBoxA`, `CreateFileA` on Windows) as they often reveal program functionality.
6.  **Analyze Control Flow:** Identify `call`, `jmp`, `je`, `jne`, etc., instructions to map out the program's execution path.

#### Links to Documentation:

*   **GNU Binutils (objdump) Manual:** [https://sourceware.org/binutils/docs/objdump/](https://sourceware.org/binutils/docs/objdump/)
*   **Wikipedia - objdump:** [https://en.wikipedia.org/wiki/Objdump](https://en.wikipedia.org/wiki/Objdump)

Happy hacking!

## Working with Multiple Architectures (Linux & Windows)

This environment is equipped to handle both Linux and Windows binaries. Here are the best practices to follow:

### 1. Identify the Binary Type

Before you do anything else, use the `file` command to understand what kind of executable you have.

```bash
file <your_binary_file>
```

*   **Linux Executable:** The output will contain the word `ELF`. For example: `ELF 64-bit LSB executable, x86-64...`
*   **Windows Executable:** The output will contain `PE32` (for 32-bit) or `PE32+` (for 64-bit). For example: `PE32+ executable (console) x86-64, for MS Windows...`
*   **macOS Executable:** The output will contain `Mach-O`. These binaries **cannot** be run in this Linux environment.

### 2. Execute the Binary

How you run the binary depends on its type:

*   **For Linux ELF binaries:**
    Make it executable and run it directly.
    ```bash
    chmod +x ./my_linux_binary
    ./my_linux_binary
    ```

*   **For Windows PE binaries:**
    Use the `wine` command to run it.
    ```bash
    wine my_windows_binary.exe
    ```
    The first time you run `wine`, it will set up a default Windows environment in `~/.wine`.

### 3. Debugging

*   **Linux:** Use `gdb` for debugging.
    ```bash
    gdb ./my_linux_binary
    ```

*   **Windows:** You can use `radare2` or `gdb` with Wine for debugging.
    ```bash
    # Using radare2
    r2 -d wine my_windows_binary.exe

    # Using gdb with Wine
    wine gdb my_windows_binary.exe
    ```
For more advanced Windows debugging, reverse engineers often use dedicated Windows virtual machines with tools like x64dbg or IDA Pro, but Wine is excellent for initial analysis and many common tasks.
