from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

from mysingle.protos.common import metadata_pb2 as _metadata_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class ReportFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPORT_FORMAT_UNSPECIFIED: _ClassVar[ReportFormat]
    REPORT_FORMAT_MARKDOWN: _ClassVar[ReportFormat]
    REPORT_FORMAT_HTML: _ClassVar[ReportFormat]
    REPORT_FORMAT_PDF: _ClassVar[ReportFormat]

class ReportSection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPORT_SECTION_UNSPECIFIED: _ClassVar[ReportSection]
    REPORT_SECTION_SUMMARY: _ClassVar[ReportSection]
    REPORT_SECTION_PERFORMANCE: _ClassVar[ReportSection]
    REPORT_SECTION_RISK: _ClassVar[ReportSection]
    REPORT_SECTION_TRADES: _ClassVar[ReportSection]
    REPORT_SECTION_INSIGHTS: _ClassVar[ReportSection]
    REPORT_SECTION_RECOMMENDATIONS: _ClassVar[ReportSection]

class ReportDetailLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPORT_DETAIL_LEVEL_UNSPECIFIED: _ClassVar[ReportDetailLevel]
    REPORT_DETAIL_LEVEL_BRIEF: _ClassVar[ReportDetailLevel]
    REPORT_DETAIL_LEVEL_STANDARD: _ClassVar[ReportDetailLevel]
    REPORT_DETAIL_LEVEL_DETAILED: _ClassVar[ReportDetailLevel]

class ReportStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPORT_STATUS_UNSPECIFIED: _ClassVar[ReportStatus]
    REPORT_STATUS_PENDING: _ClassVar[ReportStatus]
    REPORT_STATUS_PROCESSING: _ClassVar[ReportStatus]
    REPORT_STATUS_COMPLETED: _ClassVar[ReportStatus]
    REPORT_STATUS_FAILED: _ClassVar[ReportStatus]

REPORT_FORMAT_UNSPECIFIED: ReportFormat
REPORT_FORMAT_MARKDOWN: ReportFormat
REPORT_FORMAT_HTML: ReportFormat
REPORT_FORMAT_PDF: ReportFormat
REPORT_SECTION_UNSPECIFIED: ReportSection
REPORT_SECTION_SUMMARY: ReportSection
REPORT_SECTION_PERFORMANCE: ReportSection
REPORT_SECTION_RISK: ReportSection
REPORT_SECTION_TRADES: ReportSection
REPORT_SECTION_INSIGHTS: ReportSection
REPORT_SECTION_RECOMMENDATIONS: ReportSection
REPORT_DETAIL_LEVEL_UNSPECIFIED: ReportDetailLevel
REPORT_DETAIL_LEVEL_BRIEF: ReportDetailLevel
REPORT_DETAIL_LEVEL_STANDARD: ReportDetailLevel
REPORT_DETAIL_LEVEL_DETAILED: ReportDetailLevel
REPORT_STATUS_UNSPECIFIED: ReportStatus
REPORT_STATUS_PENDING: ReportStatus
REPORT_STATUS_PROCESSING: ReportStatus
REPORT_STATUS_COMPLETED: ReportStatus
REPORT_STATUS_FAILED: ReportStatus

class GenerateReportRequest(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    config: ReportConfig
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        config: _Optional[_Union[ReportConfig, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class ReportConfig(_message.Message):
    __slots__ = ()
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    format: ReportFormat
    sections: _containers.RepeatedScalarFieldContainer[ReportSection]
    language: str
    detail_level: ReportDetailLevel
    def __init__(
        self,
        format: _Optional[_Union[ReportFormat, str]] = ...,
        sections: _Optional[_Iterable[_Union[ReportSection, str]]] = ...,
        language: _Optional[str] = ...,
        detail_level: _Optional[_Union[ReportDetailLevel, str]] = ...,
    ) -> None: ...

class GenerateReportProgress(_message.Message):
    __slots__ = ()
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    status: ReportStatus
    progress_percent: int
    current_stage: str
    result: ReportResult
    def __init__(
        self,
        task_id: _Optional[str] = ...,
        status: _Optional[_Union[ReportStatus, str]] = ...,
        progress_percent: _Optional[int] = ...,
        current_stage: _Optional[str] = ...,
        result: _Optional[_Union[ReportResult, _Mapping]] = ...,
    ) -> None: ...

class ReportResult(_message.Message):
    __slots__ = ()
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    content: str
    metadata: ReportMetadata
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        content: _Optional[str] = ...,
        metadata: _Optional[_Union[ReportMetadata, _Mapping]] = ...,
        warnings: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ReportMetadata(_message.Message):
    __slots__ = ()
    GENERATED_AT_FIELD_NUMBER: _ClassVar[int]
    TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    GENERATION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    MODEL_USED_FIELD_NUMBER: _ClassVar[int]
    generated_at: int
    tokens_used: int
    generation_time_ms: int
    model_used: str
    def __init__(
        self,
        generated_at: _Optional[int] = ...,
        tokens_used: _Optional[int] = ...,
        generation_time_ms: _Optional[int] = ...,
        model_used: _Optional[str] = ...,
    ) -> None: ...

class GetReportStatusRequest(_message.Message):
    __slots__ = ()
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        task_id: _Optional[str] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class GetReportStatusResponse(_message.Message):
    __slots__ = ()
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    status: ReportStatus
    progress_percent: int
    result: ReportResult
    error_message: str
    def __init__(
        self,
        task_id: _Optional[str] = ...,
        status: _Optional[_Union[ReportStatus, str]] = ...,
        progress_percent: _Optional[int] = ...,
        result: _Optional[_Union[ReportResult, _Mapping]] = ...,
        error_message: _Optional[str] = ...,
    ) -> None: ...

class GenerateComparisonReportRequest(_message.Message):
    __slots__ = ()
    BACKTEST_IDS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    backtest_ids: _containers.RepeatedScalarFieldContainer[str]
    config: ReportConfig
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        backtest_ids: _Optional[_Iterable[str]] = ...,
        config: _Optional[_Union[ReportConfig, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...
