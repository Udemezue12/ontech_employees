import { useNavigate } from "react-router-dom";
import { useEffect, useRef } from "react";

const AUTO_LOGOUT_TIME = 16 * 60 * 1000;

function useAutoLogout(logoutCallback) {
  const timeoutRef = useRef();
  const navigate = useNavigate();

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const resetTimer = () => {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        logoutCallback();
        window.location.href = "/";
      }, AUTO_LOGOUT_TIME);
    };

    const events = [
      "mousemove",
      "keydown",
      "scroll",
      "click",
      "mousedown",
      "touchstart",
    ];

    const handleActivity = () => resetTimer();

    events.forEach((event) => window.addEventListener(event, handleActivity));
    resetTimer();

    return () => {
      clearTimeout(timeoutRef.current);
      events.forEach((event) =>
        window.removeEventListener(event, handleActivity)
      );
    };
  }, [logoutCallback, navigate]); // 👈 Include navigate here
  // Swal.fire({
  //   icon: "warning",
  //   title: "Session Expired",
  //   text: "Please login again.",
  //   confirmButtonColor: "#3085d6",
  //   confirmButtonText: "OK",
  //   timer: 4000,
  //   timerProgressBar: true,
  // }).then(() => {
  //   navigate("/login", { replace: true });
  // });
}

export default useAutoLogout;
