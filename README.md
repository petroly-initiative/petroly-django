# Petroly Backend

This is Petroly backend for our website [Visit us](https://petroly.co)
<!-- TODO: ADD TOOL ICONS -->
## Project Setup

### Clone Repository

> Do not colne this repo directly.

Steps:

1) Fork this repo.
2) Open a new terminal/powershell window.
3) Move to the directory where you want. For example:
4) Clone the repo that you forked:

   ```bash
   git clone https://github.com/YOUR_NAME/petroly.git
   ```

5) Open a new VS Code window, then drag & drop the cloned folder into VS Code.

### The main branch

The main branch is the one that gets deployed into Heroku automaticaly,
once any commit detected.
> **Please, do not pull or push any code to this branch** without an approve.

## Contribute to This Project

### Issues

If you find a bug 🐞 throughout your development or testing process,
please do not hesitate to file an issue describing the bug you noticed.

### How to File an Issue?

Here is how you create an issue:

- Go to the issues tab.
- Click on "New issue".
- Add an informative title following the naming convention below.
- Add a detailed description with the suggested solution if possible.
- Select applicable labels after reading each label's description.
- Try to label the issue priority to the best of your knowledge -this might change based on the current project milestone-.

### Conventions

#### Commits

The commit message should be structured as follows:

```git
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

- **fix:** a commit of the type `fix` patches a bug in the codebase.

- **feat:** a commit of the type `feat` introduces a new feature to the codebase.

- **BREAKING CHANGE:** a commit that has a footer `BREAKING CHANGE:`, or appends a `!` after the type/scope, introduces a breaking change.

- types other than fix: and feat: are allowed, for example `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.

Refer to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for more information.

#### python File Naming

We follow all PEP styles strictly.

- Small letters only.
- Use underscore as delimiters.
- Keep it short, clear and simple.

Examples :
`main_view.python`
`settings_controller.python`
