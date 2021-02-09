import json
import os
import platform
import random
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta
from os.path import abspath, dirname, join
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


class Configuration:

    DEFAULT_ENGINE_BINARY = "vkquake"
    QUAKE_MAPS_PATH = join("id1", "maps")
    COMMAND_LINE_ARGS = "-nojoy +skill 3"
    """
    Formats that are always or often relevant:
    .bsp (maps themselves)
    .lit (map lighting files, for modern engines)
    .pak (while sometimes maps come inside, gfx and the like also can come packed)
    .wad (guess some engines can read old doom-like wad files)
    .txt (authors, instructions, etc., although often will get overriden)
    .tga (textures inside subfolders)
    .lmp (no idea)
    .ogg (music)
    .mdl (3D models)
    .wav (sounds)
    """
    FILE_IGNORE_LIST = [
        ".map",
        ".dmm",
        ".bmp",
        ".gif",
        ".cfg",
        ".bat",
        ".htm",
        ".html",
        ".jpg",
        ".png",
        ".exe",
        ".diz",
        ".dat",
    ]

    def __init__(self) -> None:
        self.engine_binary = self.DEFAULT_ENGINE_BINARY
        # by default, where this python file resides
        self.execution_path = dirname(abspath(__file__))

    @classmethod
    def check_quake_folder(cls) -> None:
        if not os.path.exists(cls.QUAKE_MAPS_PATH):
            print("> ERROR can't find Quake maps folder ('{}')".format(cls.QUAKE_MAPS_PATH))
            exit(1)

    def set_engine_binary(self, engine_binary: str) -> None:
        self.engine_binary = engine_binary.lower()

    def set_execution_path(self, execution_path: str) -> None:
        self.execution_path = execution_path

    @property
    def command_line_binary_and_args(self) -> List[str]:
        return [self._engine_binary_arg] + self.COMMAND_LINE_ARGS.split(" ")

    @property
    def _engine_binary_arg(self) -> str:
        formatted_binary = self.engine_binary

        operating_system_string = platform.system().lower()
        if any(["windows" in operating_system_string, "cygwin" in operating_system_string]):
            if not self.engine_binary.endswith(".exe"):
                formatted_binary = "{}.exe".format(self.engine_binary)

        return join(self.execution_path, formatted_binary)


class Database:

    DATABASE_URL = "https://www.quaddicted.com/reviews/quaddicted_database.xml"
    # db files stored in the same execution folder
    DATABASE_FILE = "database.xml"
    LOCAL_CACHE_FILE = "database_cache.json"
    MAP_ZIP_URL = "https://www.quaddicted.com/filebase/{id}.zip"
    SCREENSHOT_URL = "https://www.quaddicted.com/reviews/screenshots/{id}.jpg"

    def __init__(self, config: "Configuration") -> None:
        self.config = config
        self.loaded_maps = []  # type: List[Any]
        self.cache = {}  # type: Dict

    @classmethod
    def update(cls) -> None:
        # Updates only once each 24h
        one_day_timedelta = timedelta(days=1)

        stale = True
        if os.path.exists(cls.DATABASE_FILE):
            db_file_statinfo = os.stat(cls.DATABASE_FILE)
            modification_datetime = datetime.fromtimestamp(db_file_statinfo.st_mtime)
            stale = datetime.now() > modification_datetime + one_day_timedelta

        if stale:
            print("> Updating Maps database from https://www.quaddicted.com ...")
            request = requests.get(cls.DATABASE_URL)
            if request.status_code != 200:
                print("> ERROR updating database file from {}".format(cls.DATABASE_URL))
                exit(1)

            with open(cls.DATABASE_FILE, "w") as db_file_handle:
                db_file_handle.write(request.text.encode("cp1252", errors="ignore").decode("UTF-8", errors="ignore"))

    def load_maps(self, do_shuffle: bool = True) -> None:
        def outmost_file_tags(element: Any) -> bool:
            return element.name == "file" and element.has_attr("id") and element.has_attr("type")

        with open(self.DATABASE_FILE, encoding="utf-8") as db_file_handle:
            xml_contents = db_file_handle.read()
        soup = BeautifulSoup(xml_contents, "xml")
        items = soup.files.findAll(outmost_file_tags)

        if do_shuffle:
            random.shuffle(items)
        self.loaded_maps = items

        self._load_cache()

    # Optional parameter allows to choose an specific index (with non-shuffling, allows deterministic selection)
    def choose_map(self, chosen_index: int = 0) -> Any:
        return self.loaded_maps.pop(chosen_index)

    def fetch_map(self, quake_map: Any, delete_zip: bool = False) -> str:
        map_id = quake_map["id"]

        map_zipfile = "{}.zip".format(os.path.join(self.config.QUAKE_MAPS_PATH, map_id))

        if quake_map["id"] in self.cache.keys():
            return self.cache["id"]

        map_url = self.MAP_ZIP_URL.format(id=map_id)
        request = requests.get(map_url)
        if request.status_code != 200:
            print("> ERROR fetching map from {}".format(map_url))
            exit(1)
        with open(map_zipfile, "wb") as map_file_handle:
            map_file_handle.write(request.content)

        zip_files = []
        if zipfile.is_zipfile(map_zipfile):
            with zipfile.ZipFile(map_zipfile, "r") as zip_handle:
                zip_files = zip_handle.namelist()
                zip_files = self._filter_unwanted_zip_files(zip_files)
                if self._contains_any_map(zip_files):
                    zip_handle.extractall(path=self.config.QUAKE_MAPS_PATH, members=zip_files)

        os.remove(map_zipfile)
        self._lowercase_files()

        chosen_map_file = self._find_suitable_map(zip_files)
        self._update_cache(map_id, chosen_map_file)

        return chosen_map_file

    @classmethod
    def screenshot_url(cls, quake_map: Any) -> str:
        return cls.SCREENSHOT_URL.format(id=quake_map["id"])

    def _filter_unwanted_zip_files(self, original_file_list: List[str]) -> List[str]:
        return [
            filename
            for filename in original_file_list
            if filename.lower()[filename.rfind(".") :] not in self.config.FILE_IGNORE_LIST
        ]

    @classmethod
    def _contains_any_map(cls, map_filenames: List[str]) -> bool:
        return len([filename for filename in map_filenames if filename.lower().endswith(".bsp")]) > 0

    @classmethod
    def _find_suitable_map(cls, map_filenames: List[str]) -> str:
        # Doesn't works at least for now with maps on subfolders
        map_files = [
            filename.lower()
            for filename in map_filenames
            if filename.lower().endswith(".bsp") and os.pathsep not in filename
        ]

        if not cls._contains_any_map(map_files):
            return ""

        start_map_candidates = [filename for filename in map_files if "start" in filename.lower()]
        if start_map_candidates:
            return start_map_candidates[0]
        else:
            return map_files[0]

    def _load_cache(self) -> None:
        if not os.path.exists(self.LOCAL_CACHE_FILE):
            return

        with open(self.LOCAL_CACHE_FILE, "r") as cache_file_handle:
            self.cache = json.load(cache_file_handle)

    def _update_cache(self, key: str, value: str) -> None:
        self.cache[key] = value

        with open(self.LOCAL_CACHE_FILE, "w") as cache_file_handle:
            json.dump(self.cache, cache_file_handle, indent=None)

    def _lowercase_files(self) -> None:
        for filename in os.listdir(self.config.QUAKE_MAPS_PATH):
            file_with_path = os.path.join(self.config.QUAKE_MAPS_PATH, filename)
            os.rename(file_with_path, file_with_path.lower())


if __name__ == "__main__":

    def check_args(argv: List[str], index: int, config: Configuration):
        if len(argv) < index + 1:
            return

        if argv[index] == "--engine":
            config.set_engine_binary(argv[index + 1])
        elif argv[index] == "--path":
            config.set_execution_path(argv[index + 1])

    config = Configuration()

    config.check_quake_folder()

    # 0: script name
    # 1 & 2: one param and value
    check_args(sys.argv, 1, config)
    # 3 & 4: another param and value
    check_args(sys.argv, 3, config)

    db = Database(config=config)

    print("Quaddicted.com Random Map")

    db.update()
    # Sample deactivation of random map:
    # db.load_maps(do_shuffle=False)
    # chosen_map = db.choose_map(chosen_index=200)
    db.load_maps()

    map_filename = ""
    while not map_filename:
        chosen_map = db.choose_map()
        print("> Checking Map '{}'...".format(chosen_map.find("title").text))
        map_filename = db.fetch_map(chosen_map)

    print("")
    print("Map name:   ", chosen_map.find("title").text)
    print("Screenshot: ", db.screenshot_url(chosen_map))
    print("Description: {}\n".format(chosen_map.find("description").text))

    input("\n-=[ Press Enter to start Quake with map '{}' ]=-".format(map_filename))

    subprocess.run(config.command_line_binary_and_args + ["+map", map_filename])
