#!/usr/bin/env python3

#####################
#     Verse FOX     #
#####################

import os
import sys
import json
import typing
import asyncio
import argparse
import warnings

import rich.console
import rich.traceback
import rich.progress
import rich.panel
import rich.live
import rich_argparse
import soupsieve
import aiohttp
import bs4

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
warnings.filterwarnings("ignore")

blank_string = ""

main_style = "magenta bold"

sys.stderr = open(os.devnull, "w")


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
    file_path: str
    folder_path: str
    selector: str
    worker_count: int
    timeout: int


def file_path_validator(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"File doesn't exists ! [FILE PATH: '{file_path}']")
    try:
        json.loads(read_file(file_path, mode="r"))
        return file_path
    except Exception as error:
        raise argparse.ArgumentTypeError(f"File is't valid ! [FILE PATH: '{file_path}'] \n ({error})")


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


def count_number_validator(count_number: str) -> int:
    digit_check = count_number.isdigit() and count_number.isascii()
    if not digit_check or int(count_number) <= 0:
        raise argparse.ArgumentTypeError(f"Count Number isn't valid ! [COUNT NUMBER: '{count_number}']")
    return int(count_number)


def timeout_value_validator(timeout_value: str) -> int:
    digit_check = timeout_value.isdigit() and timeout_value.isascii()
    if not digit_check or int(timeout_value) <= 0:
        raise argparse.ArgumentTypeError(f"Timeout Value isn't valid ! [TIMEOUT VALUE: '{timeout_value}']")
    return int(timeout_value)


argument_parser = custom_argument_parser(
    prog="verse-fox",
    formatter_class=rich_argparse.RichHelpFormatter,
    description="Scrap novel from website effortlessly",
    epilog="No way Home !",
    add_help=False,
)


argument_parser.add_argument(
    "--file-path",
    type=file_path_validator,
    metavar="FILE_PATH",
    help="File Path for novel chapter urls",
    required=True,
)

argument_parser.add_argument(
    "--folder-path",
    type=folder_path_validator,
    metavar="FOLDER_PATH",
    help="Folder Path for novel chapter texts",
    required=True,
)

argument_parser.add_argument(
    "--selector",
    type=selector_validator,
    metavar="SELECTOR",
    help="Selector for extracting text from html",
    required=True,
)

argument_parser.add_argument(
    "--worker-count",
    type=count_number_validator,
    default=5,
    help="Worker Count for Verse Vine",
    metavar="COUNT_NUMBER",
)

argument_parser.add_argument(
    "--timeout",
    type=timeout_value_validator,
    default=60,
    help="Timeout for Verse Vine",
    metavar="TIMEOUT_VALUE",
)

argument_parser.add_argument(
    "--help",
    action="help",
    help="Show this help message and exit",
)

argument = argument_parser.parse_args(namespace=custom_argument_namespace())


def read_file(file_path: str, mode: str) -> str | bytes:
    with open(file_path, mode) as file:
        return file.read()


def write_file(file_path: str, content: str | bytes, mode: str) -> None:
    with open(file_path, mode) as file:
        file.write(content)


async def worker(
    chapter_name: str,
    chapter_url: str,
    session: aiohttp.ClientSession,
    selector: soupsieve.SoupSieve,
    main_progress: rich.progress.Progress,
    main_task_id: rich.progress.TaskID,
    worker_semaphore: asyncio.Semaphore,
) -> None:
    async with worker_semaphore:
        client_timeout = aiohttp.ClientTimeout(total=argument.timeout)
        async with session.get(chapter_url, timeout=client_timeout, allow_redirects=True) as response:
            response.raise_for_status()
            html = await response.text()

        soup = bs4.BeautifulSoup(html, "html.parser")
        texts = selector.select(soup)
        assert texts, "No elements matched the selector !"
        text = blank_string.join(text.get_text(strip=True) for text in texts)

        file_path = os.path.join(argument.folder_path, f"{chapter_name}.txt")
        write_file(file_path, text, mode="w")

        console.print("[magenta]<verse-fox>[/magenta]", f"Scraped successfully ! [FILE NAME: '{chapter_name}']")
        main_progress.advance(main_task_id)


async def verse_vine(main_progress: rich.progress.Progress) -> None:
    os.makedirs(argument.folder_path, exist_ok=True)
    chapters: dict[str, str] = json.loads(read_file(argument.file_path, mode="r"))
    selector = soupsieve.compile(argument.selector)

    main_task_id = main_progress.add_task("TOTAL", total=len(chapters), style=main_style)
    worker_semaphore = asyncio.Semaphore(argument.worker_count)

    async with aiohttp.ClientSession() as session:
        tasks: list[typing.Coroutine[typing.Any, typing.Any, None]] = []
        for chapter_name, chapter_url in chapters.items():
            task = worker(chapter_name, chapter_url, session, selector, main_progress, main_task_id, worker_semaphore)
            tasks.append(task)
        await asyncio.gather(*tasks)


async def main() -> None:
    main_progress = rich.progress.Progress()
    main_panel = rich.panel.Panel(main_progress, style=main_style, width=60)
    live_group = rich.console.Group(blank_string, main_panel)
    with rich.live.Live(live_group, console=console, refresh_per_second=4, transient=True):
        await verse_vine(main_progress)


if __name__ == "__main__":
    asyncio.run(main())

# Final Version [line-length : 120]
