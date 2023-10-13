import datetime
import json
import shutil
import subprocess

import markdown
import requests

from code_garden.readme import Readme
from code_garden.todos import Todo

from . import config


class Repository(object):
    """A Git repository object.

    All Repositories should have (1) a README.md file, and (2) a .git folder.

    Attributes:
        path: Full path of the Repository.
        branches: All local branches of the Repository.
        current_branch: The currently checked-out branch.
        log: List of (5 default) commits, sorted by most recent.
        todos: List of tasks found in the database file.
        diffs: List of all changed file in the current Repository.
        readme: Dict object of text in the README.md file 'txt' is the plaintext content, 'md' is the Markdown-formatted text.
        ignored: List of items in the .gitignore file.

    """

    def __init__(self, name: str):
        self.name = name

    @property
    def path(self):
        return config.HOME_DIR / self.name

    def run_command(self, cmd: list):
        """Run command in the Repository's directory.

        Args:
            cmd (list): List of arguments in the command. (splitting whitespace on text is recommended)
        """
        return subprocess.run(cmd, cwd=self.path, text=True, capture_output=True).stdout

    @property
    def branches(self):
        return [
            Branch(self.name, i.strip())
            for i in self.run_command(["git", "branch"]).split("\n")
            if i.strip()
        ]

    @property
    def current_branch(self):
        for i in self.run_command(["git", "branch"]).split("\n"):
            if i.startswith("* "):
                return Branch(self.name, i.replace("* ", ""))

    @property
    def log(self):
        _ = []
        try:
            for i in self.run_command(
                ["git", "log", "--oneline", "-5", "--pretty=format:%s\t%at\t%h"]
            ).split("\n"):
                if len(i.strip().split("\t")) == 2:
                    _.append(
                        LogItem(
                            self.name,
                            "[No Commit Message]",
                            datetime.datetime.min,
                            i.strip().split("\t")[0],
                        )
                    )
                else:
                    _.append(
                        LogItem(
                            self.name,
                            i.strip().split("\t")[0],
                            datetime.datetime.fromtimestamp(int(i.split("\t")[1])),
                            i.strip().split("\t")[2],
                        )
                    )

            return _
        except:
            return []

    @property
    def todos(self):
        return Todo.see_list(self.name)

    @property
    def diffs(self):
        return [
            DiffItem(
                self.name, (self.path / i.strip().split()[1]).name, i.strip().split()[0]
            )
            for i in self.run_command(["git", "status", "--short"]).split("\n")
            if i.strip()
        ]

    @property
    def readme(self):
        try:
            raw = open(self.path / "README.md").read()
            return dict(txt=raw, md=markdown.markdown(raw))
        except:
            return {}

    @property
    def ignored(self):
        try:
            return [
                IgnoreItem(self.name, i.strip())
                for i in open(self.path / ".gitignore").readlines()
                if i.strip()
            ]
        except:
            return []

    @property
    def remote_url(self):
        return (
            self.run_command(["git", "remote", "-v"]).split("\n")[0].split()[1]
            if self.run_command(["git", "remote", "-v"])
            else None
        )

    @classmethod
    def all(cls):
        """Get all Repositories in the home directory."""
        return [
            Repository(i.name)
            for i in config.HOME_DIR.iterdir()
            if i.is_dir() and (i / ".git").exists()
        ]

    @classmethod
    def generate_name(cls):
        adj = requests.get(
            "https://random-word-form.herokuapp.com/random/adjective"
        ).json()[0]
        noun = requests.get(
            "https://random-word-form.herokuapp.com/random/noun"
        ).json()[0]
        return f"{adj}-{noun}"

    def init(self, brief_descrip: str):
        """Create a new Repository.

        Args:
            brief_descrip (str): Short description of what the Repository contains.
        """
        files = ["LICENSE.md", ".gitignore"]
        self.path.mkdir()
        Readme(self.name, brief_descrip).write(self.path)
        for i in files:
            (self.path / i).touch()

        self.run_command(["git", "init"])
        self.commit("Initial commit")

    @classmethod
    def clone(cls, url: str):
        """Clone a Repository.

        Args:
            url (str): URL of the Git Repository.
        """
        subprocess.run(["git", "clone", url], cwd=config.HOME_DIR)

    def delete(self):
        """Delete this Repository."""
        shutil.rmtree(self.path)

    def edit_readme(self, content: str):
        """Edit this Repository's README file.

        Args:
            content (str): New plaintext content of the README.
        """
        open((self.path / "README.md"), "w").write(content)

    def commit(self, msg: str):
        """Commit all local changes to git.

        Args:
            msg (str): Commit message.
        """
        self.run_command(["git", "add", "-A"])
        self.run_command(["git", "commit", "-am", msg])

    def reset_all(self):
        """Discard all local changes, reset Repository to most recent commit."""
        self.run_command(["git", "checkout", "."])
        self.run_command(["git", "clean", "-fd"])

    def push(self):
        """Push to remote branch."""
        self.run_command(["git", "push", "origin"])

    def export(self):
        """Export all Repository info, such as todos, to single JSON file."""
        with open(config.HOME_DIR / f"{self.name}.json", "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_dict(self):
        """Get a dict representation of the Repository object (for API usage)."""
        return dict(
            name=self.name,
            path=str(self.path),
            branches=[i.to_dict() for i in self.branches],
            current_branch=self.current_branch.to_dict(),
            remote_url=self.remote_url,
            log=[i.to_dict() for i in self.log],
            todos=[i.to_dict() for i in self.todos],
            diffs=[i.to_dict() for i in self.diffs],
            readme=self.readme,
            ignored=[i.to_dict() for i in self.ignored],
        )

    def __str__(self):
        return f"{self.name.ljust(20)} (current branch: {self.current_branch.name} (+{self.current_branch.compare_with_master}), last updated: {self.log[0].timestamp.strftime('%B %-d, %Y @ %-I:%M %p')})"


class Branch(object):
    """Branch object.

    Attributes:
        repository (str): name of the containing Repository
        name (str): name of this branch.
    """

    def __init__(self, repository, name):
        self.repository = repository
        self.name = name

    def create(self):
        """Create a new branch."""
        Repository(self.repository).run_command(["git", "checkout", "-b", self.name])

    def delete(self):
        """Delete this branch."""
        Repository(self.repository).run_command(["git", "branch", "-D", self.name])

    def checkout(self):
        """Checkout this branch."""
        Repository(self.repository).run_command(["git", "checkout", self.name])

    @property
    def compare_with_master(self):
        """Compare this branch to master."""
        comparison = Repository(self.repository).run_command(
            [
                "git",
                "log",
                f"{'master' if self.name != 'master' else 'origin/master'}...{self.name}",
                "--oneline",
            ]
        )
        return len([i.strip() for i in comparison.split("\n") if i])

    def merge(self, other_branch):
        """Merge this branch with another.

        Args:
            other_branch (str): Other branch to merge with.
        """
        Repository(self.repository).run_command(["git", "merge", other_branch])

    def to_dict(self):
        """Get a dict representation of this object (for API use)."""
        return dict(
            repository=self.repository,
            name=self.name,
            compare_with_master=self.compare_with_master,
        )


class LogItem(object):
    """Commit item from log.

    Attributes:
        repository (str): name of the containing Repository
        name (str): subject line of this commit.
    """

    def __init__(self, repository, name, timestamp, abbrev_hash):
        self.repository = repository
        self.name = name
        self.timestamp = timestamp
        self.abbrev_hash = abbrev_hash

    def to_dict(self):
        """Get a dict representation of this object (for API use)."""
        return dict(
            repository=self.repository,
            name=self.name,
            timestamp=self.timestamp.strftime("%B %-d, %Y @ %-I:%M %p"),
            abbrev_hash=self.abbrev_hash,
        )


class DiffItem(object):
    """Changed item in the Repository.

    Attributes:
        repository (str): name of the containing Repository
        name (str): name of this file.
    """

    def __init__(self, repository, name, type_):
        self.repository = repository
        self.name = name
        self.type_ = type_

    @property
    def path(self):
        return Repository(self.repository).path / self.name

    @property
    def color(self):
        choices = {"M": "orange", "A": "green", "D": "red", "R": "yellow", "?": "green"}
        return choices.get(self.type_)

    def reset(self):
        """Reset this file to its original state in the most recent commit."""
        Repository(self.repository).run_command(
            ["git", "checkout", "HEAD", "--", str(self.path)]
        )

    def to_dict(self):
        """Get a dict representation of this object (for API use)."""
        return dict(
            repository=self.repository,
            name=self.name,
            path=str(self.path),
            type_=str(self.type_),
            color=self.color,
        )


class IgnoreItem(object):
    """Ignored items found in the .gitignore file.

    Attributes:
        repository (str): name of the containing Repository
        name (str): name of this file.
    """

    def __init__(self, repository, name):
        self.repository = repository
        self.name = name

    def create(self):
        """Add this item to the .gitignore."""
        ignores_ = Repository(self.repository).ignored
        ignores_.append(self)

        with open((Repository(self.repository).path / ".gitignore"), "w") as f:
            for i in ignores_:
                f.write(f"{i.name}\n")

    @classmethod
    def delete(cls, repository, id):
        """Delete an Ignore item.

        Args:
            repository (str): name of the Repository that contains this Ignore item.
            id (int): index, or location, of the Ignore item in the list.
        """
        ignores_ = Repository(repository).ignored
        del ignores_[id]

        with open((Repository(repository).path / ".gitignore"), "w") as f:
            for i in ignores_:
                f.write(f"{i.name}\n")

    def to_dict(self):
        """Get a dict representation of this object (for API use)."""
        return dict(repository=self.repository, name=self.name)
