import invoke

from compas_invocations.console import chdir


@invoke.task()
def lint(ctx):
    """Check the consistency of coding style."""
    print("Running flake8 python linter...")
    ctx.run("flake8 src tests")

    print("Running black python linter...")
    ctx.run("black --check --diff --color src tests")


@invoke.task()
def format(ctx):
    """Reformat the code base using black."""
    print("Running black python formatter...")
    ctx.run("black src tests")


@invoke.task()
def check(ctx):
    """Check the consistency of documentation, coding style and a few other things."""

    with chdir(ctx.base_folder):
        lint(ctx)

        print("Checking MANIFEST.in...")
        ctx.run("check-manifest")

        print("Checking metadata...")
        ctx.run("python setup.py check --strict --metadata")
