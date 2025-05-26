import React from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import { Controller } from "react-hook-form";

export default function TextFields(props) {
  const { label, name, control } = props;

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { onChange, value }, fieldState: { error } }) => (
        <TextField
          id="standard-basic"
          label={label}
          variant="standard"
          onChange={onChange}
          value={value}
          error={!!error}
          helperText={error?.message}
        />
      )}
    />
  );
}
