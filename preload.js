const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  async request(method, path, body) {
    const url = `http://127.0.0.1:5678${path}`;
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body && method !== 'GET') {
      opts.body = JSON.stringify(body);
    }
    const resp = await fetch(url, opts);
    return resp.json();
  },
  get(path) { return this.request('GET', path); },
  post(path, body) { return this.request('POST', path, body); },
  put(path, body) { return this.request('PUT', path, body); },
  delete(path) { return this.request('DELETE', path); },
});
