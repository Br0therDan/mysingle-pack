#!/usr/bin/env python3
"""MySingle Package 전체 Import 테스트 스크립트

모든 mysingle 패키지 모듈의 import 가능 여부를 검증합니다.
"""

import importlib
import pkgutil
import sys
import traceback


def get_module_path(module_name: str) -> str:
    """모듈의 파일 경로를 반환"""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "__file__") and module.__file__:
            return module.__file__
        return f"<{module_name}>"
    except Exception:
        return "<unknown>"


def test_all_imports():
    """mysingle 패키지의 모든 모듈 import 테스트"""
    print("=" * 80)
    print("  MySingle Package 전체 Import 테스트")
    print("=" * 80)
    print()

    try:
        import mysingle
    except Exception as e:
        print(f"❌ mysingle 패키지를 찾을 수 없습니다: {e}")
        return 1

    failed = []
    passed = []
    skipped = []

    # mysingle 패키지의 모든 하위 모듈 탐색
    def walk_packages(package, prefix=""):
        """재귀적으로 패키지의 모든 모듈 탐색"""
        if hasattr(package, "__path__"):
            for _importer, modname, ispkg in pkgutil.walk_packages(
                package.__path__, prefix=f"{package.__name__}."
            ):
                yield modname, ispkg

    print("🔍 모듈 탐색 중...")
    all_modules = list(walk_packages(mysingle))
    print(f"   발견된 모듈: {len(all_modules)}개\n")

    # 각 모듈 import 테스트
    for module_name, is_package in sorted(all_modules):
        # 테스트 모듈은 스킵
        if ".tests." in module_name or module_name.endswith(".tests"):
            skipped.append(module_name)
            continue

        # __pycache__ 등 스킵
        if "__pycache__" in module_name:
            skipped.append(module_name)
            continue

        try:
            importlib.import_module(module_name)
            module_path = get_module_path(module_name)
            pkg_mark = "📦" if is_package else "📄"
            print(f"  ✅ {pkg_mark} {module_name}")
            passed.append((module_name, module_path))
        except Exception as e:
            module_path = get_module_path(module_name)
            error_msg = str(e)
            # 짧은 에러 메시지만 표시
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"  ❌ {'📦' if is_package else '📄'} {module_name}")
            print(f"     경로: {module_path}")
            print(f"     에러: {error_msg}")
            failed.append((module_name, module_path, str(e), traceback.format_exc()))

    # 결과 요약
    print()
    print("=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print(f"✅ 성공: {len(passed)}개")
    print(f"❌ 실패: {len(failed)}개")
    print(f"⏭️  스킵: {len(skipped)}개")
    print(f"📈 총계: {len(passed) + len(failed) + len(skipped)}개")

    if failed:
        print()
        print("=" * 80)
        print("❌ 실패 상세")
        print("=" * 80)
        for idx, (name, path, error, tb) in enumerate(failed, 1):
            print(f"\n{idx}. {name}")
            print(f"   파일: {path}")
            print(f"   에러: {error}")
            if "--verbose" in sys.argv or "-v" in sys.argv:
                print("\n   Traceback:")
                for line in tb.split("\n"):
                    if line.strip():
                        print(f"   {line}")
        return 1

    print()
    print("🎉 모든 모듈 import 테스트 통과!")
    print()
    print("💡 Tip: --verbose 또는 -v 옵션으로 상세한 traceback을 볼 수 있습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(test_all_imports())
