import React, { Component } from "react";
import Cookies from "universal-cookie";

const cookies = new Cookies();

export default class CookieApp extends Component {
 constructor(props) {
    super(props);
    this.state = {
      email: "",
      password: "",
      error: "",
      isAuthenticated: false,
    };
  }

  componentDidMount = () => {
    this.getSession();
  };
  getSession = () => {
    fetch("http://localhost:8000/payroll/session", {
      credentials: 'same-origin',
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        if (data.isAuthenticated) {
          this.setState({
            isAuthenticated: true,
            email: data.email,
          });
        } else {
          this.setState({
            isAuthenticated: false,
          });
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };
  whoami = () => {
    fetch("http://localhost:8000/payroll/whoami", {
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        if (data.isAuthenticated) {
          this.setState({
            isAuthenticated: true,
            email: data.email,
          });
        } else {
          this.setState({
            isAuthenticated: false,
          });
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };
  handlePasswordChange = (e) => {
    this.setState({ password: e.target.value });
  };
  handleEmailChange = (e) => {
    this.setState({ email: e.target.value });
  };
  IsResponseOk(response) {
    if (response.status >= 200 && response.status < 299) {
      return response.json();
    } else {
      throw Error(response.statusText);
    }
  }
  login = (e) => {
    e.preventDefault();
    const { email, password } = this.state;
    fetch("http://localhost:8000/payroll/login_view", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": cookies.get("csrftoken"),
      },
      credentials: "same-origin",
      body: JSON.stringify({
        email,
        password,
      }),
    })
      .then(this.IsResponseOk)
      .then((data) => {
        console.log(data);
        this.setState({
          isAuthenticated: true,
          email: "",
          password: "",
          error: "",
        });
      })
      .catch((err) => {
        console.log(err);
        this.setState({
          isAuthenticated: false,
          error: "Invalid email or password",
        });
      });
  };
  logout = () => {
    fetch("/payroll/logout_view", {
      //   headers: {
      //     "Content-Type": "application/json",
      //     "X-CSRFToken": cookies.get("csrftoken"),
      //   },
      credentials: "same-origin",
    })
      .then(this.IsResponseOk)
      .then((data) => {
        console.log(data);
        this.setState({
          isAuthenticated: false,
        });
      })
      .catch((err) => {
        console.log(err);
      });
  };
  render() {
    const { email, password, error, isAuthenticated } = this.state;
    const { login, logout, handlePasswordChange, whoami } = this;
    if (!isAuthenticated) {
      return (
        <div className="container mt-3">
          <h1>React Cookie</h1>
          <br />
          <h2>Login</h2>
          <form onSubmit={login}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                className="form-control"
                id="email"
                value={email}
                onChange={this.handleEmailChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                className="form-control"
                id="password"
                value={password}
                onChange={handlePasswordChange}
                required
              />
            </div>
            <div>{error && <p style={{ color: "red" }}>{error}</p>}</div>
            <button type="submit" className="btn btn-primary">
              Login
            </button>
          </form>
        </div>
      );
    }
    return (
      <div className="container mt-3">
        <h1>React Cookie</h1>
        <br />
        <h2>Welcome {email}</h2>
        <button className="btn btn-danger" onClick={logout}>
          Logout
        </button>
        <button className="btn btn-primary " onClick={whoami}>
          Whoami
        </button>
      </div>
    );
  }
}
