import html
import string
from typing import Sequence, Any, Mapping


class HtmlTemplate(string.Formatter):
    def get_field(self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        val, key = super().get_field(field_name, args, kwargs)
        if hasattr(val, "__html__"):
            val = val.__html__()
        elif isinstance(val, str):
            val = html.escape(val)
        return val, key


class Html:
    def __init__(self, v: str) -> None:
        self.v = v

    def __str__(self) -> str:
        return self.v

    def __html__(self) -> str:
        return str(self)