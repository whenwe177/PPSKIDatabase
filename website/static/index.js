function editSelected(userID) {
    alert("Editing " + userID)
    fetch("/admin-select-user", {
        method: "POST",
        body: JSON.stringify({ userID: userID })

    }).then((_res) => {
        window.location.href = "/admin-edit-user"
    })
}

function reviewSelected(userID) {
    alert("Reviewing " + userID)
    fetch("/select-user", {
        method: "POST",
        body: JSON.stringify({ userID: userID })
    }).then((_res) => {
        window.location.href = "/review-calon"
    });
}

function tolakCalon(userID) {
  alert("Menolak " + userID)

  fetch("/tolak-calon", {
    method: "POST",
    body: JSON.stringify({ userID: userID })
  }).then((_res) => {
    window.location.href = '/registration-queue'
  });
}

function terimaCalon(userID) {
    alert("Menerima " + userID)

    fetch("/terima-calon", {
    method: "POST",
    body: JSON.stringify({ userID: userID })
    }).then((_res) => {
    alert("Auto Fetch")
    window.location.href = '/registration-queue'
    });
}

