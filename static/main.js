function postSecretFile(event) {
  event.preventDefault();
  document.getElementById('results').classList.remove('active');
  
  const file = document.getElementById('file').files[0];
  const formData = new FormData();
  formData.append('file', file);
  
  if ((file.size / 1024 / 1024) > 5) {
    setResp('processing', 'Processing upload');
  }

  _encrypt(formData, {});
}
  
  
function postSecret(event) {
  event.preventDefault();
  document.getElementById('results').classList.remove('active');
  
  const formData = new FormData(document.getElementById("form")).entries();
  
  _encrypt(JSON.stringify(Object.fromEntries(formData)), {'Content-Type': 'application/json'});
}

function _encrypt(data, headers) {
  fetch('/encrypt', {
    method: 'post',
    headers: headers,
    body: data
  })
  .then(
    function(resp) {
      if (resp.ok) {
        return resp.json();
      } else {
        setResp('alert', 'There was an error storing secret');
      }
    }
  )
  .then(
    function(data) {
      const secret_link = `${window.location.origin}/secret/${data.secret_id}`;
      setResp('success', `<br /><a href="${secret_link}" target="_blank">${secret_link}</a><br />passphrase: ${data.passphrase}`);
    }
  )
  .catch(() => {
    setResp('alert', 'There was an error storing secret');
  });
}

function getSecret(event) {
  event.preventDefault();
  document.getElementById('results').classList.remove('active');

  const formData = new FormData(document.getElementById("form"));
  formData.append('secret_id', window.location.pathname.split('/').slice(-1)[0]);
  
  fetch('/decrypt', {
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(Object.fromEntries(formData.entries()))
  })
  .then(
    function(resp) {
      if (!(resp.ok)) {
        if (resp.status === 404) {
          setResp('warning', 'Secret has either already been viewed<br />or your passphrase is incorrect.');
        } else {
          setResp('alert', 'There was an error retrieving secret');
        }
      } else {
        if (resp.headers.has('Content-Disposition')) {
          return resp.blob().then(
            function(blob) {
              dlBlob(resp.headers.get('Content-Disposition'), blob);
          });
        } else {
          return resp.json().then(
            function(json) {
              setResp('success', json.data);
          });
        }
      }
    }
  );
}

function dlBlob(cdheader, blob) {
  const parts = cdheader.split(';');
  filename = parts[1].split('=')[1];
  var url = window.URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function setResp(level, content) {
  const results = document.getElementById('results');
  results.classList.remove('active');
  
  const response = document.getElementById('response');
  switch(level) {
    case 'alert':
      response.classList.add('alert', 'alert-danger');
      response.setAttribute('role', 'alert');
      response.innerHTML = content;
      break;
    case 'warning':
      response.classList.add('alert', 'alert-warning');
      response.setAttribute('role', 'alert');
      response.innerHTML = content;
      break;
    case 'processing':
      response.classList.add('alert', 'alert-primary');
      response.setAttribute('role', 'alert');
      response.innerHTML = content;
      break;
    default:
      response.classList.remove('alert', 'alert-danger', 'alert-warning', 'alert-primary');
      response.removeAttribute('role');
      let pre_content = `<pre id="response_body" class="mw-50 fs-5">${content}</pre>`;
      response.innerHTML = pre_content;
      break;
  }
  

  results.classList.add('active');
}
