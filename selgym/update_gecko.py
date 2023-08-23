import os
import platform
import requests
import subprocess
import zipfile
import tarfile
import tempfile
import shutil


def get_current_geckodriver_version():
    try:
        result = subprocess.run(
            ["geckodriver", "--version"], capture_output=True, text=True
        )
        version_info = result.stdout.strip().split(" ")[1]
        return version_info.lstrip("v")
    except FileNotFoundError:
        return None


def get_latest_geckodriver_version():
    url = "https://github.com/mozilla/geckodriver/releases/latest"
    response = requests.get(url)
    latest_version = response.url.split("/")[-1]
    return latest_version.lstrip("v")


def download_geckodriver(version: str, destination: str):
    base_url = f"https://github.com/mozilla/geckodriver/releases/download/v{version}/"
    if platform.system() == "Windows":
        filename = f"geckodriver-v{version}-win64.zip"
    elif platform.system() == "Linux":
        filename = f"geckodriver-v{version}-linux64.tar.gz"
    else:
        raise OSError("\nUnsupported operating system")

    download_url = base_url + filename
    response = requests.get(download_url)
    with open(destination, "wb") as f:
        f.write(response.content)


def move_geckodriver_to_windows(geckodriver_path: str):
    if platform.system() == "Windows":
        shutil.move(geckodriver_path, "C:\\Windows")
    elif platform.system() == "Linux":
        shutil.move(geckodriver_path, os.path.expanduser("~/.local/bin"))
    else:
        raise OSError("\nUnsupported operating system")


def update_geckodriver(ask: bool = True, quiet: bool = False):
    latest_version = get_latest_geckodriver_version()
    current_version = get_current_geckodriver_version()

    qprint = lambda text: print(
        text if not quiet else "", end="\n" if not quiet else ""
    )

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
            temp_dir = tempfile.mkdtemp(dir=os.getcwd())
            try:
                zip_file_path = os.path.join(temp_dir, "geckodriver.zip")

                download_geckodriver(latest_version, zip_file_path)

                if platform.system() == "Windows":
                    geckodriver_path = os.path.join(temp_dir, "geckodriver.exe")
                    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif platform.system() == "Linux":
                    geckodriver_path = os.path.join(temp_dir, "geckodriver")
                    with tarfile.open(zip_file_path, "r:gz") as tar_ref:
                        tar_ref.extractall(temp_dir)
                else:
                    raise OSError("\nUnsupported operating system")

                qprint(f"\nGeckodriver version {latest_version} downloaded!")

                if current_version:
                    qprint(f"\nRemoving old version -> {current_version}...")
                    os.remove(shutil.which("geckodriver"))

                move_geckodriver_to_windows(geckodriver_path)
                qprint(f"\nGeckodriver has been updated to -> {latest_version} !")
            finally:
                shutil.rmtree(temp_dir)
    else:
        qprint(f"\nGeckodriver is already updated -> {shutil.which('geckodriver')}")


if __name__ == "__main__":
    update_geckodriver()
