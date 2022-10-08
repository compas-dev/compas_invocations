import invoke
from compas_invocations.console import chdir


@invoke.task()
def test(ctx, doctest=False):
    """Run all tests."""
    with chdir(ctx.base_folder):
        if doctest:
            ctx.run("pytest --doctest-modules")
        else:
            ctx.run("pytest")


@invoke.task()
def testdocs(ctx):
    """Test the examples in the docstrings."""
    print("Running doctest...")
    ctx.run("pytest --doctest-modules")
