# Crawler Development

This directory contains the Python source code for the `get-crackme` command used in the parent Docker environment.

## Development Environment

The development environment is the running Docker container itself. This `crawler` directory is mounted as a volume into the container at `/home/user/crawler`.

This means you can edit the `crawler.py` script on your host machine, and the changes will be instantly available inside the container, so you don't need to rebuild the image for simple script changes.

## Managing Dependencies

Python dependencies are managed in the `requirements.txt` file.

If you need to add or update a dependency:
1.  Add the package name to `requirements.txt`.
2.  Rebuild the Docker image to install the new dependencies:
    ```bash
    docker compose build
    ```

## Testing Changes

You can test your changes to the script directly inside the container.

1.  **Start the container:**
    ```bash
    docker compose run --rm crackme-dev
    ```

2.  **Run the script:**
    You can either run the script directly or use the `get-crackme` command.
    ```bash
    # Run the script directly for testing
    python3 /home/user/crawler/crawler.py 685048992b84be7ea7743940

    # Test the installed command
    get-crackme 685048992b84be7ea7743940
    ```

## How It Works

The `crawler.py` script uses the following libraries:
-   `requests`: To fetch the HTML content of a crackme page.
-   `BeautifulSoup4`: To parse the HTML and extract the required information (details, description, comments, download link).
-   `argparse`: To handle command-line arguments.

The script constructs the full URL from the provided crackme ID, scrapes the data, downloads the associated file, and saves the text content into a `README.md` file.

## Testing

This project uses `pytest` for unit testing. The tests are located in the `crawler/tests` directory and are configured to ensure 100% code coverage. The `pytest.ini` file is also located in this directory.

### Running Tests Inside the Container

To run the tests, you have two options:

1.  **From the project root (`/home/user`) inside the container:**
    ```bash
    pytest -c crawler/pytest.ini crawler/tests
    ```

2.  **From the `crawler` directory (`/home/user/crawler`) inside the container:**
    ```bash
    cd crawler
    pytest
    ```

The test suite will automatically run, measure coverage, and fail if the coverage drops below 100%.

### Running Tests on Host Machine (for CI/CD)

For running tests directly on your host machine, especially for CI/CD pipelines, a `Makefile` has been provided in the project root.

1.  **Ensure Python 3 is installed** on your host machine.
2.  **Navigate to the project root** directory on your host.
3.  **Run the tests:**
    ```bash
    make test
    ```
    This command will automatically create a virtual environment (`.venv`), install all necessary Python dependencies (from `requirements.txt` and `requirements-dev.txt`), and then execute the `pytest` suite.

    **Specifying Python Version:**
    By default, `make install` will use the `python3` executable found in your system's PATH. If you want to use a specific Python version (e.g., Python 3.12), you can override it:
    ```bash
    make install PYTHON_VERSION=python3.12
    make test
    ```

You can also clean up the virtual environment and build artifacts with:
```bash
make clean
```

### Local Development (without Docker)

If you prefer to develop and test the `crawler.py` script directly on your host machine without using Docker, follow these steps:

1.  **Prerequisites:**
    *   Ensure you have Python 3.13 (or your preferred version) installed on your system.
    *   Ensure `make` is installed if you wish to use the provided `Makefile`.

2.  **Setup Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    # Create a virtual environment (e.g., using Python 3.13)
    python3.13 -m venv .venv

    # Activate the virtual environment
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install the required packages into your active virtual environment:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

4.  **Run the Script:**
    Once dependencies are installed, you can run the `crawler.py` script directly:
    ```bash
    python crawler.py <crackme_id> -o <output_directory>
    ```
    For example:
    ```bash
    python crawler.py 685048992b84be7ea7743940 -o crackmes
    ```

5.  **Run Tests:**
    With the virtual environment activated, you can run the tests using `pytest`:
    ```bash
    pytest -c crawler/pytest.ini crawler/tests
    ```

6.  **Using the `Makefile`:**
    Alternatively, you can use the provided `Makefile` to automate steps 2-5.
    ```bash
    # Install dependencies and create venv (defaults to python3.13)
    make install

    # Run tests
    make test

    # Clean up
    make clean
    ```
    You can specify a different Python version for the virtual environment:
    ```bash
    make install PYTHON_VERSION=python3.12
    ```

