$(document).ready(function() {
    localStorage.getItem('CodeGarden') === 'dark' ? setDark() : setLight();
    getRepo(localStorage.getItem('lastRepoOpened'));
});

function setDark() {
    localStorage.setItem('CodeGarden', 'dark');
    document.documentElement.setAttribute('data-theme', localStorage.getItem('CodeGarden'));
    $('#dark').show();
    $('#light').hide();
}

function setLight() {
    localStorage.setItem('CodeGarden', 'light');
    document.documentElement.setAttribute('data-theme', localStorage.getItem('CodeGarden'));
    $('#light').show();
    $('#dark').hide();
}

function settingsPage() {
    $.get('settings', function(data) {
        $('#index').html(`<a onclick="getRepo('${localStorage.getItem('lastRepoOpened')}');" class="btn btn-sm text-secondary"><i class="bi bi-arrow-left"></i> Back</a>`);
        for (x in data) {
            $('#index').append(`
                <div class="form-floating mb-1">
                    <input id="${x}" name="${x}" autocomplete="off" class="form-control border-0" value="${data[x]}">
                    <label for="${x}">${x}</label>
                </div>
                `);
        }
    });
}

function createRepoPage() {
    $('#index').html(`
        <div>
            <a onclick="getRepo('${localStorage.getItem('lastRepoOpened')}');" class="btn btn-sm text-secondary"><i class="bi bi-arrow-left"></i> Back</a>
            <form onsubmit="event.preventDefault(); createRepository();" class="mt-3">
                <div class="input-group input-group-sm mb-3">
                    <input autocomplete="off" class="form-control" id="name" placeholder="Name" required>
                    <a onclick="generateRepoName()" class="btn btn-outline-primary">Generate Name <i class="bi bi-shuffle"></i></a>
                </div>
                <textarea rows=10 autocomplete="off" class="form-control form-control-sm mb-3" id="briefDescrip" placeholder="Description"></textarea>
                <button type="submit" class="btn btn-sm btn-outline-success w-100">Create New Repository</button>
            </form>
        </div>
        `);
}

const repo = (repo_) => `
<div class="row">
    <div class="col-3">
        <div class="col-12">
            <div class="btn-group btn-group-sm w-100 mb-2">
                <a id="changes" class="btn btn-outline-secondary" onclick="getDiff('${repo_}')">Changes</a>
                <a id="history" onclick="getLog('${repo_}')" class="btn btn-outline-secondary">History</a>
            </div>
            <div id="sideStage"></div>
        </div>
        <div class="col-12 mt-3">
            <div id="commit"></div>
            <form onsubmit="event.preventDefault(); commit('${repo_}');">
                <input id="msg" autocomplete="off" class="form-control form-control-sm mb-2" placeholder="Commit Message" required>
                <button class="btn btn-sm btn-outline-primary w-100">Commit</button>
            </form>
        </div>
        <div class="col-12 mt-3">
            <div id="todos"></div>
        </div>
    </div>
    <div class="col-9" id="stage"></div>
</div>
<div class="pt-5">
    <a onclick="copyPath()" class="btn btn-sm text-secondary"><i class="bi bi-clipboard" id="clipboard"></i> Copy Path</a>
    <a class="btn btn-sm text-danger"><i class="bi bi-trash2"></i> Delete</a>
</div>
`;

const diffItem = (item) => `
<a onclick="getFile('${item.path}')" class="hover">
    <span>${item.name}</span>
    <span class="float-end" style="color: ${item.color}"><i class="bi bi-circle"></i></span>
</a><br>
`;

const logItem = (item) => `
<div class="mb-2 hover">
    <a>
        <div class="fw-bold">${item.msg}</div>
        <div class="fw-light small text-muted">${item.timestamp}</div>
    </a>
</div>
`;

const todoItem = (item, repo_, id) => `
<div class="hover input-group input-group-sm mb-1 ${item.done ? 'opacity-25' : ''}">
    <a onclick="toggleTodo('${repo_}', '${id}')" class="text-${item.done ? 'success' : 'secondary'}"><i class="bi bi-check-lg"></i></a>
    <input onchange="editTodo('${repo_}', '${id}')" id="description${id}" autocomplete="off" class="form-control border-0" value="${item.description}">
    <a onclick="deleteTodo('${repo_}', '${id}')" class="text-danger"><i class="bi bi-x-lg"></i></a>
</div>
`;

const addTodoForm = (repo_) => `
<form onsubmit="event.preventDefault(); addTodo('${repo_}');" class="input-group input-group-sm mt-4 mb-2">
    <input id="description" autocomplete="off" class="form-control border-success" placeholder="New Todo">
</form>
`;

function getDiff(name) {
    $('#changes').addClass('active');
    $('#history').removeClass('active');
    $('#sideStage').html('');
    $.get('get_diffs', {
        name: name
    }, function (data) {
        $('#sideStage').html(`<div class="small text-center">${data.diffs.length} changed files</div>`);
        for (x of data.diffs) {
            $('#sideStage').append(diffItem(x));
        }
    });
}

function getLog(name) {
    $('#changes').removeClass('active');
    $('#history').addClass('active');
    $('#sideStage').html('');
    $.get('get_log', {
        name: name
    }, function (data) {
        for (x of data.log) {
            $('#sideStage').append(logItem(x));
        }
    });
}

function getReadme(name) {
    $.get('get_readme', {
        name: name
    }, function (data) {
        $('#stage').html(data);
    });
}

function getTodos(name) {
    $.get('get_todos', {
        name: name
    }, function (data) {
        $('#todos').html(addTodoForm(name));
        for (let [id, x] of data.todos.entries()) {
            $('#todos').append(todoItem(x, name, id));
        }
    });
}

function getBranches(name) {
    $.get('get_branches', {
        name: name
    }, function (data) {
        for (x of data.branches) {
            if (!x.startsWith('* ')) {
                $('#branches').append(`<a onclick="checkout('${name}', '${x}')" class="dropdown-item">${x}</a>`);
            }
        }
    });
}

function getFile(path) {
    $.get('get_file', {
        path: path
    }, function (data) {
        $('#stage').html(`
            <a class="btn btn-sm text-secondary mb-3" onclick="getReadme('${localStorage.getItem('lastRepoOpened')}')"><i class="bi bi-arrow-left"></i> Back</a>
            <div class="font-monospace" style="white-space:pre-wrap; font-size: 0.9em" id="file"></div>
            `);
        $('#file').text(data);
    });
}

function getRepo(name) {
    $.get('get_repository', {
        name: name
    }, function (data) {
        localStorage.setItem('lastRepoOpened', name);
        $('#current').html(`
            <div class="small text-muted">Current Repository</div>
            ${name}
            `);
        $('#index').html(repo(name));
        $('#branchSelect').remove();
        $('#push').remove();
        $('#copy').remove();
        $('#nav').append(`
            <li class="nav-item dropdown" id="branchSelect">
                <a data-bs-toggle="dropdown" data-bs-target="#branches" class="nav-link dropdown-toggle">
                    <div class="small text-muted">Current Branch</div>
                    ${data.current_branch}
                </a>
                <div class="dropdown-menu" id="branches">
                </div>
            </li>
            <li class="nav-item" id="push">
                <a class="nav-link" onclick="push('${name}')">
                    <div class="text-muted">Remote: origin</div>
                    Push <i class="bi bi-arrow-up-short"></i>
                </a>
            </li>
            <input id="copy" value="${data.path}" style="display:none">
            `);
        getBranches(name);
        getDiff(name);
        getReadme(name);
        getTodos(name);
    });
}

function createRepository() {
    $.post('create_repository', {
        name: $('#name').val(),
        brief_descrip: $('#briefDescrip').val()
    }, function(data) {
        getRepo($('#name').val());
    });
}

function addTodo(name) {
    $.post('create_todo', {
        name: name,
        description: $('#description').val()
    }, function(data) {
        getTodos(name);
    });
}

function editTodo(name, id) {
    $.post('edit_todo', {
        name: name,
        id: id,
        description: $('#description' + id).val()
    }, function(data) {
        getTodos(name);
    });
}

function deleteTodo(name, id) {
    $.get('delete_todo', {
        name: name,
        id: id,
    }, function(data) {
        getTodos(name);
    });
}

function toggleTodo(name, id) {
    $.get('toggle_todo', {
        name: name,
        id: id,
    }, function(data) {
        getTodos(name);
    });
}

function commit(name) {
    $('#spinner').show();
    $.post('commit', {
        name: name,
        msg: $('#msg').val()
    }, function(data) {
        $('#spinner').hide();
        alert(data);
        getRepo(name);
    });
}

function checkout(name, branch) {
    $.get('checkout', {
        name: name,
        branch: branch
    }, function(data) {
        getRepo(name);
    });
}

function push(name) {
    $('#spinner').show();
    $.get('push', {
        name: name
    }, function(data) {
        $('#spinner').hide();
        alert(data);
        getRepo(name);
    });
}

function generateRepoName() {
    $.get('generate_repo_name', function(data) {
        $('#name').val(data);
    });
}

function copyPath() {
    copyThis = document.getElementById('copy');
    copyThis.style.display = 'block';
    copyThis.select();
    document.execCommand('copy');
    copyThis.style.display = 'none';
    $('#clipboard').toggleClass(['bi-clipboard', 'bi-clipboard-check', 'text-success']);
    setTimeout(function() { $('#clipboard').toggleClass(['bi-clipboard', 'bi-clipboard-check', 'text-success']); }, 1500);
}
