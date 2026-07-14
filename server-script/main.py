#!/usr/bin/env python3

########################
#     Verse Captor     #
########################

import os
import sys
import json
import typing
import asyncio
import argparse
import urllib.parse

import rich.console
import rich.traceback
import rich_argparse
import soupsieve
import websockets
import bs4

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
halt_event = asyncio.Event()
sys.stderr = open(os.devnull, "w")

blank_line = "\n"
target_url = "https://example.com/"
current_count = 0


@typing.overload
def read_file(file_path: str, mode: typing.Literal["r"]) -> str: ...
@typing.overload
def read_file(file_path: str, mode: typing.Literal["rb"]) -> bytes: ...


@typing.overload
def write_file(file_path: str, content: str, mode: typing.Literal["w"]) -> None: ...
@typing.overload
def write_file(file_path: str, content: str, mode: typing.Literal["a"]) -> None: ...
@typing.overload
def write_file(file_path: str, content: bytes, mode: typing.Literal["wb"]) -> None: ...
@typing.overload
def write_file(file_path: str, content: bytes, mode: typing.Literal["ab"]) -> None: ...


class custom_argument_parser(argparse.ArgumentParser):
    def error(self, message: str) -> typing.NoReturn:
        self.print_help()
        console.print("\n" + "#======#_#======#" + "\n")
        console.print(message.capitalize())
        sys.exit(2)


class custom_argument_namespace(argparse.Namespace):
    start_url: str
    stop_url: str
    url_selector: str
    file_path: str
    folder_path: str
    text_selector: str
    show_locals: str


def url_validator(url: str) -> str:
    parse_result = urllib.parse.urlparse(url)
    if not (parse_result.scheme in ("http", "https") and parse_result.netloc):
        raise argparse.ArgumentTypeError(f"URL isn't valid! [URL: '{url}']")
    return url


def file_path_validator(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"File doesn't exist ! [FILE PATH: '{file_path}']")
    return file_path


def folder_path_validator(folder_path: str) -> str:
    if os.path.isdir(folder_path) and len(os.listdir(folder_path)) != 0:
        raise argparse.ArgumentTypeError(f"Folder isn't empty ! [FOLDER PATH: '{folder_path}']")
    return folder_path


def selector_validator(selector: str) -> str:
    try:
        soupsieve.compile(selector)
        return selector
    except Exception as error:
        raise argparse.ArgumentTypeError(f"Selector isn't valid ! [SELECTOR: '{selector}']  \n ({error})")


argument_parser = custom_argument_parser(
    prog="verse-captor",
    formatter_class=rich_argparse.RichHelpFormatter,
    description="Scrap novel from website dynamically",
    epilog="No way Home !",
    add_help=False,
)

argument_parser.add_argument(
    "--start-url",
    type=url_validator,
    metavar="URL",
    help="Start URL for scaping novel chapter",
)

argument_parser.add_argument(
    "--stop-url",
    type=url_validator,
    metavar="URL",
    help="Stop URL for scaping novel chapter",
)

argument_parser.add_argument(
    "--url-selector",
    type=selector_validator,
    metavar="SELECTOR",
    help="Selector for extracting url from html",
)

argument_parser.add_argument(
    "--file-path",
    type=file_path_validator,
    metavar="FILE_PATH",
    help="File Path for novel chapter urls",
)

argument_parser.add_argument(
    "--folder-path",
    type=folder_path_validator,
    metavar="FOLDER_PATH",
    help="Folder Path for novel chapter texts",
    required=True,
)

argument_parser.add_argument(
    "--text-selector",
    type=selector_validator,
    metavar="SELECTOR",
    help="Selector for extracting text from html",
)

argument_parser.add_argument(
    "--show-locals",
    action="store_true",
    help="Show local variables for rich.traceback",
)

argument_parser.add_argument(
    "--help",
    action="help",
    help="Show this help message and exit",
)

argument = argument_parser.parse_args(namespace=custom_argument_namespace())

_file_path = argument.file_path is not None
_start_url = argument.start_url is not None
_stop_url = argument.stop_url is not None
_url_selector = argument.url_selector is not None

_mode_file = _file_path and not (_start_url or _stop_url or _url_selector)
_mode_url = (_start_url and _stop_url and _url_selector) and not _file_path

if _mode_file == _mode_url:
    argument_parser.error("Required arguments: --file-path or (--start-url and --stop-url and --url-selector)")

rich.traceback.install(console=console, show_locals=argument.show_locals)


def read_file(file_path: str, mode: str) -> str | bytes:
    with open(file_path, mode) as file:
        return file.read()


def write_file(file_path: str, content: str | bytes, mode: str) -> None:
    with open(file_path, mode) as file:
        file.write(content)


async def request_work(websocket: websockets.ServerConnection, data: dict) -> None:
    await websocket.send(json.dumps({"type": "response_work", "data": {"target_url": target_url}}))


async def submit_work(websocket: websockets.ServerConnection, data: dict) -> None:
    global target_url, current_count
    assert target_url == data["target_url"], "Mismatch between target urls !"
    assert "target_content" in data, "Target Content isn't found !"
    if argument.text_selector:
        soup = bs4.BeautifulSoup(data["target_content"], "html.parser")
        text_selector = soupsieve.compile(argument.text_selector)
        text_elements = text_selector.select(soup)
        assert len(text_elements) > 0, "No text element found !"
        text = blank_line.join([element.get_text(separator=blank_line, strip=True) for element in text_elements])
        text = blank_line.join([line.strip() for line in text.split(blank_line) if line.strip() != ""])
        assert len(text) > 0, "No text found in the text elements !"
        write_file(os.path.join(argument.folder_path, f"chapter-{current_count}.txt"), text, "w")
        console.print(f"SUCCESS: chapter-{current_count}.txt ! [{target_url}]")
    else:
        write_file(os.path.join(argument.folder_path, f"chapter-{current_count}.html"), data["target_content"], "w")
        console.print(f"SUCCESS: chapter-{current_count}.html ! [{target_url}]")
    if _mode_url:
        url_selector = soupsieve.compile(argument.url_selector)
        url_elements = url_selector.select(soup)
        if target_url == argument.stop_url:
            await websocket.close()
            return halt_event.set()
        assert len(url_elements) > 0, "No url element found !"
        url = url_elements[0]["href"].strip()
        assert len(url) > 0, "No url found in the url element !"
        target_url = urllib.parse.urljoin(target_url, str(url))
    elif _mode_file:
        chapter_urls = read_file(argument.file_path, "r").split("\n")
        if chapter_urls.index(target_url) == len(chapter_urls) - 1:
            await websocket.close()
            return halt_event.set()
        target_url = chapter_urls[chapter_urls.index(target_url) + 1]
    else:
        raise Exception("Mode values aren't as usual !")
    current_count += 1


async def verse_captor(websocket: websockets.ServerConnection):
    handler_mapping = {
        "request_work": request_work,
        "submit_work": submit_work,
    }
    async for message in websocket:
        if halt_event.is_set():
            return await websocket.close()
        try:
            message = json.loads(message)
            assert "type" in message, "Message Type isn't found !"
            assert "data" in message, "Message Data isn't found !"
            assert message["type"] in handler_mapping, "Message Type isn't known !"
            if message["type"] in handler_mapping:
                await handler_mapping[message["type"]](websocket, message["data"])
        except Exception:
            console.print_exception()


async def main() -> None:
    global target_url, current_count
    current_count = current_count or 1
    if _mode_url:
        target_url = argument.start_url
    elif _mode_file:
        chapter_urls = read_file(argument.file_path, "r").split("\n")
        assert len(chapter_urls) == len(set(chapter_urls)), "Chapter urls have duplicates !"
        target_url = chapter_urls[0]
    else:
        raise Exception("Mode values aren't as usual !")
    os.makedirs(argument.folder_path, exist_ok=True)
    server = await websockets.serve(verse_captor, "127.0.0.1", 6969)
    console.print("SERVER IS RUNNING ! [127.0.0.1:6969]")
    await halt_event.wait()
    server.close()
    await server.wait_closed()
    console.print("SERVER IS STOPPED !")


if __name__ == "__main__":
    asyncio.run(main())
