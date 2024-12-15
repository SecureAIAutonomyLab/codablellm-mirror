
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypedDict, no_type_check

from codablellm.core.utils import SupportsJSON, JSONObject


@dataclass(frozen=True)
class Function:
    uid: str
    path: Path


@dataclass(frozen=True)
class SourceFunction(Function):
    language: str
    definition: str
    name: str
    start_byte: int
    end_byte: int
    class_name: Optional[str] = None

    @property
    def is_method(self) -> bool:
        return self.class_name is not None

    def with_definition(self, definition: str, name: Optional[str] = None,
                        write_back: bool = True) -> 'SourceFunction':
        if not self.class_name:
            source_function = SourceFunction(f'{self.path}:{name}' if name else self.uid,
                                             self.path, self.language, definition,
                                             name if name else self.name,
                                             self.start_byte, self.start_byte + len(definition))
        else:
            source_function = SourceFunction(f'{self.path}:{self.class_name}.{name}' if name else self.uid,
                                             self.path, self.language, definition,
                                             name if name else self.name, self.start_byte,
                                             self.start_byte + len(definition),
                                             class_name=self.class_name)
        if write_back:
            source_code = source_function.path.read_text()
            source_function.path.write_text(source_code[:self.start_byte] +
                                            source_function.definition +
                                            source_code[self.end_byte:])
        return source_function

    @classmethod
    def from_source(cls, path: Path, language: str, definition: str, name: str, start_byte: int,
                    end_byte: int, class_name: Optional[str] = None) -> 'SourceFunction':
        if not class_name:
            return cls(f'{path}:{name}', path, language, definition, name, start_byte, end_byte)
        return cls(f'{path}:{class_name}.{name}', path, language, definition, name, start_byte,
                   end_byte, class_name=class_name)


class DecompiledFunctionJSONObject(TypedDict):
    uid: str
    path: str
    definition: str
    name: str
    assembly: str
    architecture: str


@dataclass(frozen=True)
class DecompiledFunction(Function, SupportsJSON[DecompiledFunctionJSONObject]):
    definition: str
    name: str
    assembly: str
    architecture: str

    def to_json(self) -> DecompiledFunctionJSONObject:
        return {'uid': self.uid, 'path': str(self.path), 'definition': self.definition,
                'name': self.name, 'assembly': self.assembly, 'architecture': self.architecture}

    @classmethod
    def from_json(cls, json_obj: DecompiledFunctionJSONObject) -> 'DecompiledFunction':
        return cls(json_obj['uid'], Path(json_obj['path']), json_obj['definition'],
                   json_obj['name'], json_obj['assembly'], json_obj['architecture'])
