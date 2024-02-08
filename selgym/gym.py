"""gym module"""

from os import path as ospath
from os import listdir, environ, getenv
from platform import system as sys_name
from shutil import which, rmtree
from screeninfo import get_monitors
from selenium.webdriver import Firefox as FirefoxWebDriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def cleanup_resources():
    """Cleanup unused temporary profile folders"""
    if sys_name() == "Windows":
        folder_path = ospath.join(environ["LOCALAPPDATA"], "Temp")
    elif sys_name() == "Linux":
        folder_path = "/tmp"
    else:
        return

    for filename in listdir(folder_path):
        full_path = ospath.join(folder_path, filename)
        if ospath.isdir(full_path):
            for prefix in ["tmp", "rust_mozpr"]:
                if filename.startswith(prefix):
                    rmtree(full_path)
                    break


def get_firefox_options(
    options: FirefoxOptions = None,
    firefox_profile: str = None,
    headless: bool = False,
    private_mode: bool = False,
) -> FirefoxOptions:
    """Returns chrome options instance with given configuration set"""
    if options is None:
        options = FirefoxOptions()

    if firefox_profile and isinstance(firefox_profile, str):
        options.profile = firefox_profile

    if headless:
        monitor = get_monitors()[0]

        # Headless window size patch
        environ["MOZ_HEADLESS_WIDTH"] = str(monitor.width)
        environ["MOZ_HEADLESS_HEIGHT"] = str(monitor.height)
        options.add_argument("--headless")
        options.add_argument(f"--window-size={monitor.width},{monitor.height}")
        options.add_argument("--start-maximized")

        # Disables volume
        options.set_preference("media.volume_scale", "0.0")

        # Disable browser cache
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False)

        # Disables WebRTC
        options.set_preference("media.peerconnection.enabled", False)

        # Disables homepage
        options.set_preference("browser.startup.homepage_welcome_url", "")
        options.set_preference("startup.homepage_welcome_url.additional", "")

        # Disable Firefox's new tab page suggestions and highlights
        options.set_preference("browser.newtabpage.enabled", False)
        options.set_preference("browser.sessionstore.resume_from_crash", False)

    if private_mode:
        options.set_preference("browser.privatebrowsing.autostart", True)

    return options


def set_firefox_proxy_opts(
    opts: FirefoxOptions, ip: str, port: int
) -> DesiredCapabilities:
    """Set proxy ip and port of FirefoxOptions (Unauthenticated)"""
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL

    proxy.http_proxy = f"{ip}:{port}"
    proxy.ssl_proxy = f"{ip}:{port}"

    opts.set_capability("proxy", proxy.to_capabilities())


def get_firefox_webdriver(*args, **kwargs) -> FirefoxWebDriver:
    """Constructor wrapper for Firefox webdriver"""

    if sys_name() == "Windows":
        # Check if firefox is in PATH
        default_windows_firefox_path = "C:\\Program Files\\Mozilla Firefox"
        if (
            not which("firefox")
            and environ["PATH"].find(default_windows_firefox_path) == -1
        ):
            environ["PATH"] += f";{default_windows_firefox_path}"

    return FirefoxWebDriver(*args, **kwargs)


def wait_element_by(
    driver: FirefoxWebDriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> WebElement:
    """Calls WebDriverWait on a locator, waiting for visibility"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by_type, match_str))
    )


def wait_elements_by(
    driver: FirefoxWebDriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> list[WebElement]:
    """Calls WebDriverWait on a locator, waiting for visibility of all elements"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_all_elements_located((by_type, match_str))
    )


def wait_hidden_element_by(
    driver: FirefoxWebDriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> WebElement:
    """Calls WebDriverWait on a locator, waiting for presence located"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by_type, match_str))
    )


def wait_hidden_elements_by(
    driver: FirefoxWebDriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> list[WebElement]:
    """Calls WebDriverWait on a locator, waiting for presence located for all elements"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by_type, match_str))
    )


def click_element(
    driver: FirefoxWebDriver,
    element: WebElement,
    timeout: int = 10,
) -> None:
    """Calls WebDriverWait on the element, and perform click when the element is clickable"""
    (WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))).click()


def scroll_into_element(driver: FirefoxWebDriver, element: WebElement):
    """Performs element.scrollIntoView()"""
    driver.execute_script("arguments[0].scrollIntoView();", element)


def scroll_element_to_bottom(driver: FirefoxWebDriver, element: WebElement):
    """Performs element.scrollIntoView() and assign element.scrollTop = element.scrollHeight"""
    scroll_into_element(driver, element)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)


def scroll_element_to_top(driver: FirefoxWebDriver, element: WebElement):
    """Performs element.scrollIntoView() and assign element.scrollTop = 0"""
    scroll_into_element(driver, element)
    driver.execute_script("arguments[0].scrollTop = 0", element)


def linux_default_firefox_profile_path() -> str:
    """Retrieves .default-release profile path on Linux"""
    profile_path = ospath.expanduser("~/.mozilla/firefox")

    if not ospath.exists(profile_path):
        raise RuntimeError(f"\nUnable to retrieve {profile_path} directory")

    for entry in listdir(profile_path):
        if entry.endswith(".default-release"):
            return ospath.join(profile_path, entry)
    return None


def mac_default_firefox_profile_path() -> str:
    """Retrieves .default-release profile path on MacOS"""
    profile_path = ospath.expanduser("~/Library/Application Support/Firefox/Profiles")

    if not ospath.exists(profile_path):
        raise RuntimeError(f"\nUnable to retrieve {profile_path} directory")

    for entry in listdir(profile_path):
        if entry.endswith(".default-release"):
            return ospath.join(profile_path, entry)
    return None


def win_default_firefox_profile_path() -> str:
    """Retrieves .default-release profile path on Windows"""
    profile_path = ospath.join(getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
    for entry in listdir(profile_path):
        if entry.endswith(".default-release"):
            return ospath.join(profile_path, entry)
    return None


def get_default_firefox_profile() -> str:
    """Retrieves .default-release profile path (cross compatible)"""
    if sys_name() == "Windows":
        return win_default_firefox_profile_path()
    if sys_name() == "Linux":
        return linux_default_firefox_profile_path()
    if sys_name() == "Darwin":
        return mac_default_firefox_profile_path()
    raise RuntimeError(f"Unsupported OS: {sys_name()}")


def dnd_file(
    driver: FirefoxWebDriver,
    element: WebElement,
    fpath: str,
):
    """Drag&Drop file into element"""
    dnd_script = """
        var target = arguments[0],
            offsetX = arguments[1],
            offsetY = arguments[2],
            document = target.ownerDocument || document,
            window = document.defaultView || window;

        var input = document.createElement('INPUT');
        input.type = 'file';
        input.onchange = function () {
        var rect = target.getBoundingClientRect(),
            x = rect.left + (offsetX || (rect.width >> 1)),
            y = rect.top + (offsetY || (rect.height >> 1)),
            dataTransfer = { files: this.files };

        ['dragenter', 'dragover', 'dragstart', 'dragend', 'drop'].forEach(function (name) {
            var evt = document.createEvent('MouseEvent');
            evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
            evt.dataTransfer = dataTransfer;
            target.dispatchEvent(evt);
        });

        setTimeout(function () { document.body.removeChild(input); }, 25);
        };
        document.body.appendChild(input);
        return input;
    """
    file_input = driver.execute_script(dnd_script, element, 0, 0)
    file_input.send_keys(fpath)


def dnd_file_alt(
    driver: FirefoxWebDriver,
    element: WebElement,
    fpath: str,
):
    """Alternative method for Drag&Drop ( in case dnd_file doesn't work )"""
    # Find the target element using the provided CSS selector

    # Read the content of the text file
    with open(fpath, "r", encoding="utf-8", errors="ignore") as file:
        file_content = file.read().replace("\n", "\\n").replace("'", "\\'")

    # Create a File object and trigger drop event
    js_code = f"""
        var content = '{file_content}';
        var file = new File([content], '{fpath}');
        var dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        var event = new DragEvent('drop', {{ bubbles: true, dataTransfer: dataTransfer }});
        arguments[0].dispatchEvent(event);
    """

    # Simulate the drag and drop action using ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    driver.execute_script(js_code, element)
