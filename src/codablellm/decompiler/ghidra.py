import json
import os
import subprocess

from codablellm.core.decompiler import Decompiler
from codablellm.core.function import CompiledFunction
from codablellm.core import utils
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Final, Optional, Sequence


class Ghidra(Decompiler):

    ENVIRON_KEY: Final[str] = 'GHIDRA_HEADLESS'
    SCRIPT_PATH: Final[Path] = Path(__file__).parent.parent / 'resources' / 'ghidra_scripts' / \
        'decompile.py'

    def decompile(self, path: utils.PathLike) -> Sequence[CompiledFunction]:
        # Ensure Ghidra is installed
        ghidra_path = Ghidra.get_path()
        if not ghidra_path:
            raise ValueError(
                f"{Ghidra.ENVIRON_KEY} is not set to Ghidra's analyzeHeadless command")
        path = Path(path)
        with TemporaryDirectory() as project_dir:
            with NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as output_file:
                output_path = Path(output_file.name)
                try:
                    output_file.close()
                    # Run decompile script
                    try:
                        result = subprocess.run([ghidra_path, project_dir, 'codablellm', '-import', path,
                                                 '-scriptPath', Ghidra.SCRIPT_PATH.parent, '-noanalysis',
                                                 '-postScript', Ghidra.SCRIPT_PATH.name, output_path],
                                                check=True, capture_output=True)
                    except subprocess.CalledProcessError as e:
                        raise ValueError('Ghidra command failed: '
                                         f'{e.stderr}') from e
                    try:
                        return []
                    except json.JSONDecodeError as e:
                        raise ValueError('Ghidra post script error: '
                                         f'{result.stdout}') from e
                finally:
                    output_path.unlink(missing_ok=True)

    @staticmethod
    def set_path(path: utils.PathLike) -> None:
        os.environ[Ghidra.ENVIRON_KEY] = str(path)

    @staticmethod
    def get_path() -> Optional[Path]:
        os.environ.get(Ghidra.ENVIRON_KEY)
