[![Build Status](https://github.com/happticde/crackmes-playground/actions/workflows/ci-release.yml/badge.svg)](https://github.com/happticde/crackmes-playground/actions/workflows/ci-release.yml)
[![Latest Tag](https://img.shields.io/github/v/tag/happticde/crackmes-playground)](https://github.com/happticde/crackmes-playground/tags)
![Coverage](coverage.svg)

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
    docker compose run --rm crackmes-dev
    ```
    You will be dropped into a `bash` shell as the `user` inside the container. The `--rm` flag is good practice as it will automatically remove the container when you exit.

3.  **Your Workspace:**
    The `crackmes` directory in this project is mounted inside the container at `/home/user/crackmes`. Any files you put in the local `crackmes` directory will be available inside the container, and any changes you make inside the container will be reflected on your host machine.

## Tools Included

*   **`gdb`**: The GNU Debugger. Essential for dynamic analysis (running the program and inspecting its state).
*   **`radare2`**: A powerful suite of tools for static and dynamic analysis. It has a steeper learning curve but is incredibly versatile.
*   **`objdump`**: A powerful tool for static analysis, allowing you to inspect assembly code and other information from object files.
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
    ## Local Development Setup

This project uses `ruff` for linting and formatting. Here's how to set up your local environment to match the CI pipeline.

### 1. Install Dependencies

It's recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install all necessary dependencies
pip install -r crawler/requirements.txt
pip install -r crawler/requirements-dev.txt
```

### 2. Running Ruff Manually

You can run `ruff` from your terminal to check for issues or to format your code.

```bash
# Check for linting errors
ruff check crawler/

# Fix linting errors automatically (where possible)
ruff check crawler/ --fix

# Check if formatting is correct
ruff format crawler/ --check

# Format the code
ruff format crawler/
```

### 3. VS Code Integration (Recommended)

If you use Visual Studio Code, you can get real-time feedback and auto-formatting.

1.  **Install the Ruff Extension:**
    Search for and install the `charliermarsh.ruff` extension from the VS Code Marketplace.

2.  **Enable VS Code Settings:**
    This project includes a pre-configured `.vscode/settings.json` file to enable auto-fixing and auto-formatting on save with `ruff`. The `source.fixAll` setting is set to `"explicit"` which is the recommended setting. When you open this project in VS Code, it should automatically use these settings.

## Documentation & Resources

Here are some resources to help you on your journey.

### Assembly Language

*   **Intel x86 Assembly Reference:** [https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) (This is the official, very dense, but complete reference).
*   **A more friendly guide:** [https://www.cs.virginia.edu/~evans/cs216/guides/x86.html](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html)

### GDB (GNU Debugger)

GDB is an essential tool for dynamic analysis, allowing you to pause program execution, inspect memory and registers, and trace the flow of code.

#### Documentation & Resources

*   **Official GDB Manual:** [https://www.gnu.org/software/gdb/documentation/](https://www.gnu.org/software/gdb/documentation/)
*   **GDB Cheat Sheet:** [https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf)
*   **In-depth Tutorial:** [https://cs.cmu.edu/~gilbert/gdb/tutorial.html](https://cs.cmu.edu/~gilbert/gdb/tutorial.html)

#### Getting Started with GDB

1.  **Compile with Debug Symbols:** Before debugging, compile your program with the `-g` flag to include debugging information.
    ```bash
    gcc -g my_program.c -o my_program
    ```
2.  **Start a GDB Session:**
    ```bash
    gdb ./my_program
    ```
3.  **Set a Breakpoint:** Set a breakpoint to tell GDB where to pause execution. A good starting point is the `main` function.
    ```gdb
    break main
    ```
4.  **Run the Program:**
    ```gdb
    run
    ```
    Execution will stop at your breakpoint.
5.  **Step Through Code:** Use `next` to execute the next line (stepping over functions) or `step` (to step into functions).
6.  **Inspect Data:** Use `print <variable>` to check variable values and `info locals` to see all local variables.

#### Most Common Commands

| Command | Alias | Description |
| :--- | :--- | :--- |
| `run` | `r` | Start program execution. |
| `break <loc>` | `b` | Set a breakpoint at `<loc>` (e.g., `main`, `file.c:10`). |
| `continue` | `c` | Continue execution until the next breakpoint. |
| `next` | `n` | Execute the next line of code (steps **over** function calls). |
| `step` | `s` | Execute the next line of code (steps **into** function calls). |
| `print <var>` | `p` | Print the value of a variable or expression. |
| `backtrace` | `bt` | Show the current function call stack. |
| `list` | `l` | Display the source code around the current line. |
| `info break` | | Show all breakpoints. |
| `info locals` | | Display local variables in the current function. |
| `delete <n>` | `d` | Delete breakpoint number `<n>`. |
| `quit` | `q` | Exit GDB. |

#### Best Practices

*   **Use a `.gdbinit` file:** Create a `.gdbinit` file in your project or home directory to store custom commands and settings that you use frequently.
*   **Conditional Breakpoints:** Stop only when a specific condition is met (e.g., `break 15 if i == 10`). This is invaluable for debugging loops.
*   **Watchpoints:** Use `watch <variable>` to stop execution whenever the value of `<variable>` changes.
*   **Layouts:** Use `layout src` or `layout asm` to see the source code or disassembly alongside the command prompt. Press `Ctrl+X`, `A` to toggle.

### Radare2

The official GitHub link is [https://github.com/radareorg/radare2](https://github.com/radareorg/radare2).

#### Documentation & Resources

*   **Official radare2 Book:** [https://rada.re/n/book.html](https://rada.re/n/book.html)
*   **Community-driven Book:** [https://radare.gitbooks.io/radare2book/content/](https://radare.gitbooks.io/radare2book/content/)
*   **Radare2 Cheatsheet:** [https://github.com/radareorg/radare2/blob/master/doc/cheatsheet.md](https://github.com/radareorg/radare2/blob/master/doc/cheatsheet.md)

#### Getting Started with radare2

1.  **Installation:** The most reliable way to install radare2 is by following the official instructions on their GitHub page.
2.  **Initial Analysis:** Begin by opening your target binary with `radare2 <binary>` and running the `aaa` command to perform a full analysis. This will identify functions, strings, and symbols.
3.  **Basic Exploration:**
    *   `afl`: List all identified functions.
    *   `pdf`: Print the disassembly of the current function.
    *   `s <address>`: Seek to a specific address or symbol.
4.  **Visual Mode:** Use `VV` to enter the powerful graph-based visual mode for exploring the control flow of the program.
5.  **Practice:** The best way to learn is by doing. Experiment with the commands and try solving some simple crackmes.

#### Best Practices

*   **Define a Goal:** Know what you're looking for before you start.
*   **Save Your Work:** Use projects (`P` command) to save and resume your analysis sessions.
*   **Use the Debugger:** Start radare2 with the `-d` flag to use its built-in debugger.
*   **Annotate:** Use comments (`;`) and flags (`f`) to document your findings within your analysis.
*   **Scripting:** For repetitive tasks, leverage `r2pipe` to script your workflow in languages like Python.

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

## Dependency Management

This project uses [Renovate](https://github.com/renovatebot/renovate) to automate dependency updates.

### How it Works

*   **Weekly Checks:** Renovate will run every weekend to check for new versions of all dependencies (Python packages and GitHub Actions).
*   **Pull Requests:** If updates are found, Renovate will automatically create a pull request for each update.
*   **Auto-merging:** If the update is a `patch` or `minor` version change, and the CI pipeline passes, Renovate will automatically merge the pull request. Major version updates will require manual review and merging.

### What You Need to Do

Renovate is now automated via a GitHub Action (`.github/workflows/renovate.yml`). No manual setup or GitHub App installation is required. It will automatically run on a schedule and create pull requests for dependency updates.