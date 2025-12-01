from common import error_pb2 as _error_pb2
from common import metadata_pb2 as _metadata_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValidationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALIDATION_TYPE_UNSPECIFIED: _ClassVar[ValidationType]
    VALIDATION_TYPE_SYNTAX: _ClassVar[ValidationType]
    VALIDATION_TYPE_SEMANTIC: _ClassVar[ValidationType]
    VALIDATION_TYPE_FULL: _ClassVar[ValidationType]

class SuggestionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUGGESTION_TYPE_UNSPECIFIED: _ClassVar[SuggestionType]
    SUGGESTION_TYPE_KEYWORD: _ClassVar[SuggestionType]
    SUGGESTION_TYPE_FUNCTION: _ClassVar[SuggestionType]
    SUGGESTION_TYPE_PARAMETER: _ClassVar[SuggestionType]
    SUGGESTION_TYPE_VARIABLE: _ClassVar[SuggestionType]
    SUGGESTION_TYPE_SECTION: _ClassVar[SuggestionType]
VALIDATION_TYPE_UNSPECIFIED: ValidationType
VALIDATION_TYPE_SYNTAX: ValidationType
VALIDATION_TYPE_SEMANTIC: ValidationType
VALIDATION_TYPE_FULL: ValidationType
SUGGESTION_TYPE_UNSPECIFIED: SuggestionType
SUGGESTION_TYPE_KEYWORD: SuggestionType
SUGGESTION_TYPE_FUNCTION: SuggestionType
SUGGESTION_TYPE_PARAMETER: SuggestionType
SUGGESTION_TYPE_VARIABLE: SuggestionType
SUGGESTION_TYPE_SECTION: SuggestionType

class ValidateDSLRequest(_message.Message):
    __slots__ = ()
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    dsl_code: str
    validation_type: ValidationType
    metadata: _metadata_pb2.Metadata
    def __init__(self, dsl_code: _Optional[str] = ..., validation_type: _Optional[_Union[ValidationType, str]] = ..., metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...) -> None: ...

class ValidateDSLResponse(_message.Message):
    __slots__ = ()
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    SYNTAX_ERRORS_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    syntax_errors: _containers.RepeatedCompositeFieldContainer[SyntaxError]
    semantic_warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.ValidationWarning]
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, is_valid: _Optional[bool] = ..., syntax_errors: _Optional[_Iterable[_Union[SyntaxError, _Mapping]]] = ..., semantic_warnings: _Optional[_Iterable[_Union[_error_pb2.ValidationWarning, _Mapping]]] = ..., suggestions: _Optional[_Iterable[str]] = ...) -> None: ...

class SyntaxError(_message.Message):
    __slots__ = ()
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_FIELD_NUMBER: _ClassVar[int]
    line: int
    column: int
    message: str
    expected: str
    actual: str
    def __init__(self, line: _Optional[int] = ..., column: _Optional[int] = ..., message: _Optional[str] = ..., expected: _Optional[str] = ..., actual: _Optional[str] = ...) -> None: ...

class AutocompleteDSLRequest(_message.Message):
    __slots__ = ()
    PARTIAL_DSL_FIELD_NUMBER: _ClassVar[int]
    CURSOR_POSITION_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    partial_dsl: str
    cursor_position: int
    context: AutocompleteContext
    metadata: _metadata_pb2.Metadata
    def __init__(self, partial_dsl: _Optional[str] = ..., cursor_position: _Optional[int] = ..., context: _Optional[_Union[AutocompleteContext, _Mapping]] = ..., metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...) -> None: ...

class AutocompleteContext(_message.Message):
    __slots__ = ()
    SECTION_FIELD_NUMBER: _ClassVar[int]
    PARENT_NODE_FIELD_NUMBER: _ClassVar[int]
    section: str
    parent_node: str
    def __init__(self, section: _Optional[str] = ..., parent_node: _Optional[str] = ...) -> None: ...

class AutocompleteDSLResponse(_message.Message):
    __slots__ = ()
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[AutocompleteSuggestion]
    def __init__(self, suggestions: _Optional[_Iterable[_Union[AutocompleteSuggestion, _Mapping]]] = ...) -> None: ...

class AutocompleteSuggestion(_message.Message):
    __slots__ = ()
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTATION_FIELD_NUMBER: _ClassVar[int]
    value: str
    description: str
    type: SuggestionType
    confidence: _metadata_pb2.ConfidenceScore
    documentation: str
    def __init__(self, value: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[SuggestionType, str]] = ..., confidence: _Optional[_Union[_metadata_pb2.ConfidenceScore, _Mapping]] = ..., documentation: _Optional[str] = ...) -> None: ...

class GetSyntaxHelpRequest(_message.Message):
    __slots__ = ()
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    topic: str
    metadata: _metadata_pb2.Metadata
    def __init__(self, topic: _Optional[str] = ..., metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...) -> None: ...

class GetSyntaxHelpResponse(_message.Message):
    __slots__ = ()
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    RELATED_TOPICS_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    examples: _containers.RepeatedScalarFieldContainer[str]
    related_topics: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., examples: _Optional[_Iterable[str]] = ..., related_topics: _Optional[_Iterable[str]] = ...) -> None: ...
