"""update_gecko module"""
from os import path as ospath
from os import getcwd, remove
from platform import system as sys_name
from subprocess import run
from zipfile import ZipFile
from tarfile import open as tar_open
from shutil import move, which, rmtree
from tempfile import mkdtemp
from requests import get as http_get


def __get_current_geckodriver_version():
    try:
        result = run(
            ["geckodriver", "--version"], capture_output=True, text=True, check=False
        )
        version_info = result.stdout.strip().split(" ")[1]
        return version_info.lstrip("v")
    except FileNotFoundError:
        return None


def __get_latest_geckodriver_version():
    url = "https://github.com/mozilla/geckodriver/releases/latest"
    response = http_get(url, timeout=10)
    latest_version = response.url.split("/")[-1]
    return latest_version.lstrip("v")


def __download_geckodriver(version: str, destination: str):
    base_url = f"https://github.com/mozilla/geckodriver/releases/download/v{version}/"
    if sys_name() == "Windows":
        filename = f"geckodriver-v{version}-win64.zip"
    elif sys_name() == "Linux":
        filename = f"geckodriver-v{version}-linux64.tar.gz"
    else:
        raise OSError("\nUnsupported operating system")

    download_url = base_url + filename
    response = http_get(download_url, timeout=10)
    with open(destination, "wb") as f:
        f.write(response.content)


def __move_gecko_to_path(geckodriver_path: str, out_dir: str = None):
    if sys_name() == "Windows":
        if not out_dir or not ospath.isdir(out_dir):
            out_dir = "C:\\Windows"
        move(geckodriver_path, out_dir)
    elif sys_name() == "Linux":
        if not out_dir or not ospath.isdir(out_dir):
            out_dir = ospath.expanduser("~/.local/bin")
        move(geckodriver_path, out_dir)
    else:
        raise OSError("\nUnsupported operating system")


def update_geckodriver(ask: bool = True, out_dir: str = None, quiet: bool = False):
    """Automatically downloads and install geckodriver, inside `out_dir` folder.

    By default, if `out_dir` is omitted, it will install it either
    on C:/Windows or ~/.local/bin depending on the OS.
    """
    latest_version = __get_latest_geckodriver_version()
    current_version = __get_current_geckodriver_version()

    def qprint(text: str):
        if not quiet:
            print(text)

    qprint(f"\nCurrent Geckodriver -> {current_version}\nLatest -> {latest_version}")

    if current_version is None or latest_version != current_version:
        if (
            not ask
            or "y"
            == input(
                f"\nDo you want to download latest version -> {latest_version} ? (Press y)\n>>"
            )
            .lstrip()
            .rstrip()
            .lower()
        ):
            temp_dir = mkdtemp(dir=getcwd())
            try:
                zip_file_path = ospath.join(temp_dir, "geckodriver.zip")

                __download_geckodriver(latest_version, zip_file_path)

                if sys_name() == "Windows":
                    geckodriver_path = ospath.join(temp_dir, "geckodriver.exe")
                    with ZipFile(zip_file_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif sys_name() == "Linux":
                    geckodriver_path = ospath.join(temp_dir, "geckodriver")
                    with tar_open(zip_file_path, "r:gz") as tar_ref:
                        tar_ref.extractall(temp_dir)
                else:
                    raise OSError("\nUnsupported operating system")

                qprint(f"\nGeckodriver version {latest_version} downloaded!")

                if current_version:
                    qprint(f"\nRemoving old version -> {current_version}...")
                    remove(which("geckodriver"))

                __move_gecko_to_path(geckodriver_path, out_dir=out_dir)
                qprint(
                    f"\nGeckodriver {latest_version} has been installed into -> {out_dir}"
                )
            finally:
                rmtree(temp_dir)
    else:
        qprint(f"\nGeckodriver is already updated -> {which('geckodriver')}")


if __name__ == "__main__":
    update_geckodriver()
