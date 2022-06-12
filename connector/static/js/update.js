const stateP = document.getElementById('update_state');

function downloadUpdate() {
    stateP.innerText = 'Downloading Update';
    fetch('/api/v1/download_update')
        .then(res => {
            if (res.ok) {
                installUpdate();
            } else {
                res.json().then(data => {
                    stateP.innerText = data.data.message
                })
            }
        })
        .catch(error => {
            stateP.innerText = error;
        })
}


function installUpdate() {
    stateP.innerText = 'Installing Update';
    fetch('/api/v1/install_update')
        .then(res => {
            if (res.ok) {
                setTimeout(restart, 2000);
            } else {
                res.json().then(data => {
                    stateP.innerText = data.data.message
                })
            }
        })
        .catch(error => {
            stateP.innerText = error;
        })
}


function restart() {
    stateP.innerText = 'Restarting Connector';
    fetch('/api/v1/restart')
        .then(res => {
            if (res.ok) {
                setTimeout(loadHomepage, 5000)
            } else {
                res.json().then(data => {
                    stateP.innerText = data.data.message
                })
            }
        })
        .catch(error => {
            stateP.innerText = error;
        })
}


function loadHomepage() {
    window.location.replace('/');
}

downloadUpdate();
