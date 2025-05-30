
import React from 'react';
import { Link } from 'react-router-dom';

const ErrorPage = () => (
  <div className="finger d-flex flex-column justify-content-center align-items-center vh-100 bg-light">
    <h1 className="display-1 text-danger mb-3">404</h1>
    <h2 className="mb-3">Page Not Found</h2>
    <p className="mb-4 text-muted fs-5">
      The page you are looking for does not exist.
    </p>
    <Link to="/dashboard" className="btn btn-primary btn-lg">
      Go to Dashboard
    </Link>
  </div>
);

export default ErrorPage;
