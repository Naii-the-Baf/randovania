from __future__ import annotations

import dataclasses
import logging


class MemoryOperationException(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class MemoryOperation:
    address: int
    offset: int | None = None
    read_byte_count: int | None = None
    write_bytes: bytes | None = None

    @property
    def byte_count(self) -> int:
        if self.read_byte_count is not None:
            return self.read_byte_count
        if self.write_bytes is not None:
            return len(self.write_bytes)
        return 0

    def validate_byte_sizes(self) -> None:
        if (
            self.write_bytes is not None
            and self.read_byte_count is not None
            and len(self.write_bytes) != self.read_byte_count
        ):
            raise ValueError(f"Attempting to read {self.read_byte_count} bytes while writing {len(self.write_bytes)}.")

    def __str__(self) -> str:
        address_text = f"0x{self.address:08x}"
        if self.offset is not None:
            address_text = f"*{address_text} {self.offset:+05x}"

        operation_pretty = []
        if self.read_byte_count is not None:
            operation_pretty.append(f"read {self.read_byte_count} bytes")
        if self.write_bytes is not None:
            operation_pretty.append(f"write {self.write_bytes.hex()}")

        return f"At {address_text}, {' and '.join(operation_pretty)}"


class MemoryOperationExecutor:
    def __init__(self) -> None:
        self.logger = logging.getLogger(type(self).__name__)

    async def connect(self) -> str | None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def is_connected(self) -> bool:
        raise NotImplementedError

    async def perform_memory_operations(self, ops: list[MemoryOperation]) -> dict[MemoryOperation, bytes]:
        raise NotImplementedError

    async def perform_single_memory_operation(self, op: MemoryOperation) -> bytes | None:
        result = await self.perform_memory_operations([op])
        return result.get(op)
