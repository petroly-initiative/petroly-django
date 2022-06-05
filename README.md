# Petroly

 Employing technology to deliver car express services 

 This is Petroly repo where the magic happens!

## 1.0 Table of Content

* [Set up this project](#11-project-setup) to your own device.
* [Maintain the codebase](#12-maintain-the-codebase).
* [Contribute to this project](#13-contribute-to-this-project).

## 1.1 Project Setup

### Clone Repository

To clone this repo:

1) Open a new terminal/powershell window.
2) Move to the directory where you want Garage to be. For example:
   ```bash
   cd C:\Users\yourname\Petroly
   ```
3) Clone the repo:
   ```
   git clone https://github.com/Petroly/Petroly.git
   ```
4) Open VS Code, then from the top menu `File > Open` Folder and navigate to Petroly.

<!-- ### Setup Instructions

Please, refer to these documents for each module setup.
Once you clone this repo you'll have to use each module individually.


## 1.2 Maintain The Codebase

- Before creating a new branch, make sure you are on dev, and run:
```bash
git pull
```
- If you're already on a branch and some new changes have been pushed to dev, run:
```bash
git pull origin dev
```

### Walk Through The Main Branches

Refer to the following main branches to get familiar with the code base.

* *main* contains production code. **Please, do not pull or push any code to this branch**
* *dev* where the action is happening. This branch contains code under development where we build, improve, test, and debug the project apps.

## 1.3 Contribute to This Project

### Repo Issues

If you find a bug throughout your development or testing process, please do not hesitate to file an issue describing the bug you noticed.

### How to File an Issue?

Here is how you create an issue:

* Go to the issues tab.
* Click on "New issue".
* Add an informative title following the naming convention below.
* Add a detailed description with the suggested solution if possible.
* Select applicable labels after reading each label's description.
* Try to label the issue priority to the best of your knowledge -this might change based on the current project milestone-.

### Creating a New Branch

Once you're assigned to an issue or want to start working on a new feature, create a new branch with a descriptive title preceded with your name as `@yourname/new-feature-title`.

_Note: branch names ar all small case separated by a dash `-`, e.g. `@ziyad/booking-bug`_

### Conventions

#### Commits

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

* **fix:** a commit of the type `fix` patches a bug in the codebase.

* **feat:** a commit of the type `feat` introduces a new feature to the codebase.

* **BREAKING CHANGE:** a commit that has a footer `BREAKING CHANGE:`, or appends a `!` after the type/scope, introduces a breaking change.

* types other than fix: and feat: are allowed, for example `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.
 
Refer to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for more information. 


#### python File Naming
* Small letters only.
* Use underscore as delimiters.
* Keep it short, clear and simple.

Examples :
`main_view.python`
`settings_controller.python`


