# code-garden

CodeGarden is an open source Python-based web and command-line app made to simplify your coding and development workflow and manage your Git repositories. Originally developed to be a lightweight GitHub Desktop alternative (with a few more features added.)

CodeGarden can make it easier to perform common Git operations such as cloning, committing, and pushing changes to a repository. It also allows developers to integrate Git functionality into their applications without having to interact with Git directly, which can be helpful for automating tasks and reducing errors.

![](/docs/screenshot1.png)

![](/docs/screenshot2.png)

### Features

- Add your local repositories just by putting them in the home directory.
- View git information about your repo, such as status, history, diff, branches, etc. all on the dashboard.
- Manage **TODOs** (tasks) for your repo. You can also commit your changes to the repo straight from your TODO list
- Minimalist and responsive interface
- Command-line Git wrapper functions that makes Git commands easier

### Installation / Usage

1. Clone this **[repo](https://github.com/misterrager8/CodeGarden).**
2. Run command: `python3 setup.py develop`
3. Set up configuration:
  1. Run command: `garden set-config home_dir [DIRECTORY]`
  2. (Optional) run command: `garden set-config port [PORT]`
  3. Run `--help` command for all options

<pre>
  add-repo       Create a new repo.
  add-todo       Add a task.
  commit         Commit changes to git using task info as the commit...
  commit-todo    Commit changes to git using task info as the commit...
  delete-repo    Delete a repo.
  delete-todo    Delete a task.
  edit-todo      Edit a task.
  generate-name  Generate a random placeholder name for a new repo.
  get-config     View current settings for web and command-line interfaces.
  new-readme     Generate a new README in the current directory.
  pick-todo      Mark a task as 'active' (currently being worked on).
  set-config     Set config for web and command-line interfaces.
  todo-done      Mark a task as complete.
  view-repo      View all attributes of a repo for exporting.
  view-repos     See a list of all repos found in the home directory.
  view-todo      Get a task and see detailed info.
  view-todos     See list of all undone todos.
  web            Launch web interface for CodeGarden.
</pre>

### Contributing

I welcome and appreciate contributions from the open-source community to make this project better. Whether you're a developer, designer, tester, or just someone with a great idea, I encourage you to get involved and help me improve this project.

To contribute to this project, please follow these steps:

1. **Fork the Repository**: Click the "Fork" button on the top right of the repository page. This will create a copy of the project in your GitHub account.

2. **Clone the Repository**: Clone your fork of the repository to your local machine.

   ```bash
   git clone https://github.com/misterrager/CodeGarden.git```


### License

Created by [C.N. Joseph (misterrager8)](https://github.com/misterrager8) under the MIT License.
