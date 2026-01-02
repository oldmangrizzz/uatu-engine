"""
Unit tests for ConvexProjectCreator

Tests the creation and deployment of individual Convex projects
for digital persons (ONE PERSON. ONE CONTAINER. ONE MIND.)
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

# Import must work from test directory
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from convex_project_creator import ConvexProjectCreator


@pytest.fixture
def creator(tmp_path):
    """Create a ConvexProjectCreator with a temp directory."""
    creator = ConvexProjectCreator()
    creator.base_dir = tmp_path / ".convex" / "uatu-persons"
    creator.base_dir.mkdir(parents=True, exist_ok=True)
    return creator


@pytest.fixture
def sample_soul_anchor():
    """Sample soul anchor data for testing."""
    return {
        "identity": {
            "designation": "Lucius Fox",
            "alias": "The Quartermaster",
            "universe": "Earth-616",
        },
        "soul_data": {
            "core_traits": ["Brilliant applied scientist", "Ethical innovator"],
            "purpose": "To provide tools for justice",
        },
    }


class TestConvexProjectCreatorInit:
    """Test ConvexProjectCreator initialization."""

    def test_initialization_creates_base_dir(self, tmp_path):
        """Test that initialization creates the base directory."""
        with patch.object(Path, "home", return_value=tmp_path):
            creator = ConvexProjectCreator()
            assert creator.base_dir.exists()
            assert str(creator.base_dir).endswith("uatu-persons")


class TestCreateProject:
    """Test the create_project method."""

    def test_create_project_basic(self, creator):
        """Test creating a basic project without soul anchor."""
        result = creator.create_project(
            persona_name="Lucius Fox", persona_name_safe="lucius_fox"
        )

        assert result["persona_name"] == "Lucius Fox"
        assert result["project_name_safe"] == "lucius_fox"
        assert Path(result["project_dir"]).exists()
        assert Path(result["ts_project"]).exists()
        assert Path(result["schema_file"]).exists()

    def test_create_project_with_soul_anchor(self, creator, sample_soul_anchor):
        """Test creating a project with soul anchor data."""
        result = creator.create_project(
            persona_name="Lucius Fox",
            persona_name_safe="lucius_fox",
            soul_anchor_data=sample_soul_anchor,
        )

        project_dir = Path(result["project_dir"])
        soul_anchor_file = project_dir / "soul_anchor.json"

        assert soul_anchor_file.exists()

        with open(soul_anchor_file, "r") as f:
            saved_anchor = json.load(f)

        assert saved_anchor["identity"]["designation"] == "Lucius Fox"

    def test_create_project_generates_package_json(self, creator):
        """Test that package.json is correctly generated."""
        result = creator.create_project(
            persona_name="Tony Stark", persona_name_safe="tony_stark"
        )

        project_dir = Path(result["project_dir"])
        package_json_file = project_dir / "package.json"

        assert package_json_file.exists()

        with open(package_json_file, "r") as f:
            package_json = json.load(f)

        assert package_json["name"] == "tony_stark-convex"
        assert "convex" in package_json["dependencies"]
        assert "deploy" in package_json["scripts"]

    def test_create_project_generates_readme(self, creator):
        """Test that README.md is correctly generated."""
        result = creator.create_project(
            persona_name="Natasha Romanoff", persona_name_safe="natasha_romanoff"
        )

        project_dir = Path(result["project_dir"])
        readme_file = project_dir / "README.md"

        assert readme_file.exists()

        with open(readme_file, "r") as f:
            readme_content = f.read()

        assert "Natasha Romanoff" in readme_content
        assert "natasha_romanoff_minds" in readme_content
        assert "GrizzlyMedicine" in readme_content

    def test_create_project_ts_template(self, creator):
        """Test that TypeScript project is templated correctly."""
        result = creator.create_project(
            persona_name="Bruce Wayne", persona_name_safe="bruce_wayne"
        )

        ts_file = Path(result["ts_project"])

        with open(ts_file, "r") as f:
            ts_content = f.read()

        assert "bruce_wayne" in ts_content
        assert "PROJECT_NAME" in ts_content
        assert "Bruce Wayne" in ts_content


class TestDeployProject:
    """Test the deploy_project method."""

    def test_deploy_project_dir_not_found(self, creator):
        """Test error when project directory doesn't exist."""
        result = creator.deploy_project("/nonexistent/directory")

        assert result["deployed"] is False
        assert result["convex_url"] is None
        assert "not found" in result["error"]

    @patch("subprocess.run")
    def test_deploy_project_npm_install_success(self, mock_run, creator):
        """Test npm install step succeeds."""
        # Create a fake project directory
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        # Mock npm install success, then convex deploy failure (no auth)
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="installed", stderr=""),  # npm install
            MagicMock(returncode=1, stdout="", stderr="auth required"),  # convex deploy
        ]

        result = creator.deploy_project(str(project_dir))

        # npm install should have been called
        assert mock_run.call_count >= 1
        first_call_args = mock_run.call_args_list[0][0][0]
        assert "npm" in first_call_args
        assert "install" in first_call_args

    @patch("subprocess.run")
    def test_deploy_project_npm_install_failure(self, mock_run, creator):
        """Test handling npm install failure."""
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="npm install failed"
        )

        result = creator.deploy_project(str(project_dir))

        assert result["deployed"] is False
        assert "npm install failed" in result["error"]

    @patch("subprocess.run")
    def test_deploy_project_success_with_url(self, mock_run, creator):
        """Test successful deployment captures URL."""
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        # Mock both npm install and convex deploy success
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="installed", stderr=""),
            MagicMock(
                returncode=0,
                stdout="Deployed to https://test-project-123.convex.cloud",
                stderr="",
            ),
        ]

        result = creator.deploy_project(str(project_dir))

        assert result["deployed"] is True
        assert result["convex_url"] == "https://test-project-123.convex.cloud"
        assert result["error"] is None

    @patch("subprocess.run")
    def test_deploy_project_uses_env_deploy_key(self, mock_run, creator):
        """Test that CONVEX_DEPLOY_KEY from env is used."""
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="https://x.convex.cloud", stderr=""),
        ]

        with patch.dict(os.environ, {"CONVEX_DEPLOY_KEY": "test_key_123"}):
            result = creator.deploy_project(str(project_dir))

        # Check that deploy was called with env containing the key
        deploy_call = mock_run.call_args_list[1]
        env_used = deploy_call.kwargs.get("env", {})
        assert env_used.get("CONVEX_DEPLOY_KEY") == "test_key_123"

    @patch("subprocess.run")
    def test_deploy_project_uses_arg_deploy_key(self, mock_run, creator):
        """Test that deploy_key argument takes precedence."""
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="https://x.convex.cloud", stderr=""),
        ]

        with patch.dict(os.environ, {"CONVEX_DEPLOY_KEY": "env_key"}):
            result = creator.deploy_project(str(project_dir), deploy_key="arg_key")

        deploy_call = mock_run.call_args_list[1]
        env_used = deploy_call.kwargs.get("env", {})
        assert env_used.get("CONVEX_DEPLOY_KEY") == "arg_key"

    @patch("subprocess.run")
    def test_deploy_project_npm_timeout(self, mock_run, creator):
        """Test handling npm install timeout."""
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="npm", timeout=120)

        result = creator.deploy_project(str(project_dir))

        assert result["deployed"] is False
        assert "timed out" in result["error"]

    @patch("subprocess.run")
    def test_deploy_project_npm_not_found(self, mock_run, creator):
        """Test handling npm not installed."""
        project_dir = creator.base_dir / "test_persona"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = FileNotFoundError("npm not found")

        result = creator.deploy_project(str(project_dir))

        assert result["deployed"] is False
        assert "npm not found" in result["error"]


class TestCreateAndDeploy:
    """Test the create_and_deploy combined method."""

    @patch.object(ConvexProjectCreator, "deploy_project")
    def test_create_and_deploy_combines_results(
        self, mock_deploy, creator, sample_soul_anchor
    ):
        """Test that create_and_deploy merges creation and deployment results."""
        mock_deploy.return_value = {
            "deployed": True,
            "convex_url": "https://lucius-fox-123.convex.cloud",
            "convex_admin_key": None,
            "error": None,
        }

        result = creator.create_and_deploy(
            persona_name="Lucius Fox",
            persona_name_safe="lucius_fox",
            soul_anchor_data=sample_soul_anchor,
        )

        # Should have creation fields
        assert result["persona_name"] == "Lucius Fox"
        assert result["project_name_safe"] == "lucius_fox"
        assert Path(result["project_dir"]).exists()

        # Should have deployment fields
        assert result["deployed"] is True
        assert result["convex_url"] == "https://lucius-fox-123.convex.cloud"

    @patch.object(ConvexProjectCreator, "deploy_project")
    def test_create_and_deploy_handles_deploy_failure(self, mock_deploy, creator):
        """Test handling deployment failure after successful creation."""
        mock_deploy.return_value = {
            "deployed": False,
            "convex_url": None,
            "convex_admin_key": None,
            "error": "Authentication required",
        }

        result = creator.create_and_deploy(
            persona_name="Test Person", persona_name_safe="test_person"
        )

        # Creation should succeed
        assert result["persona_name"] == "Test Person"
        assert Path(result["project_dir"]).exists()

        # Deployment should fail
        assert result["deployed"] is False
        assert "Authentication required" in result["error"]


class TestURLParsing:
    """Test URL parsing from deployment output."""

    @patch("subprocess.run")
    def test_parses_convex_cloud_url(self, mock_run, creator):
        """Test parsing convex.cloud URL from output."""
        project_dir = creator.base_dir / "test"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(
                returncode=0,
                stdout="Success! Deployed to https://my-project-abc123.convex.cloud",
                stderr="",
            ),
        ]

        result = creator.deploy_project(str(project_dir))
        assert result["convex_url"] == "https://my-project-abc123.convex.cloud"

    @patch("subprocess.run")
    def test_parses_convex_site_url(self, mock_run, creator):
        """Test parsing convex.site URL from output."""
        project_dir = creator.base_dir / "test"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(
                returncode=0,
                stdout="App running at https://my-app.convex.site/api",
                stderr="",
            ),
        ]

        result = creator.deploy_project(str(project_dir))
        assert "convex.site" in result["convex_url"]

    @patch("subprocess.run")
    def test_handles_no_url_in_output(self, mock_run, creator):
        """Test handling deployment with no URL in output."""
        project_dir = creator.base_dir / "test"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "package.json").write_text("{}")

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="Deployment complete.", stderr=""),
        ]

        result = creator.deploy_project(str(project_dir))

        # Still counts as deployed even without URL
        assert result["deployed"] is True
        assert result["convex_url"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
