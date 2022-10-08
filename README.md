# compas_invocations

A collection of reusable pyinvoke tasks

## Usage

Import and add tasks to a collection in your project's `tasks.py` file:

    import os
    from invoke import Collection
    from compas_invocations import style

    ns = Collection(style.check, style.lint)
    ns.configure(
        {
            "base_folder": os.path.dirname(__file__),
        }
    )

For a more complete example, check the [`tasks.py`](tasks.py) of this project.
