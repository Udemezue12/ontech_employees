const LoadingDots = () => {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100 bg-dark">
        <h3 className="text-light fw-bold">
          Loading
          <span className="dot-one">.</span>
          <span className="dot-two">.</span>
          <span className="dot-three">.</span>
        </h3>
        <style>
          {`
            .dot-one, .dot-two, .dot-three {
              animation: blink 1.5s infinite;
            }
            .dot-two {
              animation-delay: 0.2s;
            }
            .dot-three {
              animation-delay: 0.4s;
            }
            @keyframes blink {
              0% { opacity: 0; }
              50% { opacity: 1; }
              100% { opacity: 0; }
            }
          `}
        </style>
      </div>
    );
  };
  
  export default LoadingDots;
  