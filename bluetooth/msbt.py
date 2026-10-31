"""Microsoft Bluetooth API with per-operation native socket ownership."""
from __future__ import annotations

import errno
import math
from _thread import RLock
from contextlib import contextmanager
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from . import _msbt as bt
from . import btcommon as common

if TYPE_CHECKING:
    from collections.abc import Buffer

__all__ = [
    "BluetoothSocket", "DeviceDiscoverer", "advertise_service", "discover_devices",
    "find_service", "lookup_name", "read_local_bdaddr", "stop_advertising",
]

bt.initwinsock()

DiscoveryResult = Union[str, Tuple[str, str], Tuple[str, int], Tuple[str, str, int]]


def discover_devices(duration: int = 8, flush_cache: bool = True,
                     lookup_names: bool = False, lookup_class: bool = False,
                     device_id: int = -1) -> List[DiscoveryResult]:
    # The Windows API chooses the available radios; device_id is retained for
    # compatibility with the cross-platform public signature.
    try:
        devices = bt.discover_devices(duration=duration, flush_cache=flush_cache)
    except OSError:
        return []
    result: List[DiscoveryResult] = []
    for address, name, device_class in devices:
        if lookup_names and lookup_class:
            result.append((address, name, device_class))
        elif lookup_names:
            result.append((address, name))
        elif lookup_class:
            result.append((address, device_class))
        else:
            result.append(address)
    return result


def read_local_bdaddr() -> List[str]:
    return bt.list_local()


def lookup_name(address: str, timeout: float = 10) -> Optional[str]:
    if not common.is_valid_address(address):
        raise ValueError("Invalid Bluetooth address")
    # The existing Windows API queries its device cache without an inquiry.
    try:
        return bt.lookup_name(address)
    except OSError:
        return None


class BluetoothSocket:
    """Own a socket handle; blocking operations use independent native leases.

    A lease shares the Winsock endpoint while preventing descriptor reuse when
    another thread closes this owner. It does not lock a blocking I/O call.
    Like native socket duplicates, dup() shares endpoint options.
    """

    def __init__(self, proto: int = common.RFCOMM, sockfd: Optional[int] = None) -> None:
        if proto != common.RFCOMM:
            raise ValueError("invalid protocol")
        self._lock = RLock()
        self._sockfd = -1
        self._proto = proto
        self._sdp_handle: Optional[int] = None
        self._raw_sdp_record: Optional[bytes] = None
        self._blocking = True
        self._timeout: Optional[float] = None
        if sockfd is not None and sockfd < 0:
            raise ValueError("invalid socket descriptor")
        self._sockfd = sockfd if sockfd is not None else bt.socket(bt.SOCK_STREAM, bt.BTHPROTO_RFCOMM)

    def _open_descriptor(self) -> int:
        if self._sockfd < 0:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._sockfd

    @contextmanager
    def _lease(self) -> Generator[int, None, None]:
        with self._lock:
            descriptor = bt.dup(self._open_descriptor())
        try:
            yield descriptor
        finally:
            bt.close(descriptor)

    @property
    def family(self) -> int:
        return bt.AF_BTH

    @property
    def type(self) -> int:
        return bt.SOCK_STREAM

    @property
    def proto(self) -> int:
        return bt.BTHPROTO_RFCOMM

    def bind(self, addrport: Tuple[str, int]) -> None:
        address, port = addrport
        with self._lease() as descriptor:
            bt.bind(descriptor, address, bt.BT_PORT_ANY if port == 0 else port)

    def listen(self, backlog: int) -> None:
        with self._lease() as descriptor:
            bt.listen(descriptor, backlog)

    def accept(self) -> Tuple[BluetoothSocket, Tuple[str, int]]:
        with self._lease() as descriptor:
            accepted, address, port = bt.accept(descriptor)
        try:
            client = BluetoothSocket(self._proto, sockfd=accepted)
        except BaseException:
            bt.close(accepted)
            raise
        return client, (address, port)

    def connect(self, addrport: Tuple[str, int]) -> None:
        address, port = addrport
        with self._lease() as descriptor:
            bt.connect(descriptor, address, port)

    def send(self, data: Union[Buffer, str]) -> int:
        with self._lease() as descriptor:
            return bt.send(descriptor, data)

    def recv(self, numbytes: int) -> bytes:
        with self._lease() as descriptor:
            return bt.recv(descriptor, numbytes)

    def close(self) -> None:
        with self._lock:
            descriptor = self._sockfd
            self._sockfd = -1
        if descriptor >= 0:
            bt.close(descriptor)

    def getsockname(self) -> Tuple[str, int]:
        with self._lease() as descriptor:
            return bt.getsockname(descriptor)

    def getpeername(self) -> Tuple[str, int]:
        with self._lease() as descriptor:
            return bt.getpeername(descriptor)

    getpeername.__doc__ = bt.getpeername.__doc__

    def setblocking(self, blocking: bool) -> None:
        with self._lock:
            descriptor = self._open_descriptor()
            bt.settimeout(descriptor, 0.0)
            bt.setblocking(descriptor, bool(blocking))
            self._blocking = bool(blocking)
            self._timeout = None if blocking else 0.0

    def settimeout(self, timeout: Optional[float]) -> None:
        if timeout is None:
            seconds, blocking = 0.0, True
        else:
            seconds = float(timeout)
            if not math.isfinite(seconds) or seconds < 0:
                raise ValueError("timeout must be finite and non-negative")
            blocking = seconds != 0
        with self._lock:
            descriptor = self._open_descriptor()
            bt.settimeout(descriptor, seconds)
            bt.setblocking(descriptor, blocking)
            self._blocking = blocking
            self._timeout = None if timeout is None else seconds

    def gettimeout(self) -> Optional[float]:
        with self._lock:
            descriptor = self._open_descriptor()
            if not self._blocking:
                return 0.0
            if self._timeout is None:
                return None
            return bt.gettimeout(descriptor)

    def fileno(self) -> int:
        with self._lock:
            return self._sockfd

    def dup(self) -> BluetoothSocket:
        with self._lock:
            descriptor = bt.dup(self._open_descriptor())
            try:
                result = BluetoothSocket(self._proto, sockfd=descriptor)
            except BaseException:
                bt.close(descriptor)
                raise
            result._blocking = self._blocking
            result._timeout = self._timeout
            return result

    def advertise_service(self, name: str, service_id: str = "",
                          service_classes: Sequence[str] = (),
                          profiles: Sequence[Tuple[str, int]] = (), provider: str = "",
                          description: str = "", protocols: Sequence[str] = ()) -> None:
        # Snapshot caller-owned collections before building the record.
        classes, profile_list, protocol_list = tuple(service_classes), tuple(profiles), tuple(protocols)
        if service_id and not common.is_valid_uuid(service_id):
            raise ValueError("invalid UUID specified for service_id")
        if any(not common.is_valid_uuid(uuid) for uuid in classes):
            raise ValueError("invalid UUID specified in service_classes")
        if any(not common.is_valid_uuid(uuid) or not 0 <= version <= 0xFFFF
               for uuid, version in profile_list):
            raise ValueError("Invalid Profile Descriptor")
        if any(not common.is_valid_uuid(uuid) for uuid in protocol_list):
            raise ValueError("invalid UUID specified in protocols")

        with self._lock:
            self._open_descriptor()
            if self._raw_sdp_record is not None:
                raise OSError("service already advertised")
            pairs: List[common.SDPElement] = []
            def attribute(identifier: int, kind: str, value: common.SDPValue) -> None:
                pairs.extend((("UInt16", identifier), (kind, value)))

            if service_id:
                attribute(common.SERVICE_ID_ATTRID, "UUID", service_id)
            if classes:
                attribute(common.SERVICE_CLASS_ID_LIST_ATTRID, "ElemSeq", [("UUID", uuid) for uuid in classes])
            _, port = self.getsockname()
            protocol_descriptors: List[common.SDPElement] = [
                ("ElemSeq", (("UUID", common.L2CAP_UUID),)),
                ("ElemSeq", (("UUID", common.RFCOMM_UUID), ("UInt8", port))),
            ]
            protocol_descriptors.extend(("ElemSeq", (("UUID", uuid),)) for uuid in protocol_list)
            attribute(common.PROTOCOL_DESCRIPTOR_LIST_ATTRID, "ElemSeq", protocol_descriptors)
            attribute(common.BROWSE_GROUP_LIST_ATTRID, "ElemSeq", (("UUID", common.PUBLIC_BROWSE_GROUP),))
            if profile_list:
                attribute(common.BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRID, "ElemSeq", [
                    ("ElemSeq", (("UUID", uuid), ("UInt16", version))) for uuid, version in profile_list
                ])
            attribute(common.SERVICE_NAME_ATTRID, "String", name)
            if description:
                attribute(common.SERVICE_DESCRIPTION_ATTRID, "String", description)
            if provider:
                attribute(common.PROVIDER_NAME_ATTRID, "String", provider)
            record = common.sdp_make_data_element("ElemSeq", pairs)
            handle = bt.set_service_raw(record, True)
            # Publish the pair only after the Windows registration succeeds.
            self._raw_sdp_record, self._sdp_handle = record, handle


    def stop_advertising(self) -> None:
        with self._lock:
            if self._raw_sdp_record is None or self._sdp_handle is None:
                raise OSError("service isn't advertised, but trying to un-advertise")
            bt.set_service_raw(self._raw_sdp_record, False, self._sdp_handle)
            self._raw_sdp_record, self._sdp_handle = None, None


    def makefile(self) -> None:
        # Retain the pre-existing Windows API; this port adds no replacement
        # for the previously unsupported file wrapper.
        raise Exception("Not yet implemented")

    def __enter__(self) -> BluetoothSocket:
        with self._lock:
            self._open_descriptor()
        return self

    def __exit__(self, exc_type: Optional[type[BaseException]],
                 exc: Optional[BaseException], tb: Optional[TracebackType]) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            # Normal close() reports errors; interpreter teardown is best effort.
            pass


def advertise_service(sock: BluetoothSocket, name: str, service_id: str = "",
                      service_classes: Sequence[str] = (),
                      profiles: Sequence[Tuple[str, int]] = (), provider: str = "",
                      description: str = "", protocols: Sequence[str] = ()) -> None:
    sock.advertise_service(name, service_id, service_classes, profiles, provider, description, protocols)


def stop_advertising(sock: BluetoothSocket) -> None:
    sock.stop_advertising()


def find_service(name: Optional[str] = None, uuid: Optional[str] = None,
                 address: Optional[str] = None) -> List[Dict[str, object]]:
    uuid_string = uuid or common.PUBLIC_BROWSE_GROUP
    if not common.is_valid_uuid(uuid_string):
        raise ValueError("invalid UUID")
    full_uuid = common.to_full_uuid(uuid_string)
    addresses = [address] if address is not None else [
        item for item in discover_devices() if isinstance(item, str)
    ]
    results: List[Dict[str, object]] = []
    for host in addresses:
        for native in bt.find_service(host, full_uuid):
            record = common.sdp_parse_raw_record(native["rawrecord"])
            result: Dict[str, object] = dict(native)
            classes = record.get(common.SERVICE_CLASS_ID_LIST_ATTRID)
            if classes is not None and not isinstance(classes, (int, str, bytes)):
                result["service-classes"] = [item[1] for item in classes]
            else:
                result["service-classes"] = []
            profiles = record.get(common.BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRID)
            profile_list: List[Tuple[common.SDPValue, common.SDPValue]] = []
            if profiles is not None and not isinstance(profiles, (int, str, bytes)):
                for _, value in profiles:
                    if value is None or isinstance(value, (int, str, bytes)) or len(value) != 2:
                        raise ValueError("invalid SDP profile descriptor")
                    uuid_pair, version_pair = value
                    profile_list.append((uuid_pair[1], version_pair[1]))
            result["profiles"] = profile_list
            result["provider"] = record.get(common.PROVIDER_NAME_ATTRID)
            result["service-id"] = record.get(common.SERVICE_ID_ATTRID)
            result["name"] = record.get(common.SERVICE_NAME_ATTRID)
            result["handle"] = record.get(common.SERVICE_RECORD_HANDLE_ATTRID)
            if name is None or result["name"] in (name, name.encode("utf-8")):
                results.append(result)
    return results


class DeviceDiscoverer:
    def __init__(self) -> None:
        raise NotImplementedError
