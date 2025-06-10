# Frontend Documentation

## Overview
The `frontend` folder contains the React-based user interface for Saras – Your Personal AI Assistant for Indian Financial Markets. This application allows users to interact with an AI assistant to query and receive insights about Indian companies' financials and market data.

## Purpose
The frontend provides a modern, responsive chat interface where users can:
- Ask questions about Indian financial markets and companies.
- View AI-generated responses in real time.
- Experience a seamless, user-friendly design tailored for financial data exploration.

## Usage Details
- **Start the frontend**: Typically, run `npm install` followed by `npm start` inside the `frontend` directory to launch the development server.
- **Configuration**: The frontend expects an environment variable `REACT_APP_API_BASE_URL` pointing to the backend API endpoint (e.g., `http://localhost:8000`).
- **Main entry point**: The application starts from `src/App.js`.
- **Styling**: Uses Tailwind CSS for styling, configured via `tailwind.config.js` and `postcss.config.js`.

## Inputs
- **User Input**: Text queries entered by the user in the chat input box.
- **API Endpoint**: The backend API URL provided via the `REACT_APP_API_BASE_URL` environment variable.

## Outputs
- **Chat Messages**: Displays both user queries and AI assistant responses in a chat format.
- **Error Handling**: Shows error messages if the backend is unreachable or returns an error.

## File Structure
- `src/` – Contains React components and main application logic.
- `public/` – Static files and the main HTML template.
- `build/` – Production build output (after running `npm run build`).
- `package.json` – Project dependencies and scripts.

## Example Usage
1. User enters a question about a company's financials.
2. The frontend sends the query to the backend API.
3. The backend responds with an answer, which is rendered in the chat window.

## Local Setup Instructions

To set up and run the frontend on your local machine, follow these steps:

### 1. Prerequisites
- **Node.js**: Download and install the latest LTS version of Node.js from [nodejs.org](https://nodejs.org/). This will also install npm (Node Package Manager).
- **npm**: Comes bundled with Node.js. You can check the installation by running:
  ```sh
  node -v
  npm -v
  ```

### 2. Install Dependencies
Open a terminal, navigate to the `frontend` directory, and run the following commands to install all required packages:

```sh
npm install tailwindcss @tailwindcss/postcss
npm install -D @tailwindcss/cli
npm install @tailwindcss/typography
npm install -D marked
npm install -D dompurify
npm install axios
npm install react@18 react-dom@18
```

This will install all necessary dependencies for styling, markdown rendering, sanitization, HTTP requests, and React itself. All dependencies are also listed in `package.json`.

### 3. Configure Environment Variables
Create a `.env` file in the `frontend` directory and add the following line (replace the URL with your backend address if needed):
```sh
REACT_APP_API_BASE_URL=http://localhost:8000
```

### 4. Start the Development Server
Run:
```sh
npm start
```
This will launch the frontend at [http://localhost:3000](http://localhost:3000) by default.

### 5. Build for Production
To create an optimized production build of the frontend, run:

```sh
npm run build
```

This will generate a `build/` directory containing static files ready to be deployed to any static hosting service or web server. The production build is minified and optimized for best performance.

---
For troubleshooting, refer to the official React and Node.js documentation or check the project README.
