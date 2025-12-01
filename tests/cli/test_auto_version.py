"""Conventional Commits 자동 버전 관리 테스트."""

from __future__ import annotations

import subprocess

import pytest

from mysingle.cli.core.auto_version import (
    CommitInfo,
    analyze_commits,
    get_commits_since_tag,
)
from mysingle.cli.core.version import Version


class TestCommitInfo:
    """CommitInfo 클래스 테스트"""

    def test_is_breaking_with_exclamation(self):
        """! 마크가 있는 breaking change 감지"""
        commit = CommitInfo("abc123", "feat!: breaking change", [])
        assert commit.is_breaking is True

    def test_is_breaking_with_body(self):
        """BREAKING CHANGE: 문구가 있는 breaking change 감지"""
        commit = CommitInfo(
            "abc123", "feat: new feature\n\nBREAKING CHANGE: API changed", []
        )
        assert commit.is_breaking is True

    def test_is_breaking_false(self):
        """일반 커밋은 breaking change 아님"""
        commit = CommitInfo("abc123", "feat: normal feature", [])
        assert commit.is_breaking is False

    def test_is_feat(self):
        """feat 커밋 감지"""
        commit = CommitInfo("abc123", "feat: add feature", [])
        assert commit.is_feat is True

    def test_is_fix(self):
        """fix 커밋 감지"""
        commit = CommitInfo("abc123", "fix: resolve bug", [])
        assert commit.is_fix is True

    def test_is_proto_only(self):
        """Proto 파일만 변경된 커밋 감지"""
        commit = CommitInfo("abc123", "proto: update schema", ["protos/user.proto"])
        assert commit.is_proto_only is True

        commit2 = CommitInfo(
            "abc123", "feat: add field", ["src/mysingle/protos/user_pb2.py"]
        )
        assert commit2.is_proto_only is True

    def test_is_proto_only_false(self):
        """일반 파일 포함된 경우"""
        commit = CommitInfo(
            "abc123", "feat: update", ["protos/user.proto", "src/app.py"]
        )
        assert commit.is_proto_only is False

    def test_is_proto_related(self):
        """Proto 관련 변경 포함 여부"""
        commit = CommitInfo(
            "abc123", "feat: update", ["protos/user.proto", "src/app.py"]
        )
        assert commit.is_proto_related is True

    def test_type_extraction(self):
        """커밋 타입 추출"""
        assert CommitInfo("abc", "feat: msg", []).type == "feat"
        assert CommitInfo("abc", "fix: msg", []).type == "fix"
        assert CommitInfo("abc", "feat(scope): msg", []).type == "feat"
        assert CommitInfo("abc", "feat!: msg", []).type == "feat"
        assert CommitInfo("abc", "invalid message", []).type == "unknown"


class TestAnalyzeCommits:
    """커밋 분석 테스트"""

    def test_breaking_change_major_bump(self):
        """Breaking change → major 버전 증가"""
        commits = [
            CommitInfo("abc", "feat!: breaking change", []),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "major"
        assert len(result["breaking_changes"]) == 1

    def test_feature_minor_bump(self):
        """Feature → minor 버전 증가"""
        commits = [
            CommitInfo("abc", "feat: add feature", ["src/app.py"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "minor"
        assert len(result["features"]) == 1

    def test_fix_patch_bump(self):
        """Fix → patch 버전 증가"""
        commits = [
            CommitInfo("abc", "fix: resolve bug", ["src/app.py"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "patch"
        assert len(result["fixes"]) == 1

    def test_proto_only_feature_no_main_bump(self):
        """Proto만 변경된 feature → 메인 버전 유지"""
        commits = [
            CommitInfo("abc", "feat: add field", ["protos/user.proto"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "none"
        assert result["proto_bump"] is True

    def test_proto_only_fix_no_main_bump(self):
        """Proto만 변경된 fix → 메인 버전 유지"""
        commits = [
            CommitInfo("abc", "fix: correct type", ["protos/user.proto"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "none"
        assert result["proto_bump"] is True

    def test_mixed_commits(self):
        """여러 타입 커밋 혼합"""
        commits = [
            CommitInfo("abc", "feat: add feature", ["src/app.py"]),
            CommitInfo("def", "fix: resolve bug", ["src/app.py"]),
            CommitInfo("ghi", "docs: update README", ["README.md"]),
            CommitInfo("jkl", "proto: update schema", ["protos/user.proto"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "minor"  # feat takes precedence
        assert result["proto_bump"] is True
        assert len(result["features"]) == 1
        assert len(result["fixes"]) == 1
        assert len(result["proto_changes"]) == 1

    def test_no_version_bump(self):
        """버전 변경 불필요한 커밋만"""
        commits = [
            CommitInfo("abc", "docs: update docs", ["docs/README.md"]),
            CommitInfo("def", "chore: update deps", ["pyproject.toml"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "none"
        assert result["proto_bump"] is False

    def test_priority_major_over_minor(self):
        """Breaking change가 feature보다 우선"""
        commits = [
            CommitInfo("abc", "feat: add feature", ["src/app.py"]),
            CommitInfo("def", "feat!: breaking change", ["src/api.py"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "major"

    def test_priority_minor_over_patch(self):
        """Feature가 fix보다 우선"""
        commits = [
            CommitInfo("abc", "fix: bug fix", ["src/app.py"]),
            CommitInfo("def", "feat: new feature", ["src/api.py"]),
        ]
        result = analyze_commits(commits)
        assert result["bump_type"] == "minor"


class TestVersionBumping:
    """버전 범핑 로직 테스트"""

    def test_major_bump(self):
        """Major 버전 증가"""
        v = Version(2, 0, 1)
        new = v.bump("major")
        assert str(new) == "3.0.0"

    def test_minor_bump(self):
        """Minor 버전 증가"""
        v = Version(2, 0, 1)
        new = v.bump("minor")
        assert str(new) == "2.1.0"

    def test_patch_bump(self):
        """Patch 버전 증가"""
        v = Version(2, 0, 1)
        new = v.bump("patch")
        assert str(new) == "2.0.2"


@pytest.mark.skipif(
    subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True).returncode
    != 0,
    reason="Not a git repository",
)
class TestGitIntegration:
    """Git 통합 테스트 (실제 저장소에서만 실행)"""

    def test_get_commits_since_tag(self):
        """마지막 태그 이후 커밋 가져오기"""
        # This test will only run in an actual git repo
        try:
            commits = get_commits_since_tag()
            # Should return a list (might be empty)
            assert isinstance(commits, list)
            for commit in commits:
                assert isinstance(commit, CommitInfo)
                assert commit.sha
                assert commit.message
        except subprocess.CalledProcessError:
            # No tags yet, that's okay
            pytest.skip("No git tags found")
