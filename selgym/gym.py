import os
import platform
import screeninfo
import selenium
import shutil
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def cleanup_resources():
    if platform.system() == "Windows":
        folder_path = os.path.join(os.environ["LOCALAPPDATA"], "Temp")
    elif platform.system() == "Linux":
        folder_path = "/tmp"
    else:
        return

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isdir(full_path):
            for dirPrefix in ["tmp", "rust_mozpr"]:
                if filename.startswith(dirPrefix):
                    shutil.rmtree(full_path)
                    break


def get_firefox_options(
    firefox_profile: str = "", headless: bool = False, private_mode: bool = False
) -> selenium.webdriver.firefox.options.Options:
    """Returns chrome options instance with given configuration set"""
    options = FirefoxOptions()
    options.profile = (
        get_default_firefox_profile() if not firefox_profile else firefox_profile
    )

    if headless:
        monitor = screeninfo.get_monitors()[0]
        os.environ["MOZ_HEADLESS_WIDTH"] = str(monitor.width)
        os.environ["MOZ_HEADLESS_HEIGHT"] = str(monitor.height)
        options.add_argument("--headless")
        options.add_argument(f"--window-size={monitor.width},{monitor.height}")
        options.add_argument("--start-maximized")
        options.set_preference("media.volume_scale", "0.0")
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False)

    if private_mode:
        options.set_preference("browser.privatebrowsing.autostart", True)

    return options


def set_firefox_proxy_opts(
    opts: FirefoxOptions, ip: str, port: int
) -> DesiredCapabilities:
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL

    proxy.http_proxy = f"{ip}:{port}"
    proxy.ssl_proxy = f"{ip}:{port}"

    opts.set_capability("proxy", proxy.to_capabilities())


def get_firefox_webdriver(*args, **kwargs) -> selenium.webdriver:
    """Constructor wrapper for Firefox webdriver"""

    if platform.system() == "Windows":
        # Check if firefox is in PATH
        DEFAULT_WINDWOS_FIREFOX_PATH = "C:\\Program Files\\Mozilla Firefox"
        if (
            not shutil.which("firefox")
            and os.environ["PATH"].find(DEFAULT_WINDWOS_FIREFOX_PATH) == -1
        ):
            os.environ["PATH"] += f";{DEFAULT_WINDWOS_FIREFOX_PATH}"

    return selenium.webdriver.Firefox(*args, **kwargs)


def wait_element_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> selenium.webdriver.remote.webelement.WebElement:
    """Calls WebDriverWait on a locator, waiting for visibility"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by_type, match_str))
    )


def wait_elements_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> list[selenium.webdriver.remote.webelement.WebElement]:
    """Calls WebDriverWait on a locator, waiting for visibility of all elements"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_all_elements_located((by_type, match_str))
    )


def wait_hidden_element_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> selenium.webdriver.remote.webelement.WebElement:
    """Calls WebDriverWait on a locator, waiting for presence located"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by_type, match_str))
    )


def wait_hidden_elements_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> list[selenium.webdriver.remote.webelement.WebElement]:
    """Calls WebDriverWait on a locator, waiting for presence located for all elements"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by_type, match_str))
    )


def click_element(
    driver: selenium.webdriver,
    element: selenium.webdriver.remote.webelement.WebElement,
    timeout: int = 10,
) -> None:
    """Calls WebDriverWait on the element, and perform click when the element is clickable"""
    (WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))).click()


def scroll_element_to_bottom(
    driver: selenium.webdriver, element: selenium.webdriver.remote.webelement.WebElement
):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)


def scroll_element_to_top(
    driver: selenium.webdriver, element: selenium.webdriver.remote.webelement.WebElement
):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].scrollTop = 0", element)


def scroll_into_element(
    driver: selenium.webdriver, element: selenium.webdriver.remote.webelement.WebElement
):
    driver.execute_script("arguments[0].scrollIntoView();", element)


def linux_default_firefox_profile_path() -> str:
    profile_path = os.path.expanduser("~/.mozilla/firefox")

    if not os.path.exists(profile_path):
        raise RuntimeError(f"\nUnable to retrieve {profile_path} directory")

    for entry in os.listdir(profile_path):
        if entry.endswith(".default-release"):
            return os.path.join(profile_path, entry)
    return None


def win_default_firefox_profile_path() -> str:
    profile_path = os.path.join(os.getenv("APPDATA"), "Mozilla\Firefox\Profiles")
    for entry in os.listdir(profile_path):
        if entry.endswith(".default-release"):
            return os.path.join(profile_path, entry)
    return None


def get_default_firefox_profile() -> str:
    if platform.system() == "Windows":
        return win_default_firefox_profile_path
    elif platform.system() == "Linux":
        return linux_default_firefox_profile_path()
    return ""


def dnd_file(
    driver: selenium.webdriver,
    element: selenium.webdriver.remote.webelement.WebElement,
    fpath: str,
):
    __DRAG_AND_DROP_SCRIPT = """
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
    file_input = driver.execute_script(__DRAG_AND_DROP_SCRIPT, element, 0, 0)
    file_input.send_keys(fpath)


def dnd_file_alt(
    driver: selenium.webdriver,
    element: selenium.webdriver.remote.webelement.WebElement,
    fpath: str,
):
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
