from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

from mysingle.protos.common import error_pb2 as _error_pb2
from mysingle.protos.common import metadata_pb2 as _metadata_pb2

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
    __slots__ = ("dsl_code", "validation_type", "metadata")
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    dsl_code: str
    validation_type: ValidationType
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        dsl_code: _Optional[str] = ...,
        validation_type: _Optional[_Union[ValidationType, str]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class ValidateDSLResponse(_message.Message):
    __slots__ = ("is_valid", "syntax_errors", "semantic_warnings", "suggestions")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    SYNTAX_ERRORS_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    syntax_errors: _containers.RepeatedCompositeFieldContainer[SyntaxError]
    semantic_warnings: _containers.RepeatedCompositeFieldContainer[
        _error_pb2.ValidationWarning
    ]
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        is_valid: bool = ...,
        syntax_errors: _Optional[_Iterable[_Union[SyntaxError, _Mapping]]] = ...,
        semantic_warnings: _Optional[
            _Iterable[_Union[_error_pb2.ValidationWarning, _Mapping]]
        ] = ...,
        suggestions: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class SyntaxError(_message.Message):
    __slots__ = ("line", "column", "message", "expected", "actual")
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
    def __init__(
        self,
        line: _Optional[int] = ...,
        column: _Optional[int] = ...,
        message: _Optional[str] = ...,
        expected: _Optional[str] = ...,
        actual: _Optional[str] = ...,
    ) -> None: ...

class AutocompleteDSLRequest(_message.Message):
    __slots__ = ("partial_dsl", "cursor_position", "context", "metadata")
    PARTIAL_DSL_FIELD_NUMBER: _ClassVar[int]
    CURSOR_POSITION_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    partial_dsl: str
    cursor_position: int
    context: AutocompleteContext
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        partial_dsl: _Optional[str] = ...,
        cursor_position: _Optional[int] = ...,
        context: _Optional[_Union[AutocompleteContext, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class AutocompleteContext(_message.Message):
    __slots__ = ("section", "parent_node")
    SECTION_FIELD_NUMBER: _ClassVar[int]
    PARENT_NODE_FIELD_NUMBER: _ClassVar[int]
    section: str
    parent_node: str
    def __init__(
        self, section: _Optional[str] = ..., parent_node: _Optional[str] = ...
    ) -> None: ...

class AutocompleteDSLResponse(_message.Message):
    __slots__ = ("suggestions",)
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[AutocompleteSuggestion]
    def __init__(
        self,
        suggestions: _Optional[
            _Iterable[_Union[AutocompleteSuggestion, _Mapping]]
        ] = ...,
    ) -> None: ...

class AutocompleteSuggestion(_message.Message):
    __slots__ = ("value", "description", "type", "confidence", "documentation")
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
    def __init__(
        self,
        value: _Optional[str] = ...,
        description: _Optional[str] = ...,
        type: _Optional[_Union[SuggestionType, str]] = ...,
        confidence: _Optional[_Union[_metadata_pb2.ConfidenceScore, _Mapping]] = ...,
        documentation: _Optional[str] = ...,
    ) -> None: ...

class GetSyntaxHelpRequest(_message.Message):
    __slots__ = ("topic", "metadata")
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    topic: str
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        topic: _Optional[str] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class GetSyntaxHelpResponse(_message.Message):
    __slots__ = ("title", "description", "examples", "related_topics")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    RELATED_TOPICS_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    examples: _containers.RepeatedScalarFieldContainer[str]
    related_topics: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        title: _Optional[str] = ...,
        description: _Optional[str] = ...,
        examples: _Optional[_Iterable[str]] = ...,
        related_topics: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class SuggestRefactoringRequest(_message.Message):
    __slots__ = ("dsl_code", "focus", "metadata")
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    FOCUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    dsl_code: str
    focus: str
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        dsl_code: _Optional[str] = ...,
        focus: _Optional[str] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class SuggestRefactoringResponse(_message.Message):
    __slots__ = ("suggestions", "llm_powered")
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    LLM_POWERED_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[RefactoringSuggestion]
    llm_powered: bool
    def __init__(
        self,
        suggestions: _Optional[
            _Iterable[_Union[RefactoringSuggestion, _Mapping]]
        ] = ...,
        llm_powered: bool = ...,
    ) -> None: ...

class RefactoringSuggestion(_message.Message):
    __slots__ = (
        "title",
        "description",
        "original_code",
        "refactored_code",
        "reasoning",
        "impact",
        "confidence",
    )
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_CODE_FIELD_NUMBER: _ClassVar[int]
    REFACTORED_CODE_FIELD_NUMBER: _ClassVar[int]
    REASONING_FIELD_NUMBER: _ClassVar[int]
    IMPACT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    original_code: str
    refactored_code: str
    reasoning: str
    impact: str
    confidence: _metadata_pb2.ConfidenceScore
    def __init__(
        self,
        title: _Optional[str] = ...,
        description: _Optional[str] = ...,
        original_code: _Optional[str] = ...,
        refactored_code: _Optional[str] = ...,
        reasoning: _Optional[str] = ...,
        impact: _Optional[str] = ...,
        confidence: _Optional[_Union[_metadata_pb2.ConfidenceScore, _Mapping]] = ...,
    ) -> None: ...

class ExplainErrorRequest(_message.Message):
    __slots__ = ("error_message", "dsl_code", "error_line", "metadata")
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_LINE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    dsl_code: str
    error_line: int
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        error_message: _Optional[str] = ...,
        dsl_code: _Optional[str] = ...,
        error_line: _Optional[int] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class ExplainErrorResponse(_message.Message):
    __slots__ = ("explanation", "root_cause", "fix_suggestions", "llm_powered")
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    ROOT_CAUSE_FIELD_NUMBER: _ClassVar[int]
    FIX_SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    LLM_POWERED_FIELD_NUMBER: _ClassVar[int]
    explanation: str
    root_cause: str
    fix_suggestions: _containers.RepeatedCompositeFieldContainer[FixSuggestion]
    llm_powered: bool
    def __init__(
        self,
        explanation: _Optional[str] = ...,
        root_cause: _Optional[str] = ...,
        fix_suggestions: _Optional[_Iterable[_Union[FixSuggestion, _Mapping]]] = ...,
        llm_powered: bool = ...,
    ) -> None: ...

class FixSuggestion(_message.Message):
    __slots__ = ("description", "corrected_code", "confidence")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CORRECTED_CODE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    description: str
    corrected_code: str
    confidence: _metadata_pb2.ConfidenceScore
    def __init__(
        self,
        description: _Optional[str] = ...,
        corrected_code: _Optional[str] = ...,
        confidence: _Optional[_Union[_metadata_pb2.ConfidenceScore, _Mapping]] = ...,
    ) -> None: ...

class GenerateDocumentationRequest(_message.Message):
    __slots__ = ("dsl_code", "metadata")
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    dsl_code: str
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        dsl_code: _Optional[str] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class GenerateDocumentationResponse(_message.Message):
    __slots__ = (
        "summary",
        "purpose",
        "logic_steps",
        "indicators",
        "signals",
        "llm_powered",
    )
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    LOGIC_STEPS_FIELD_NUMBER: _ClassVar[int]
    INDICATORS_FIELD_NUMBER: _ClassVar[int]
    SIGNALS_FIELD_NUMBER: _ClassVar[int]
    LLM_POWERED_FIELD_NUMBER: _ClassVar[int]
    summary: str
    purpose: str
    logic_steps: _containers.RepeatedScalarFieldContainer[str]
    indicators: _containers.RepeatedScalarFieldContainer[str]
    signals: SignalConditions
    llm_powered: bool
    def __init__(
        self,
        summary: _Optional[str] = ...,
        purpose: _Optional[str] = ...,
        logic_steps: _Optional[_Iterable[str]] = ...,
        indicators: _Optional[_Iterable[str]] = ...,
        signals: _Optional[_Union[SignalConditions, _Mapping]] = ...,
        llm_powered: bool = ...,
    ) -> None: ...

class SignalConditions(_message.Message):
    __slots__ = ("buy_conditions", "sell_conditions")
    BUY_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    SELL_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    buy_conditions: _containers.RepeatedScalarFieldContainer[str]
    sell_conditions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        buy_conditions: _Optional[_Iterable[str]] = ...,
        sell_conditions: _Optional[_Iterable[str]] = ...,
    ) -> None: ...
