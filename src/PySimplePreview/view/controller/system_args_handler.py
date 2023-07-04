import argparse
import sys
from pathlib import Path

import PySimplePreview
from PySimplePreview.domain.model.config import Config, is_valid_project


class SystemArgsHandler:
    def __init__(self, config: Config):
        parser = argparse.ArgumentParser(
            prog="PySimplePreview",
            description="Realtime (live/hot) preview of PySimpleGUI layouts",
        )
        self._config = config
        self.parser = parser
        parser.add_argument('-v', '--version', action='version', version=PySimplePreview.__version__)
        parser.add_argument(
            '-P', '--project-path', action='store',
            help="Sets path to root module (__init__), single .py module, or directory as current project"
        )
        parser.add_argument(
            '-p', '--preview', action='store',
            help="Overrides current preview"
        )

    def run(self):
        args = self.parser.parse_args()
        if args.project_path:
            new_project = Path(args.project_path)
            if is_valid_project(new_project):
                self._config.add_project(new_project)
            else:
                print(f"Path '{new_project.absolute()}' isn't valid project!")
                sys.exit()
        if args.preview:
            print(args.preview)
            self._config.last_preview_key = args.preview

        # There is no configuration save to imitate "virtual" configuration
        # But any configuration change will also persist changes made here
        # It's a feature :)
