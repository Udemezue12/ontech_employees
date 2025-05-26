import * as React from 'react';
import Button from '@mui/material/Button';
// import Stack from '@mui/material/Stack';

export default function ButtonFields(props) {
    const {label, type, onClick}= props
  return (
      <Button variant="contained" type={type} onClick={onClick}>{label}</Button>
     
  );
}
