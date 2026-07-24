# The beautiful data-science setup

If you care this much about notebook colors...

there is a non-negligible chance you care about your VS Code colors too.

My completely peer-unreviewed Bayesian estimate:

$$
P(\text{Catppuccin} \cup \text{rainbow indents} \mid
\text{you starred wm-notecards}) \gg 0
$$

I did not calculate the posterior.

I did install the extensions.

This is the small, opinionated setup behind the project. It is a starting point, not a
claim that everybody already knows or wants the same tools. If it don't apply, let it
fly.

## The chosen stack

| Job | Choice | Why it stays |
|---|---|---|
| Python projects and lockfile | [uv](https://docs.astral.sh/uv/guides/projects/) | One project file, local environment, lockfile, run, sync, and build workflow |
| Python lint + format | [Ruff](https://docs.astral.sh/ruff/editors/setup/) | Fast feedback in the editor and the same checks in CI |
| Python language feedback | [Python + Pylance](https://code.visualstudio.com/docs/languages/python) | Interpreter selection, notebook support, navigation, tests, and type diagnostics |
| Runtime input contracts | [Pydantic](https://pydantic.dev/docs/validation/latest/get-started/) | Type-hint-driven validation for boundaries where data must meet a schema |
| Web lint + format | [Biome](https://biomejs.dev/reference/vscode/) | One formatter/linter path for modern JS, TS, JSX, JSON, HTML, and CSS projects |
| Notebook editing | [Jupyter for VS Code](https://code.visualstudio.com/docs/languages/python#_jupyter-notebooks) | Cells, kernels, IntelliSense, execution, and debugging in the editor |
| Palette | [Catppuccin](https://marketplace.visualstudio.com/items?itemName=Catppuccin.catppuccin-vsc) | A coordinated light/dark family instead of unrelated UI colors |
| Structure cue | [Indent-Rainbow](https://marketplace.visualstudio.com/items?itemName=oderwat.indent-rainbow) | Indentation becomes visible before a nesting mistake becomes a bug |
| Loud diagnostics | [Error Lens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens) | Moves diagnostics next to the line that earned them |

The VS Code Problems panel is not decorative. Click the warning/error count or press
`Shift+Command+M` on macOS (`Ctrl+Shift+M` on Windows/Linux) to open the list. Copy the
specific diagnostic into your AI conversation with the relevant code and expected
behavior. The message is evidence, not an insult.

## Extension IDs

```text
Catppuccin.catppuccin-vsc
Catppuccin.catppuccin-vsc-icons
charliermarsh.ruff
ms-python.python
ms-python.vscode-pylance
ms-toolsai.jupyter
biomejs.biome
oderwat.indent-rainbow
usernamehw.errorlens
```

## Safe workspace settings

Put project-specific behavior in `.vscode/settings.json`, not a screenshot of somebody
else's entire user profile:

```json
{
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "strict",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "workbench.colorTheme": "Catppuccin Latte",
  "workbench.iconTheme": "catppuccin-latte",
  "indentRainbow.indicatorStyle": "light",
  "indentRainbow.lightIndicatorStyleLineWidth": 1
}
```

The repository still owns the truth: `pyproject.toml`, `uv.lock`, tests, and CI. An
extension should surface those contracts, not replace them.

## Honorable alternatives

- [Black](https://black.readthedocs.io/) plus isort/Flake8 is a mature Python path when
  a team already owns that configuration.
- [Prettier](https://prettier.io/docs/install.html) plus
  [ESLint](https://eslint.org/docs/latest/use/getting-started) remains a strong web stack,
  especially when a project depends on ecosystem-specific lint plugins.
- [Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)
  remains valuable for teams that need environment management across Python and
  non-Python packages.

I researched and tuned this setup over a long stretch because new data scientists are
often left to discover environments, formatters, type checks, and the Problems panel by
accident. We are really out here fending for ourselves. This page exists so the next
person can start with the useful part and change whatever does not fit.
