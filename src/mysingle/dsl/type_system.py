"""DSL Type Inference System

AST-based type checking and inference for DSL code.
"""

import ast
from dataclasses import dataclass
from enum import Enum
from typing import Any


class DSLType(Enum):
    """DSL type categories"""

    UNKNOWN = "unknown"
    SERIES = "series"  # pd.Series
    DATAFRAME = "dataframe"  # pd.DataFrame
    SCALAR = "scalar"  # int, float, bool
    BOOLEAN_SERIES = "boolean_series"  # pd.Series[bool] for signals
    INDICATOR = "indicator"  # Calculated indicator result
    OHLCV = "ohlcv"  # OHLCV DataFrame with required columns


@dataclass
class TypeInfo:
    """Type information for a variable/expression"""

    type: DSLType
    nullable: bool = False
    element_type: DSLType | None = None  # For Series/DataFrame
    shape: tuple[int, ...] | None = None
    metadata: dict[str, Any] | None = None

    def __str__(self) -> str:
        base = self.type.value
        if self.element_type:
            base += f"[{self.element_type.value}]"
        if self.nullable:
            base += "?"
        return base


class TypeInferenceEngine:
    """AST-based type inference for DSL code"""

    def __init__(self):
        self.type_env: dict[str, TypeInfo] = {}
        self.ohlcv_columns = {"open", "high", "low", "close", "volume"}

    def infer(self, code: str) -> dict[str, TypeInfo]:
        """
        Infer types for all variables in DSL code

        Args:
            code: DSL source code

        Returns:
            dict mapping variable names to their type info
        """
        tree = ast.parse(code)
        self.type_env = {}

        # Initialize data parameter type
        self.type_env["data"] = TypeInfo(
            type=DSLType.OHLCV,
            nullable=False,
            metadata={"columns": self.ohlcv_columns},
        )

        # Traverse AST and infer types
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                self._infer_assignment(node)
            elif isinstance(node, ast.AugAssign):
                self._infer_aug_assignment(node)

        return self.type_env

    def _infer_assignment(self, node: ast.Assign):
        """Infer type from assignment"""
        # Get value type
        value_type = self._infer_expr_type(node.value)

        # Assign to all targets
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.type_env[target.id] = value_type

    def _infer_aug_assignment(self, node: ast.AugAssign):
        """Infer type from augmented assignment (+=, -=, etc.)"""
        target_name = node.target.id if isinstance(node.target, ast.Name) else None
        if target_name and target_name not in self.type_env:
            value_type = self._infer_expr_type(node.value)
            self.type_env[target_name] = value_type

    def _infer_expr_type(self, node: ast.expr) -> TypeInfo:
        """Infer type of an expression"""

        # Subscript: data['close'] → Series
        if isinstance(node, ast.Subscript):
            return self._infer_subscript_type(node)

        # Call: SMA(data['close'], 20) → Series
        elif isinstance(node, ast.Call):
            return self._infer_call_type(node)

        # BinOp: series1 + series2 → Series
        elif isinstance(node, ast.BinOp):
            return self._infer_binop_type(node)

        # Compare: series1 > series2 → BooleanSeries
        elif isinstance(node, (ast.Compare, ast.BoolOp)):
            return TypeInfo(type=DSLType.BOOLEAN_SERIES)

        # Constant
        elif isinstance(node, ast.Constant):
            return TypeInfo(type=DSLType.SCALAR, nullable=False)

        # Name: variable lookup
        elif isinstance(node, ast.Name):
            return self.type_env.get(node.id, TypeInfo(type=DSLType.UNKNOWN))

        # Default: unknown
        return TypeInfo(type=DSLType.UNKNOWN)

    def _infer_subscript_type(self, node: ast.Subscript) -> TypeInfo:
        """Infer type from subscript access"""

        # data['close'] → Series
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "data"
            and isinstance(node.slice, ast.Constant)
        ):
            column = node.slice.value
            if column in self.ohlcv_columns:
                return TypeInfo(
                    type=DSLType.SERIES,
                    element_type=DSLType.SCALAR,
                    nullable=False,
                )

        # Default to Series
        return TypeInfo(type=DSLType.SERIES, nullable=True)

    def _infer_call_type(self, node: ast.Call) -> TypeInfo:
        """Infer type from function call"""

        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

        # Known indicator functions → Series
        if func_name in {
            "SMA",
            "EMA",
            "RSI",
            "ATR",
            "highest",
            "lowest",
            "stdev",
            "WMA",
        }:
            return TypeInfo(type=DSLType.SERIES, element_type=DSLType.SCALAR)

        # crossover/crossunder → BooleanSeries
        elif func_name in {"crossover", "crossunder"}:
            return TypeInfo(type=DSLType.BOOLEAN_SERIES)

        # bbands → DataFrame (multi-output)
        elif func_name == "bbands":
            return TypeInfo(type=DSLType.DATAFRAME)

        # Default: unknown
        return TypeInfo(type=DSLType.UNKNOWN)

    def _infer_binop_type(self, node: ast.BinOp) -> TypeInfo:
        """Infer type from binary operation"""

        left_type = self._infer_expr_type(node.left)
        right_type = self._infer_expr_type(node.right)

        # Series + Scalar → Series
        if left_type.type == DSLType.SERIES:
            return left_type
        elif right_type.type == DSLType.SERIES:
            return right_type

        # Scalar + Scalar → Scalar
        return TypeInfo(type=DSLType.SCALAR)

    def validate_types(self, code: str) -> list[str]:
        """
        Validate type consistency in DSL code

        Returns:
            List of type error messages
        """
        errors = []
        types = self.infer(code)

        # Check for 'result' variable
        if "result" not in types:
            errors.append("Missing 'result' variable assignment")
        else:
            result_type = types["result"]
            # Strategy must return boolean series
            if result_type.type not in {DSLType.BOOLEAN_SERIES, DSLType.SERIES}:
                errors.append(
                    f"'result' must be a Series (preferably boolean), got {result_type}"
                )

        return errors


def check_types(code: str) -> tuple[bool, list[str], dict[str, TypeInfo]]:
    """
    Convenience function for type checking

    Args:
        code: DSL source code

    Returns:
        (is_valid, errors, type_info)
    """
    engine = TypeInferenceEngine()
    types = engine.infer(code)
    errors = engine.validate_types(code)

    return len(errors) == 0, errors, types
