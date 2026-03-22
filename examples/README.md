# Examples

Runnable scripts that demonstrate graphworks features. These are **not**
shipped with the library (the `examples/` directory is excluded from both the
sdist and wheel).

## Running

The recommended way is via the `uv run` script alias defined in
`pyproject.toml`:

```sh
uv run demo
```

You can also invoke the file directly:

```sh
uv run python examples/demo.py
```

## Adding new examples

1. Create a new `.py` file in this directory.
2. Give it a `main()` entry point.
3. Register it in `pyproject.toml` under `[project.scripts]`:

   ```toml
   [project.scripts]
   demo = "examples.demo:main"        # existing
   my-example = "examples.my_example:main"  # new
   ```

4. Make sure `"examples"` appears in
   `[tool.hatch.build.targets.sdist].exclude` so examples stay out of the published package.
