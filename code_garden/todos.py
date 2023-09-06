import datetime
import sqlite3
import subprocess
from pathlib import Path

import click

db = sqlite3.connect("todos.db")
cursor = db.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS tasks (title TEXT, description TEXT, tag TEXT, date_added DATETIME, status TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT)"
)


class Task:
    status_options = {"open": "cyan", "active": "yellow", "completed": "blue"}

    def __init__(
        self,
        title: str,
        description: str,
        tag: str,
        date_added: datetime.datetime,
        status: str,
        id: int = None,
    ):
        self.title = title
        self.description = description
        self.tag = tag
        self.date_added = date_added
        self.status = status
        self.id = id

    def add(self):
        cursor.execute(
            "INSERT INTO tasks (title, description, tag, date_added, status) VALUES (?,?,?,?,?)",
            (self.title, self.description, self.tag, self.date_added, self.status),
        )
        db.commit()

    @classmethod
    def get(cls, id):
        cursor.execute(
            "SELECT title, description, tag, date_added, status, id FROM tasks WHERE id=?",
            (str(id),),
        )
        result = cursor.fetchone()
        return Task(result[0], result[1], result[2], result[3], result[4], result[5])

    @classmethod
    def see_list(cls):
        cursor.execute(
            "SELECT title, description, tag, date_added, status, id FROM tasks"
        )
        results = cursor.fetchall()
        return sorted(
            [Task(i[0], i[1], i[2], i[3], i[4], i[5]) for i in results],
            key=lambda x: (x.status == "completed", x.status != "active", x.id),
        )

    def edit(self):
        cursor.execute(
            "UPDATE tasks SET title=?, description=?, tag=?, status=? WHERE id=?",
            (self.title, self.description, self.tag, self.status, str(self.id)),
        )
        db.commit()

    def delete(self):
        cursor.execute("DELETE FROM tasks WHERE id=?", (str(self.id),))
        db.commit()

    def __str__(self):
        return "#{} {:40.40} ({})".format(
            str(self.id).ljust(2),
            self.title,
            self.tag or datetime.date.today().strftime("%d/%m/%Y"),
        )


@click.group()
def todos_cli():
    pass


@todos_cli.command()
@click.argument("title")
@click.option("--desc", "-d", help="More detailed description of task.")
@click.option("--tag", "-t", help="One-word descriptor of task for sorting.")
@click.option("--fixup", "-f", is_flag=True, help="Capitalize input (convenience).")
def add_todo(title: str, desc, tag, fixup):
    """Add a task."""
    task_ = Task(
        title.capitalize() if fixup else title,
        desc,
        tag,
        datetime.datetime.now(),
        "open",
    )
    task_.add()
    click.secho(f"{task_.title} added.", fg="green")


@todos_cli.command()
@click.option(
    "-a", "--all", is_flag=True, default=False, help="Include completed tasks."
)
def view_todos(all):
    """See list of all undone tasks."""
    _ = (
        Task.see_list()
        if all
        else [i for i in Task.see_list() if i.status != "completed"]
    )
    for i in _:
        click.secho(str(i), fg=Task.status_options.get(i.status))


@todos_cli.command()
@click.argument("id")
def view_todo(id):
    """Get a task and see detailed info."""
    task_ = Task.get(int(id))
    display = "\n\n".join(
        [
            task_.title,
            task_.status,
            task_.tag or "(No Tag)",
            task_.description or "(No Description)",
            task_.date_added,
        ]
    )
    click.secho(display, fg=Task.status_options.get(task_.status))


@todos_cli.command()
@click.argument("id")
@click.option("--name", "-n", help="Name of task.")
@click.option("--desc", "-d", help="More detailed description of task.")
@click.option("--tag", "-t", help="One-word descriptor of task for sorting.")
@click.option(
    "--status",
    "-s",
    type=click.Choice(["open", "active", "completed"], case_sensitive=False),
    help="Status of task.",
)
def edit_todo(name, desc, tag, status, id):
    """Edit a task."""
    task_ = Task.get(int(id))
    task_.title = name or task_.title
    task_.description = desc or task_.description
    task_.tag = tag or task_.tag
    task_.status = status or task_.status

    task_.edit()
    click.secho(f"{task_.title} edited.", fg="green")


@todos_cli.command()
@click.argument("id")
def delete_todo(id):
    """Delete a task."""
    task_ = Task.get(int(id))
    if click.confirm(f"Delete {task_.title}?", default=True):
        task_.delete()
        click.secho(f"{task_.title} deleted.", fg="green")
    else:
        click.secho("Nevermind.", fg="red")


@todos_cli.command()
@click.argument("id")
def todo_done(id):
    """Mark a task as complete."""
    task_ = Task.get(int(id))
    task_.status = "completed"
    task_.edit()

    click.secho(f"{task_.title} completed.", fg="blue")


@todos_cli.command()
@click.argument("id")
def commit_todo(id):
    """Commit changes to git using task info as the commit message."""
    task_ = Task.get(int(id))

    if click.confirm(f"Commit {task_.title}?", default=True):
        task_.status = "completed"
        task_.edit()

        click.secho(
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-am",
                    f"({task_.tag or datetime.date.today().strftime('%d/%m/%Y')}) {task_.title}",
                ],
                cwd=Path.cwd(),
                text=True,
                capture_output=True,
            ).stdout,
            fg="blue",
        )
    else:
        click.secho("Nevermind.", fg="red")


@todos_cli.command()
@click.argument("id")
def pick_todo(id):
    """Mark a task as 'active' (currently being worked on)."""
    task_ = Task.get(int(id))
    task_.status = "active"
    task_.edit()

    click.secho(f"{task_.title} active.", fg="yellow")