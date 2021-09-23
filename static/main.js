function postSecret() {
  event.preventDefault();
  var form = new FormData(document.getElementById("form"));
  var results = document.getElementById("results");
  var secret = form.get("secret");
  var view_count = form.get("view_count");
  results.classList.remove('active');
  fetch(`${window.location.origin}/encrypt`, {
      method: 'post',
      body: JSON.stringify({
        secret: secret,
        view_count: view_count
      })
    })
    .then(function(resp) {
      if(resp.ok) {
        return resp.json();
      } else {
        var respHTML = `<br /><div class="alert alert-danger" role="alert">There was an error storing secret</div>`;
        results.innerHTML = respHTML;
        results.classList.add('active');
      }
    })
    .then(function(data) {
      var secret_link = `${window.location.origin}/secret/${data.secret_id}`;
      var respHTML = `<br /><pre id="response" class="mw-50"><a href="${secret_link}" target="_blank">${secret_link}</a><br />passphrase: ${data.passphrase}</pre>`;
      results.innerHTML = respHTML;
      results.classList.add('active');
    })
    .catch((error) => {
      var respHTML = `<br /><div class="alert alert-danger" role="alert">There was an error storing secret</div>`;
      results.innerHTML = respHTML;
      results.classList.add('active');
    });
}

function postFile() {
  event.preventDefault();
  var file = document.getElementById("file");
  var results = document.getElementById("results");
  results.classList.remove('active');
  var fileSize = file.files[0].size / 1024 / 1024;
  if (fileSize > 10) {
    var respHTML = `<br /><div class="alert alert-danger" role="alert">File exceeds 10mb, cannot upload</div>`;
    results.innerHTML = respHTML;
    results.classList.add('active');
    file.value = '';
    return;
  }
  var url = new URL(`${window.location.origin}/encrypt`);
  var params = {
    file_name: file.files[0].name
  };
  url.search = new URLSearchParams(params).toString();
  fetch(url, {
      method: 'post',
      body: file.files[0]
    })
    .then(function(resp) {
      if(resp.ok) {
        return resp.json();
      } else {
        var respHTML = `<br /><div class="alert alert-danger" role="alert">There was an error storing the secret file</div>`;
        results.innerHTML = respHTML;
        results.classList.add('active');
      }
    })
    .then(function(data) {
      var secret_link = `${window.location.origin}/secret/${data.secret_id}`;
      var respHTML = `<br /><pre id="response" class="mw-50"><a href="${secret_link}" target="_blank">${secret_link}</a><br />passphrase: ${data.passphrase}</pre>`;
      results.innerHTML = respHTML;
      results.classList.add('active');
    })
    .catch((error) => {
      var respHTML = `<br /><div class="alert alert-danger" role="alert">There was an error storing the secret file</div>`;
      results.innerHTML = respHTML;
      results.classList.add('active');
    });
}

function getSecret(e) {
  event.preventDefault();
  var form = new FormData(document.getElementById("form"));
  var password = form.get("password");
  var secret_id = window.location.pathname.split('/').slice(-1)[0];
  var results = document.getElementById("results");
  results.classList.remove('active');
  var status_code = 0;
  fetch(`${window.location.origin}/decrypt`, {
      method: "post",
      body: JSON.stringify({
        passphrase: password,
        secret_id: secret_id
      })
    })
    .then(resp => {
      status_code = resp.status;
      return resp.json();
    })
    .then(function(data) {
      if (data.file_name != null) {
        forceFileDownload(data);
      } else {
        var respHTML = `<br /><pre id="response" class="mw-50">${data.data}</pre>`;
        results.innerHTML = respHTML;
        results.classList.add("active");
      }
    })
    .catch((error) => {
      if (status_code === 404) {
        var respHTML = '<br /><div class="alert alert-warning" role="alert">Secret has either already been viewed<br />or your passphrase is incorrect.</div>';
        results.innerHTML = respHTML;
        results.classList.add("active");
      } else {
        var respHTML = '<br /><div class="alert alert-danger" role="alert">There was an error retrieving secret</div>';
        results.innerHTML = respHTML;
        results.classList.add("active");
      }
    });
}

function forceFileDownload(response) {
  const url = window.URL.createObjectURL(b64toBlob(response.data));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', response.file_name);
  document.body.appendChild(link);
  link.click();
}

function b64toBlob(b64Data) {
  sliceSize = 512;
  var byteCharacters = atob(b64Data);
  var byteArrays = [];
  for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    var slice = byteCharacters.slice(offset, offset + sliceSize);
    var byteNumbers = new Array(slice.length);
    for (var i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }
    var byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }
  var blob = new Blob(byteArrays);
  return blob;
}
