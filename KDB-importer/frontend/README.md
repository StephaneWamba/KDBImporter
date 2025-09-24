# arXiv Importer – Frontend

This is the **React frontend** for the [arXiv Importer Platform](https://arxiv.org), a minimal research assistant tool that allows users to:

- Import arXiv papers using IDs, URLs, or search queries
- Attach optional metadata (importance, tag) to each input
- Visualize results and prepare them for further organization or analysis
- Navigate between import tools, dashboards, and assistant views

The frontend is built with **React + Tailwind CSS** and communicates with the backend FastAPI API.

---

## Features

- ✅ **Import interface** with textarea and optional metadata
- ✅ Bulk input support (URLs, IDs, or free-text query)
- ✅ Toast feedback for success/failure
- ✅ Modular API integration with Axios
- ✅ Sidebar navigation with routing
- ✅ Built with Vite, Tailwind CSS, and React Router

---

## Tech Stack

| Layer     | Tool                       |
|-----------|----------------------------|
| Framework | [React](https://react.dev) |
| Styling   | [Tailwind CSS](https://tailwindcss.com) |
| Routing   | [React Router](https://reactrouter.com/) |
| Requests  | [Axios](https://axios-http.com) |
| Dev Env   | [Vite](https://vitejs.dev) |
| UX        | [React Toastify](https://fkhadra.github.io/react-toastify/) |

---

## Project Structure

```

frontend/
├── public/
├── src/
│   ├── api/                ← Axios instance & import API
│   ├── components/         ← UI components: Sidebar, Forms, etc.
│   ├── pages/              ← Routed views (Import, Dashboard, Assistant)
│   ├── App.jsx             ← Main layout and routing
│   ├── main.jsx            ← App entrypoint (with router)
│   └── index.css           ← Tailwind styles
├── package.json
├── tailwind.config.js
└── vite.config.js

````

---

## Setup & Development

### 1. Clone the repo & install dependencies

```bash
cd frontend
npm install
````

### 2. Start the local development server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Connect to backend

By default, the frontend expects the FastAPI backend to be running at:

```
http://localhost:8000/api
```

If you're using Docker or a reverse proxy, adjust the base URL in `src/api/importer.js`.

---

## 🐳 Docker (Optional)

If you want to containerize the frontend:

```Dockerfile
# Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install && npm run build
EXPOSE 4173
CMD ["npm", "run", "preview"]
```

You can then reverse-proxy this via nginx or serve statically.

---

## ✅ Roadmap

* [x] MVP import interface
* [x] Sidebar + routing
* [ ] Dashboard with KPI widgets
* [ ] Paperless Assistant UI
* [ ] Auth layer (optional)
* [ ] PDF preview + export

---

## Contribution

PRs and suggestions are welcome! Please ensure code is clean and uses Tailwind conventions.

---

## License

MIT — feel free to use, fork, or adapt this project.
