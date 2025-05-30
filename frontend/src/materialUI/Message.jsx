import { Box } from "@mui/material";
import React from "react";

const MyMessage = (props) => {
  const { text } = props;
  return (
    <Box
      sx={{
        backgroundColor: "#69c9ab",
        color: "#FFFFFF",
        width: "90%",
        height: "40px",
        position: 'absolute',
        top: '20px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {text}
    </Box>
  );
};

export default MyMessage;
