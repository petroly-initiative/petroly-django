# Petroly Backend

This is Petroly backend for our website [Visit us](https://petroly.co)
<!-- TODO: ADD TOOL ICONS -->
<p align="left">
    <a href="https://www.w3schools.com/css/" target="_blank" rel="noreferrer">
        <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="css3" width="40" height="40" />
    </a>
    <a href="https://www.w3.org/html/" target="_blank" rel="noreferrer">
        <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="html5" width="40" height="40" />
    </a>
    <a href="https://graphql.org" target="_blank" rel="noreferrer">
        <img src="https://www.vectorlogo.zone/logos/graphql/graphql-icon.svg" alt="graphql" width="40" height="40" />
    </a>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank" rel="noreferrer">
        <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="javascript" width="40" height="40" />
    </a>
    <a href="https://www.postgresql.org" target="_blank" rel="noreferrer">
        <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40" />
    </a>
    <a href="https://www.heroku.com" target="_blank" rel="noreferrer">
        <img src="https://brand.heroku.com/static/media/heroku-logo-solid.ab0c1b46.svg" alt="postgresql" width="40" height="40" />
    </a>
    <a href="https://www.djangoproject.com" target="_blank" rel="noreferrer">
        <img src="https://static.djangoproject.com/img/logos/django-logo-negative.png" alt="postgresql" height="40" />
    </a>
</p>

## Project Setup

### Clone Repository

> Do not colne this repo directly.

Steps:

1) Fork this repo.
2) Open a new terminal/powershell window.
3) Move to the directory where you want. For example:
4) Clone the repo that you forked:

   ```shell
   git clone https://github.com/YOUR_NAME/petroly.git
   ```

5) Open a new VS Code window, then drag & drop the cloned folder into VS Code.

### Setup python env

We really prefer to set up your python env:

1) install latest python 3.9
2) create env

   ```shell
   python3 -m venv env
   ```

3) activate env

   ```shell
   source env/bin/activate
   ```

4) install `requirements.txt`

   ```shell
   pip install -r requirements.txt
   ```

   If you face an error in installing `psycopg2-binary`, delete first line temporarily
   from `` file. Then repeat installing.
   > This package is meant for production only. not needed in dev stage.

### Run Django

1) For first time you need to create a SQLite database, by running the command

   ```shell
   python manage.py migrate
   ```

2) Run the server

   ```shell
   python manage.py runserver
   ```

Done, enjoy 🤩.

## The main branch

The main branch is the one that gets deployed into Heroku automaticaly,
once any commit detected.

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
