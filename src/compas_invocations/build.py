import glob
import os
import shutil
import tempfile

import invoke

from compas_invocations.console import chdir
from compas_invocations.console import confirm


@invoke.task(
    help={
        "docs": "True to clean up generated documentation, otherwise False",
        "bytecode": "True to clean up compiled python files, otherwise False.",
        "builds": "True to clean up build/packaging artifacts, otherwise False.",
    }
)
def clean(ctx, docs=True, bytecode=True, builds=True, ghuser=True):
    """Cleans the local copy from compiled artifacts."""

    with chdir(ctx.base_folder):
        if builds:
            ctx.run("python setup.py clean")

        if bytecode:
            for root, dirs, files in os.walk(ctx.base_folder):
                for f in files:
                    if f.endswith(".pyc"):
                        os.remove(os.path.join(root, f))
                if ".git" in dirs:
                    dirs.remove(".git")

        folders = []

        if docs:
            folders.append("docs/api/generated")

        folders.append("dist/")

        if bytecode:
            for t in ("src", "tests"):
                folders.extend(glob.glob("{}/**/__pycache__".format(t), recursive=True))

        if builds:
            folders.append("build/")
            folders.extend(glob.glob("src/**/*.egg-info", recursive=False))

        for folder in folders:
            shutil.rmtree(os.path.join(ctx.base_folder, folder), ignore_errors=True)


@invoke.task(help={"release_type": "Type of release follows semver rules. Must be one of: major, minor, patch."})
def release(ctx, release_type):
    """Releases the project in one swift command!"""
    if release_type not in ("patch", "minor", "major"):
        raise invoke.Exit("The release type parameter is invalid.\nMust be one of: major, minor, patch.")

    # Run formatter
    ctx.run("invoke format")

    # Run checks
    ctx.run("invoke check test")

    # Bump version and git tag it
    ctx.run("bump2version %s --verbose" % release_type)

    # Build project
    ctx.run("python setup.py clean --all sdist bdist_wheel")

    # Prepare the change log for the next release
    prepare_changelog(ctx)

    # Clean up local artifacts
    clean(ctx)

    # Upload to pypi
    if confirm(
        "Everything is ready. You are about to push to git which will trigger a release to pypi.org. Are you sure?",
        assume_yes=False,
    ):
        ctx.run("git push --tags && git push")
    else:
        raise invoke.Exit("You need to manually revert the tag/commits created.")


@invoke.task
def prepare_changelog(ctx):
    """Prepare changelog for next release."""
    UNRELEASED_CHANGELOG_TEMPLATE = "## Unreleased\n\n### Added\n\n### Changed\n\n### Removed\n\n\n## "

    with chdir(ctx.base_folder):
        # Preparing changelog for next release
        with open("CHANGELOG.md", "r+") as changelog:
            content = changelog.read()
            changelog.seek(0)
            changelog.write(content.replace("## ", UNRELEASED_CHANGELOG_TEMPLATE, 1))

        ctx.run('git add CHANGELOG.md && git commit -m "Prepare changelog for next release"')


@invoke.task(
    help={
        "gh_io_folder": "Folder where GH_IO.dll is located. Defaults to the Rhino 6.0 installation folder (platform-specific).",
        "ironpython": "Command for running the IronPython executable. Defaults to `ipy`.",
    }
)
def build_ghuser_components(ctx, gh_io_folder=None, ironpython=None, prefix=None):
    """Builds Grasshopper components using GH Componentizer."""
    prefix = prefix or ctx.ghuser.prefix
    source_dir = os.path.abspath(ctx.ghuser.source_dir)
    target_dir = os.path.abspath(ctx.ghuser.target_dir)
    repo_url = "https://github.com/compas-dev/compas-actions.ghpython_components.git"

    with chdir(ctx.base_folder):
        shutil.rmtree(os.path.join(ctx.base_folder, target_dir), ignore_errors=True)

    """Build Grasshopper user objects from source"""
    with chdir(ctx.base_folder):
        with tempfile.TemporaryDirectory("actions.ghcomponentizer") as action_dir:
            ctx.run("git clone {} {}".format(repo_url, action_dir))

            if not gh_io_folder:
                gh_io_folder = tempfile.mkdtemp("ghio")
                import compas_ghpython

                compas_ghpython.fetch_ghio_lib(gh_io_folder)

            if not ironpython:
                ironpython = "ipy"

            gh_io_folder = os.path.abspath(gh_io_folder)
            componentizer_script = os.path.join(action_dir, "componentize.py")

            cmd = "{} {} {} {}".format(ironpython, componentizer_script, source_dir, target_dir)
            cmd += ' --ghio "{}"'.format(gh_io_folder)
            if prefix:
                cmd += ' --prefix "{}"'.format(prefix)

            ctx.run(cmd)
