import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { MaterialNavBars } from './materialNavBars';



const navbarContainer = document.getElementById("navbar-root");

if (navbarContainer) {
  const root = ReactDOM.createRoot(navbarContainer);
  root.render(
    <React.StrictMode>
      <BrowserRouter>
        <MaterialNavBars content={<div>Your Navbar Content</div>} />
      </BrowserRouter>
    </React.StrictMode>
  );
}