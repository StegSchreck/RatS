# Contributing to RatS
Thank you for taking the time to read this document! Your interest in contributing to this project is highly appreciated.

#### Table Of Contents
[Code of Conduct](#code-of-conduct)
[Reporting Bugs](#reporting-bugs)
[Suggesting Enhancements](#suggesting-enhancements)
[Submitting Changes](#submitting-changes)
[Coding Conventions](#coding-conventions)

## Code of Conduct
his project and everyone participating in it is governed by the project's [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Reporting Bugs
Perform a [cursory search](https://github.com/search?l=&q=is%3Aissue+repo%3AStegSchreck%2FRatS&type=Issues) to see if the problem has already been reported. If it has **and the issue is still open**, add a comment to the existing issue instead of opening a new one.

Bugs are tracked as [GitHub issues](https://github.com/StegSchreck/RatS/issues). Create a new issue and provide the requested information to make it easier to work on the subject.

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**. For example, if you moved the cursor to the end of a line, explain if you used the mouse, or a keyboard shortcut, and if so which one?
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Specify which version of RatS you're using.**
* **Specify the name and version of the OS you're using.**

## Suggesting Enhancements
Enhancement suggestions are tracked as [GitHub issues](https://github.com/StegSchreck/RatS/issues). Create an issue on the repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples, as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** to most users.
* **Specify which version of RatS you're using.**
* **Specify the name and version of the OS you're using.**

## Submitting Changes
Please send a [GitHub Pull Request](https://github.com/StegSchreck/RatS/pull/new/master) with a clear list of what you've done (read more about [pull requests](http://help.github.com/pull-requests/)). We can always use more test coverage. Please follow the coding conventions (below) and make sure all of your commits are atomic (one feature per commit).

### Repository Setup
This project uses [uv](https://github.com/astral-sh/uv) as the package manager.
1. Install `uv` - e.g. via `pacman install uv`.
2. Afterwards, you can install the dependencies (including the dev dependencies) with `uv sync --group dev`
3. This project has a pre-commit configuration to ensure some basic file structure and code formatting. Please install it via `uv run pre-commit install`

### Coding Conventions
The project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions.
It is using [ruff](https://github.com/astral-sh/ruff) as its main linter, which is included in the pre-commit configuration of the project.
Simply run `uv run pre-commit run` to check your code changes.

Please make sure that you adapt the existing tests if necessary or write new ones. The unit tests can be executed locally by running `uv run pytest .` or via your IDE.

### Git Commit Messages
Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    >
    > A paragraph describing what changed and its impact."

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Suggesting Code Changes via PRs
After you have submitted your proposed changes by creating a PR on GitHub, I will check it out and test it.
To help me moving this along faster, please provide a catchy title of *what* problem you aim to solve,
as well as a good PR description explaining the *why*. Please don't go into details about the *how* here,
as this is what I can see in the code changes themselves.
But if there is any particular code that needs explanations, please highlight it in the PR description.
It would also be beneficial to explain which alternative solution approaches you considered.

### Releasing a New Version
After a PR is merged, the CI pipeline will take care of releasing a new project version.
For this, we are using [Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/) which is based on
[Semantic Versioning](https://semver.org/) and uses [Conventional Commits](https://www.conventionalcommits.org/)
to figure out the next version to create. The details are configured in the `pyproject.toml` file.
