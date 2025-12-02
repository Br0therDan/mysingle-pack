#!/usr/bin/env python3
"""Proto import 테스트 스크립트

protobuf 6.x 호환성 검증을 위한 모든 proto 파일 import 테스트
"""

import sys


def test_proto_imports():
    """모든 proto 서비스 import 테스트"""
    print("=" * 60)
    print("  Proto Import 테스트 (protobuf 6.x 호환성)")
    print("=" * 60)
    print()

    services = [
        (
            "Indicator Service",
            "mysingle.protos.services.indicator.v1",
            "indicator_service_pb2",
        ),
        (
            "Market Data Service",
            "mysingle.protos.services.market_data.v1",
            "market_data_service_pb2",
        ),
        (
            "Backtest Service",
            "mysingle.protos.services.backtest.v1",
            "backtest_service_pb2",
        ),
        ("IAM Service", "mysingle.protos.services.iam.v1", "iam_service_pb2"),
        ("ML Service", "mysingle.protos.services.ml.v1", "ml_service_pb2"),
        (
            "Strategy Service",
            "mysingle.protos.services.strategy.v1",
            "strategy_service_pb2",
        ),
        ("DSL Validator", "mysingle.protos.services.genai.v1", "dsl_validator_pb2"),
        (
            "Strategy Builder",
            "mysingle.protos.services.genai.v1",
            "strategy_builder_pb2",
        ),
        ("Narrative", "mysingle.protos.services.genai.v1", "narrative_pb2"),
        ("ChatOps", "mysingle.protos.services.genai.v1", "chatops_pb2"),
        ("IR Converter", "mysingle.protos.services.genai.v1", "ir_converter_pb2"),
    ]

    common_protos = [
        ("Error", "mysingle.protos.common", "error_pb2"),
        ("Metadata", "mysingle.protos.common", "metadata_pb2"),
        ("Pagination", "mysingle.protos.common", "pagination_pb2"),
    ]

    failed = []
    passed = []

    # Common protos 테스트
    print("📦 Common Protos:")
    for name, module_path, module_name in common_protos:
        try:
            module = __import__(f"{module_path}.{module_name}", fromlist=[module_name])
            descriptor_name = (
                module.DESCRIPTOR.name if hasattr(module, "DESCRIPTOR") else "N/A"
            )
            print(f"  ✅ {name}: {descriptor_name}")
            passed.append(name)
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed.append((name, str(e)))

    print()

    # Service protos 테스트
    print("🚀 Service Protos:")
    for name, module_path, module_name in services:
        try:
            module = __import__(f"{module_path}.{module_name}", fromlist=[module_name])
            descriptor_name = (
                module.DESCRIPTOR.name if hasattr(module, "DESCRIPTOR") else "N/A"
            )
            print(f"  ✅ {name}: {descriptor_name}")
            passed.append(name)
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed.append((name, str(e)))

    print()
    print("=" * 60)
    print(f"✅ 통과: {len(passed)}개")
    print(f"❌ 실패: {len(failed)}개")

    if failed:
        print()
        print("실패 상세:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return 1

    print()
    print("🎉 모든 proto import 테스트 통과!")
    return 0


if __name__ == "__main__":
    sys.exit(test_proto_imports())
