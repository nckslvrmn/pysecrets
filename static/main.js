function postSecret() {
  event.preventDefault();
  var results = document.getElementById("results");
  results.classList.remove('active');
  var file = document.getElementById("file");
  if (file != null) {
    var fileSize = file.files[0].size / 1024 / 1024;
    if (fileSize > 4) {
      setResp(results, 'alert', 'File exceeds 4mb, cannot upload');
      file.value = '';
      return;
    }
    var url = new URL(`${window.location.origin}/encrypt`);
    var params = {
      file_name: file.files[0].name
    };
    url.search = new URLSearchParams(params).toString();
    encrypt(url, file.files[0])
  } else {
    var form = new FormData(document.getElementById("form"));
    var secret = form.get("secret");
    var view_count = form.get("view_count");
    encrypt(`${window.location.origin}/encrypt`, JSON.stringify({
      secret: secret,
      view_count: view_count
    }))
  }
}

function encrypt(url, body) {
  results.classList.remove('active');
  fetch(url, {
    method: 'post',
    body: body
  }).then(function(resp) {
    if (resp.ok) {
      return resp.json();
    } else {
      setResp(results, 'alert', 'There was an error storing secret');
    }
  }).then(function(data) {
    var secret_link = `${window.location.origin}/secret/${data.secret_id}`;
    setResp(results, 'success', `<br /><a href="${secret_link}" target="_blank">${secret_link}</a><br />passphrase: ${data.passphrase}`);
  }).catch((error) => {
    setResp(results, 'alert', 'There was an error storing secret');
  });
}

function getSecret() {
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
  }).then(resp => {
    status_code = resp.status;
    return resp.json();
  }).then(function(data) {
    if (data.file_name != null) {
      forceFileDownload(data);
    } else {
      setResp(results, 'success', data.data, true);
    }
  }).catch((error) => {
    if (status_code === 404) {
      setResp(results, 'warning', 'Secret has either already been viewed<br />or your passphrase is incorrect.');
    } else {
      setResp(results, 'alert', 'There was an error retrieving secret');
    }
  });
}

function setResp(results, level, content, literal = false) {
  if (level == 'alert') {
    var resp_html = `<br /><div id="response" class="alert alert-danger" role="alert"></div>`;
  } else if (level == 'warning') {
    var resp_html = `<br /><div id="response" class="alert alert-warning" role="alert"></div>`;
  } else {
    var resp_html = '<br /><pre id="response" class="mw-50"></pre>';
  }
  results.innerHTML = resp_html;
  var response = document.getElementById("response");
  if (literal) {
    response.appendChild(document.createTextNode(content));
  } else {
    response.innerHTML = content;
  }
  results.classList.add('active');
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
