"""Windows Event XML ingestion into canonical CHITRAGUPT events."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from backend.app.models import Evidence, Event


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _attributes(element: ElementTree.Element) -> dict[str, str]:
    return {
        _local_name(name): value
        for name, value in element.attrib.items()
    }


def _raw_element(element: ElementTree.Element) -> dict[str, Any]:
    raw: dict[str, Any] = {
        "tag": _local_name(element.tag),
        "attributes": _attributes(element),
    }
    text = _clean_text(element.text)
    if text is not None:
        raw["text"] = text
    children = [_raw_element(child) for child in list(element)]
    if children:
        raw["children"] = children
    return raw


def _child(element: ElementTree.Element, name: str) -> ElementTree.Element | None:
    return next(
        (child for child in list(element) if _local_name(child.tag) == name),
        None,
    )


def _descendant_values(element: ElementTree.Element, container_name: str) -> dict[str, str]:
    container = _child(element, container_name)
    if container is None:
        return {}

    values: dict[str, str] = {}
    for data in container.iter():
        if _local_name(data.tag) != "Data":
            continue
        name = _clean_text(data.attrib.get("Name"))
        value = _clean_text(data.text)
        if name is not None and value is not None:
            values[name] = value
    return values


def _first_value(values: dict[str, str], names: tuple[str, ...]) -> str | None:
    for name in names:
        if values.get(name):
            return values[name]
    return None


def _sha256_file(file_path: Path) -> str:
    digest = sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_event(event_element: ElementTree.Element, event_number: int, case_id: int) -> Event:
    system = _child(event_element, "System")
    if system is None:
        raise ValueError(
            f"Malformed Windows Event XML event {event_number}: missing System element."
        )

    provider_element = _child(system, "Provider")
    event_id_element = _child(system, "EventID")
    time_created_element = _child(system, "TimeCreated")
    computer_element = _child(system, "Computer")
    security_element = _child(system, "Security")
    execution_element = _child(system, "Execution")

    provider = (
        _clean_text(provider_element.attrib.get("Name"))
        if provider_element is not None
        else None
    )
    event_id = (
        _clean_text(event_id_element.text)
        if event_id_element is not None
        else None
    )
    system_time = (
        _clean_text(time_created_element.attrib.get("SystemTime"))
        if time_created_element is not None
        else None
    )
    timestamp = None
    if system_time is not None:
        try:
            timestamp = datetime.fromisoformat(system_time.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(
                f"Malformed Windows Event XML event {event_number}: "
                f"invalid SystemTime {system_time!r}."
            ) from exc

    event_data = _descendant_values(event_element, "EventData")
    user_data = _descendant_values(event_element, "UserData")
    all_named_data = {**event_data, **user_data}
    user = _first_value(
        all_named_data,
        ("TargetUserName", "SubjectUserName", "UserName", "AccountName"),
    )
    if user is None and security_element is not None:
        user = _clean_text(security_element.attrib.get("UserID"))

    process_id = (
        _clean_text(execution_element.attrib.get("ProcessID"))
        if execution_element is not None
        else None
    )
    process = _first_value(
        all_named_data,
        ("NewProcessName", "Image", "ProcessName", "Process"),
    ) or process_id
    ip_address = _first_value(
        all_named_data,
        ("IpAddress", "ClientAddress", "SourceAddress"),
    )
    file_path = _first_value(
        all_named_data,
        ("ObjectName", "TargetFilename", "FileName", "Path"),
    )
    application = _first_value(
        all_named_data,
        ("Application", "ApplicationName"),
    )
    raw_data = {
        "event": _raw_element(event_element),
        "event_id": event_id,
        "provider": provider,
        "computer": _clean_text(computer_element.text)
        if computer_element is not None
        else None,
        "event_data": event_data,
        "user_data": user_data,
    }

    return Event(
        case_id=case_id,
        timestamp=timestamp,
        event_type=event_id,
        source=provider,
        user=user,
        device=raw_data["computer"],
        ip_address=ip_address,
        application=application,
        process=process,
        file_path=file_path,
        raw_data=raw_data,
    )


def ingest_windows_event_xml(
    xml_path: str | Path,
    case_id: int,
    *,
    source: str | None = None,
    ingested_at: datetime | None = None,
) -> tuple[Evidence, list[Event]]:
    """Parse exported Windows Event XML into unsaved evidence and events."""
    file_path = Path(xml_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Windows Event XML file not found: {file_path}")

    try:
        root = ElementTree.parse(file_path).getroot()
    except (OSError, ElementTree.ParseError, UnicodeDecodeError) as exc:
        raise ValueError(
            f"Unable to parse Windows Event XML evidence file: {file_path}: {exc}"
        ) from exc

    event_elements = [
        element
        for element in root.iter()
        if _local_name(element.tag) == "Event"
    ]
    if not event_elements:
        raise ValueError(
            f"Malformed Windows Event XML evidence file: no Event elements found in {file_path}."
        )

    events = [
        _parse_event(event_element, event_number, case_id)
        for event_number, event_element in enumerate(event_elements, start=1)
    ]
    evidence = Evidence(
        case_id=case_id,
        filename=file_path.name,
        source=source,
        evidence_type="windows_event_xml",
        file_size=file_path.stat().st_size,
        sha256=_sha256_file(file_path),
        ingested_at=ingested_at or datetime.now(timezone.utc),
        processing_status="pending",
    )
    for event in events:
        event.evidence = evidence

    return evidence, events