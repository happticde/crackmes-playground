"""
Unit tests for the crawler.py script.
"""

import sys
import os # Import os
from unittest.mock import MagicMock, call
import textwrap # Import textwrap
import pathlib # Import pathlib
import zipfile # Import zipfile

import pytest
import requests
from bs4 import BeautifulSoup, Tag

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import crawler # Reverted import statement


@pytest.fixture
def mock_requests(mocker):
    """Fixture to mock requests.get."""
    return mocker.patch("requests.get")


@pytest.fixture
def mock_open(mocker):
    """Fixture to mock builtins.open."""
    return mocker.patch("builtins.open", mocker.mock_open())


@pytest.fixture
def mock_makedirs(mocker):
    """Fixture to mock os.makedirs."""
    return mocker.patch("os.makedirs")


@pytest.fixture
def mock_sys_exit(mocker):
    """Fixture to mock sys.exit."""
    return mocker.patch("sys.exit")


@pytest.fixture
def sample_html_complete():
    """Fixture for a complete HTML page."""
    return """
    <html>
        <body>
            <h3><a href="/user/testuser">testuser</a>'s Test Crackme</h3>
            <div class="columns panel-background">
                <div class="column col-3">
                    <p>Author:<br> <a href="/user/testuser">testuser</a></p>
                </div>
                <div class="column col-3">
                    <p>Language:<br> C++</p>
                </div>
                <div class="column col-3">
                    <p>Platform:<br> Linux</p>
                </div>
            </div>
            <p><b>Description</b></p>
            <p><span style="white-space: pre-line">A test description.</span></p>
            <a href="/download/12345" class="btn-download">Download</a>
            <div id="comments">
                <p><a href="/user/author1">author1</a> on 1:00 PM 01/01/2025: <span style="white-space: pre-line">comment1</span></p>
                <p><a href="/user/author2">author2</a> on 2:00 PM 01/01/2025: <span style="white-space: pre-line">comment2</span></p>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_minimal():
    """Fixture for a minimal HTML page with missing elements."""
    return """
    <html>
        <body>
            <h2>Minimal Crackme</h2>
        </body>
    </html>
    """

@pytest.fixture
def sample_html_provided_from_file(request): # Add request as an argument
    """Fixture for the HTML content provided by the user, read from a file."""
    # Use request.fspath to get the path of the test file
    test_file_dir = os.path.dirname(request.fspath)
    file_path = os.path.join(test_file_dir, "html_samples", "sample_provided.html")
    print(f"File path: {file_path}") # Debug print
    try:
        html_content = pathlib.Path(file_path).read_text(encoding="utf-8")
        print(f"Read HTML content length: {len(html_content)}") # Debug print
        return html_content
    except Exception as e:
        print(f"Error reading file in fixture: {e}", file=sys.stderr)
def test_download_file_request_exception(mock_requests, capsys):
    """Test download_file handles requests.exceptions.RequestException."""
    mock_requests.side_effect = requests.exceptions.RequestException("Network Error")
    result = crawler.download_file("http://fakeurl.com/test.zip")
    assert result is None
    captured = capsys.readouterr()
    assert "Error: Could not download file" in captured.err
    assert "Network Error" in captured.err


def test_download_file_raise_for_status_failure(mocker, capsys):
    """Test download_file handles requests.exceptions.RequestException when raise_for_status fails."""
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Status Error")
    mocker.patch("requests.get", return_value=mock_response)
    
    result = crawler.download_file("http://fakeurl.com/test.zip")
    assert result is None
    captured = capsys.readouterr()
    assert "Error: Could not download file" in captured.err
    assert "Status Error" in captured.err

# --- Tests for unzip_file ---
def test_unzip_file_success_with_password(mocker, tmp_path):
    """Test unzip_file successfully unzips a file with the correct password."""
    zip_filepath = tmp_path / "dummy_protected.zip" # Just a dummy path
    password = "infected"
    base_extract_dir = tmp_path / "extracted"
    
    mock_zipfile_class = mocker.MagicMock()
    mock_zipfile_instance = mock_zipfile_class.return_value.__enter__.return_value
    mock_zipfile_instance.extractall.return_value = None # No error
    mock_zipfile_instance.namelist.return_value = ["test_file.txt"] # Simulate content
    
    mocker.patch('crawler.zipfile.ZipFile', new=mock_zipfile_class)
    
    success = crawler.unzip_file(str(zip_filepath), password=password, extract_dir=str(base_extract_dir))
    
    assert success
    mock_zipfile_class.assert_called_once_with(str(zip_filepath), 'r')
    mock_zipfile_instance.extractall.assert_called_once_with(
        path=str(base_extract_dir / "crackme"), pwd=password.encode('utf-8')
    )
def test_unzip_file_incorrect_password(mocker, tmp_path, capsys):
    """Test unzip_file handles incorrect passwords."""
    zip_filepath = tmp_path / "dummy_protected.zip" # Just a dummy path, no real file needed
    incorrect_password = "wrong_password"
    base_extract_dir = tmp_path / "extracted"
    
    # Mock the ZipFile class directly
    mock_zipfile_class = mocker.MagicMock()
    # Configure the mock instance returned by the context manager
    mock_zipfile_instance = mock_zipfile_class.return_value.__enter__.return_value
    mock_zipfile_instance.extractall.side_effect = RuntimeError("Bad password")
    
    mocker.patch('crawler.zipfile.ZipFile', new=mock_zipfile_class) # Patch the class itself
    
    success = crawler.unzip_file(str(zip_filepath), password=incorrect_password, extract_dir=str(base_extract_dir))
    
    assert not success
    captured = capsys.readouterr()
    assert "Error unzipping" in captured.err
    assert "Incorrect password?" in captured.err
    mock_zipfile_class.assert_called_once_with(str(zip_filepath), 'r')
    mock_zipfile_instance.extractall.assert_called_once_with(
        path=str(base_extract_dir / "crackme"), pwd=incorrect_password.encode('utf-8')
    )


def test_unzip_file_no_password(mocker, tmp_path):
    """Test unzip_file unzips a file without a password (if it's not password protected)."""
    zip_filepath = tmp_path / "dummy_unprotected.zip"
    base_extract_dir = tmp_path / "extracted_no_pwd"
    
    mock_zipfile_class = mocker.MagicMock()
    mock_zipfile_instance = mock_zipfile_class.return_value.__enter__.return_value
    mock_zipfile_instance.extractall.return_value = None
    mock_zipfile_instance.namelist.return_value = ["test_file.txt"]
    
    mocker.patch('crawler.zipfile.ZipFile', new=mock_zipfile_class)
    
    success = crawler.unzip_file(str(zip_filepath), extract_dir=str(base_extract_dir))
    
    assert success
    mock_zipfile_class.assert_called_once_with(str(zip_filepath), 'r')
    mock_zipfile_instance.extractall.assert_called_once_with(
        path=str(base_extract_dir / "crackme") # No password provided
    )


def test_unzip_file_bad_zip_file(mocker, tmp_path, capsys):
    """Test unzip_file handles a bad zip file."""
    zip_filepath = tmp_path / "bad.zip"
    base_extract_dir = tmp_path / "extracted"

    mock_zipfile_class = mocker.MagicMock()
    mock_zipfile_class.side_effect = zipfile.BadZipFile("Bad zip file")
    mocker.patch('crawler.zipfile.ZipFile', new=mock_zipfile_class)
    
    success = crawler.unzip_file(str(zip_filepath), extract_dir=str(base_extract_dir))
    
    assert not success
    captured = capsys.readouterr()
    assert f"Error: {zip_filepath} is a bad zip file." in captured.err
    mock_zipfile_class.assert_called_once_with(str(zip_filepath), 'r')


def test_unzip_file_general_exception(mocker, tmp_path, capsys):
    """Test unzip_file handles a general exception during unzipping."""
    zip_filepath = tmp_path / "error.zip"
    base_extract_dir = tmp_path / "extracted"

    mock_zipfile_class = mocker.MagicMock()
    mock_zipfile_class.side_effect = Exception("Generic error")
    mocker.patch('crawler.zipfile.ZipFile', new=mock_zipfile_class)
    
    success = crawler.unzip_file(str(zip_filepath), extract_dir=str(base_extract_dir))
    
    assert not success
    captured = capsys.readouterr()
    assert f"An unexpected error occurred while unzipping {zip_filepath}: Generic error" in captured.err
    mock_zipfile_class.assert_called_once_with(str(zip_filepath), 'r')


def test_unzip_file_recursive_unzip(mocker, tmp_path):
    """Test unzip_file recursively unzips nested zip files."""
    outer_zip_filepath = tmp_path / "outer.zip"
    inner_zip_filepath = tmp_path / "extracted/crackme/inner.zip"
    base_extract_dir = tmp_path / "extracted"
    final_extract_dir = base_extract_dir / "crackme"
    
    # Create dummy zip files
    with zipfile.ZipFile(outer_zip_filepath, 'w') as zf:
        zf.writestr("inner.zip", b"dummy inner zip content")
    
    # Mock the ZipFile class
    mock_zipfile_class = mocker.MagicMock()
    
    # Mock the instances returned by the context manager for outer and inner zips
    mock_outer_zip_instance = mocker.MagicMock()
    mock_outer_zip_instance.namelist.return_value = ["inner.zip"]
    
    mock_inner_zip_instance = mocker.MagicMock()
    mock_inner_zip_instance.namelist.return_value = ["nested_file.txt"]

    # Configure the side_effect for the __enter__ method of the mocked ZipFile class
    mock_zipfile_class.return_value.__enter__.side_effect = [
        mock_outer_zip_instance,
        mock_inner_zip_instance
    ]
    
    mocker.patch('crawler.zipfile.ZipFile', new=mock_zipfile_class)
    mocker.patch('os.path.isfile', side_effect=lambda p: p == str(inner_zip_filepath)) # Mock isfile for inner.zip
    
    success = crawler.unzip_file(str(outer_zip_filepath), extract_dir=str(base_extract_dir))
    
    assert success
    
    # Assert that ZipFile was called with the correct paths
    assert mocker.call(str(outer_zip_filepath), 'r') in mock_zipfile_class.call_args_list
    assert mocker.call(str(inner_zip_filepath), 'r') in mock_zipfile_class.call_args_list

    # Assert extractall was called on the correct instances
    mock_outer_zip_instance.extractall.assert_called_once_with(path=str(final_extract_dir))
    mock_inner_zip_instance.extractall.assert_called_once_with(path=str(final_extract_dir / "crackme"))

# --- Tests for generate_markdown ---
def test_generate_markdown_full():
    """Test generate_markdown with full data."""
    md = crawler.generate_markdown(
        title="My Title",
        details={"Lang": "C"},
        description="My Desc",
    )
    assert "# My Title" in md
    assert "- **Lang:** C" in md
    assert "> My Desc" in md

# --- Tests for scrape_crackme ---
def test_scrape_crackme_complete(mocker, mock_makedirs, mock_open, sample_html_complete, tmp_path):
    """Test scrape_crackme with a complete HTML page."""
    mocker.patch("requests.get").return_value.text = sample_html_complete
    
    # Mock download_file to return a dummy zip file path
    dummy_zip_path = tmp_path / "dummy.zip"
    dummy_zip_path.write_bytes(b"dummy zip content") # Create a dummy zip file
    mock_download_file = mocker.patch("crawler.download_file", return_value=str(dummy_zip_path))
    
    mock_unzip_file = mocker.patch("crawler.unzip_file", return_value=True) # Mock unzip_file to succeed

    crawler.scrape_crackme("123", str(tmp_path))

    # Check directory creation
    # Expect "Test_Crackme" because safe_title replaces spaces with underscores
    mock_makedirs.assert_called_once_with(str(tmp_path / "testuser_Test_Crackme"), exist_ok=True)
    
    # Check download was called
    mock_download_file.assert_called_once() # Use the stored mock
    
    # Check unzip_file was called
    mock_unzip_file.assert_called_once_with(str(dummy_zip_path), password="crackmes.one")

    # Check markdown file was written
    mock_open.assert_called_once_with(str(tmp_path / "testuser_Test_Crackme" / "README.md"), "w", encoding="utf-8")
    handle = mock_open()
    written_content = handle.write.call_args[0][0]
    assert "# Test Crackme" in written_content
    assert "- **Language:** C++" in written_content
    assert "- **Platform:** Linux" in written_content
    assert "> A test description." in written_content



def test_scrape_crackme_minimal(mocker, mock_makedirs, mock_open, sample_html_minimal, tmp_path):
    """Test scrape_crackme with a minimal HTML page."""
    mocker.patch("requests.get").return_value.text = sample_html_minimal
    mocker.patch("crawler.download_file") # Store mock in variable

    with pytest.raises(SystemExit) as excinfo:
        crawler.scrape_crackme("123", str(tmp_path))
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 1


def test_scrape_crackme_get_soup_fails(mocker, tmp_path):
    """Test scrape_crackme exits if get_soup returns None."""
    mocker.patch("crawler.get_soup", return_value=None)
    with pytest.raises(SystemExit) as excinfo:
        crawler.scrape_crackme("123", str(tmp_path))
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 1


def test_scrape_crackme_no_h3_tag(mocker, tmp_path, capsys):
    """Test scrape_crackme exits if no h3 tag is found."""
    mock_soup_instance = mocker.MagicMock()
    mock_soup_instance.find.return_value = None # Mock find('h3') to return None
    mocker.patch("crawler.get_soup", return_value=mock_soup_instance)
    
    with pytest.raises(SystemExit) as excinfo:
        crawler.scrape_crackme("123", str(tmp_path))
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Could not find main title/author tag." in captured.err

def test_scrape_crackme_io_error(mocker, mock_open, sample_html_complete, tmp_path, mock_sys_exit):
    """Test scrape_crackme exits if writing the markdown file fails."""
    mocker.patch("requests.get").return_value.text = sample_html_complete
    mocker.patch("crawler.download_file")
    mocker.patch("os.makedirs", return_value=None) # Ensure makedirs succeeds
    
    mock_open.side_effect = IOError("Permission denied")

    crawler.scrape_crackme("123", str(tmp_path))
    mock_sys_exit.assert_called_once_with(1)


def test_scrape_crackme_no_description_span(mocker, tmp_path, capsys):
    """Test scrape_crackme handles the case where the description span is not found."""
    mock_soup_instance = mocker.MagicMock()
    
    # Mock the h3_tag and its text attribute
    mock_h3_tag = mocker.MagicMock(spec=Tag)
    mock_h3_tag.text.strip.return_value = "testuser's Test Crackme"
    
    # Mock the panel_background_div and its find_all method
    mock_panel_background_div = mocker.MagicMock(spec=Tag)
    mock_panel_background_div.find_all.return_value = [] # No detail columns
    
    # Mock the description_header_p
    mock_description_header_p = mocker.MagicMock(spec=Tag)
    
    # Mock description_span to be a Tag, but its inner span to be None
    mock_description_span = mocker.MagicMock(spec=Tag)
    mock_description_span.find.return_value = None # final_description_text will be None
    mock_description_span.text.strip.return_value = "Description fallback text." # This will be used
    mock_description_header_p.find_next_sibling.return_value = mock_description_span
    
    # Configure the side_effect for soup.find
    # The order of calls to soup.find is: 'h3', 'div.columns.panel-background', 'p.Description', 'a.btn-download'
    mock_soup_instance.find.side_effect = [
        mock_h3_tag, # For h3_tag
        mock_panel_background_div, # For panel_background_div
        mock_description_header_p, # For description_header_p
        None # For download_link
    ]
    mocker.patch("crawler.get_soup", return_value=mock_soup_instance)
    mocker.patch("crawler.download_file", return_value=None) # No download file
    
    crawler.scrape_crackme("123", str(tmp_path))
    
    captured = capsys.readouterr()
    assert "Warning: Could not find download link." in captured.err # Still expect this warning
    # No specific assertion for description fallback, as it defaults to empty string.


def test_scrape_crackme_no_download_link(mocker, mock_makedirs, mock_open, sample_html_complete, tmp_path, capsys):
    """Test scrape_crackme handles the case where no download link is found."""
    mock_soup_instance = mocker.MagicMock()
    
    # Mock the h3_tag and its text attribute
    mock_h3_tag = mocker.MagicMock(spec=Tag)
    mock_h3_tag.text.strip.return_value = "testuser's Test Crackme"
    
    # Mock the panel_background_div and its find_all method
    mock_panel_background_div = mocker.MagicMock(spec=Tag)
    mock_panel_background_div.find_all.return_value = [] # No detail columns
    
    # Mock the description_header_p and its find_next_sibling method
    mock_description_header_p = mocker.MagicMock(spec=Tag)
    mock_description_span = mocker.MagicMock(spec=Tag)
    mock_final_description_text = mocker.MagicMock(spec=Tag)
    mock_final_description_text.text.strip.return_value = "A test description."
    mock_description_span.find.return_value = mock_final_description_text
    mock_description_header_p.find_next_sibling.return_value = mock_description_span

    # Configure the side_effect for soup.find
    # The order of calls to soup.find is: 'h3', 'div.columns.panel-background', 'p.Description', 'a.btn-download'
    mock_soup_instance.find.side_effect = [
        mock_h3_tag, # For h3_tag
        mock_panel_background_div, # For panel_background_div
        mock_description_header_p, # For description_header_p
        None # For download_link
    ]
    mocker.patch("crawler.get_soup", return_value=mock_soup_instance)
    
    crawler.scrape_crackme("123", str(tmp_path))
    
    captured = capsys.readouterr()
    assert "Warning: Could not find download link." in captured.err


# --- Tests for main ---
def test_main(mocker):
    """Test the main function parses args and calls scrape_crackme."""
    mock_scrape = mocker.patch("crawler.scrape_crackme")
    mocker.patch("sys.argv", ["crawler.py", "some_id", "-o", "some_dir", "-p", "test_pwd"])
    
    crawler.main()
    
    mock_scrape.assert_called_once_with("some_id", "some_dir", "test_pwd")

def test_main_no_password(mocker):
    """Test the main function parses args and calls scrape_crackme without a password."""
    mock_scrape = mocker.patch("crawler.scrape_crackme")
    mocker.patch("sys.argv", ["crawler.py", "some_id", "-o", "some_dir"])
    
    crawler.main()
    
    mock_scrape.assert_called_once_with("some_id", "some_dir", None)

def test_scrape_crackme_with_cli_password(mocker, mock_makedirs, mock_open, sample_html_complete, tmp_path):
    """Test scrape_crackme uses the password provided via CLI."""
    mocker.patch("requests.get").return_value.text = sample_html_complete
    
    dummy_zip_path = tmp_path / "dummy.zip"
    dummy_zip_path.write_bytes(b"dummy zip content")
    mock_download_file = mocker.patch("crawler.download_file", return_value=str(dummy_zip_path))
    
    mock_unzip_file = mocker.patch("crawler.unzip_file", return_value=True)

    crackme_id = "123"
    output_dir = str(tmp_path)
    cli_password = "my_secret_password"
    crawler.scrape_crackme(crackme_id, output_dir, password=cli_password)

    mock_download_file.assert_called_once()
    mock_unzip_file.assert_called_once_with(str(dummy_zip_path), password=cli_password)


def test_scrape_crackme_with_default_passwords_success(mocker, mock_makedirs, mock_open, sample_html_complete, tmp_path):
    """Test scrape_crackme tries default passwords when no CLI password is given and one succeeds."""
    mocker.patch("requests.get").return_value.text = sample_html_complete
    
    dummy_zip_path = tmp_path / "dummy.zip"
    dummy_zip_path.write_bytes(b"dummy zip content")
    mock_download_file = mocker.patch("crawler.download_file", return_value=str(dummy_zip_path))
    
    # Mock unzip_file to fail for the first default, then succeed for the second
    mock_unzip_file = mocker.patch("crawler.unzip_file", side_effect=[False, True])

    crackme_id = "123"
    output_dir = str(tmp_path)
    crawler.scrape_crackme(crackme_id, output_dir, password=None)

    mock_download_file.assert_called_once()
    # Assert calls for default passwords
    expected_calls = [
        mocker.call(str(dummy_zip_path), password="crackmes.one"),
        mocker.call(str(dummy_zip_path), password="crackmes.de"),
    ]
    mock_unzip_file.assert_has_calls(expected_calls)
    assert mock_unzip_file.call_count == 2 # Called twice (first default fails, second succeeds)


def test_scrape_crackme_with_default_passwords_failure(mocker, mock_makedirs, mock_open, sample_html_complete, tmp_path, capsys):
    """Test scrape_crackme tries default passwords and then without password, when all fail."""
    mocker.patch("requests.get").return_value.text = sample_html_complete
    
    dummy_zip_path = tmp_path / "dummy.zip"
    dummy_zip_path.write_bytes(b"dummy zip content")
    mock_download_file = mocker.patch("crawler.download_file", return_value=str(dummy_zip_path))
    
    # Mock unzip_file to fail for all attempts
    mock_unzip_file = mocker.patch("crawler.unzip_file", return_value=False)

    crackme_id = "123"
    output_dir = str(tmp_path)
    crawler.scrape_crackme(crackme_id, output_dir, password=None)

    mock_download_file.assert_called_once()
    # Assert calls for default passwords and then without password
    expected_calls = [
        mocker.call(str(dummy_zip_path), password="crackmes.one"),
        mocker.call(str(dummy_zip_path), password="crackmes.de"),
        mocker.call(str(dummy_zip_path)), # Final attempt without password
    ]
    mock_unzip_file.assert_has_calls(expected_calls)
    assert mock_unzip_file.call_count == 3 # Called three times
    captured = capsys.readouterr()
    assert "Warning: Could not unzip" in captured.err
    assert "without password." in captured.err