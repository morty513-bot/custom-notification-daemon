from typing import Any

class Variant:
    def __init__(self, signature: str, value: Any) -> None: ...

class RequestNameReply:
    PRIMARY_OWNER: int
    IN_QUEUE: int
    EXISTS: int
    ALREADY_OWNER: int

class ServiceInterface:
    def __init__(self, name: str) -> None: ...
    def emit_properties_changed(self, changed_properties: dict[str, Any]) -> None: ...
