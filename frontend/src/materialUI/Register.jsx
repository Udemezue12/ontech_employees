import React from 'react';
import { Box, Card, CardContent, Typography, Button, Grid } from '@mui/material';
import { Link } from 'react-router-dom';

const roles = [
  {
    title: 'HR Manager Registration',
    description: 'Handles employee records, leave requests, complaints, and HR department activities.',
    link: '/hr_register',
  },
  {
    title: 'Employee Registration',
    description: 'Can request leave, view salary, tax info, attendance, and submit complaints.',
    link: '/employee_register',
  },
  {
    title: 'Manager Registration',
    description: 'Supervises employees and HR. Manages department approvals and performance.',
    link: '/manager_register',
  },
  // {
  //   title: 'Overall Admin Registration',
  //   description: 'Full access to system settings. Oversees HRs, Managers, and employees.',
  //   link: '/admin_register',
  // },
];

const RoleRegistrationCards = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'linear-gradient(to right, #e0f7fa, #fce4ec)',
        background: 'linear-gradient(to right, #e0f7fa, #fce4ec)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 4,
        py: 8,
      }}
    >
      <Grid container spacing={4} justifyContent="center">
        {roles.map((role, index) => (
          <Grid item key={index} xs={12} sm={6} md={3}>
            <Card
              sx={{
                height: '100%',
                p: 2,
                borderRadius: '20px',
                transition: 'all 0.3s ease',
                boxShadow: '0 6px 20px rgba(0,0,0,0.08)',
                border: '2px solid #e3e3e3',
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
                  borderColor: '#90caf9',
                },
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <CardContent>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    mb: 1,
                    color: '#333',
                    textAlign: 'center',
                  }}
                >
                  {role.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: '#666', textAlign: 'center' }}
                >
                  {role.description}
                </Typography>
              </CardContent>
              <Box sx={{ textAlign: 'center', mt: 2, mb: 1 }}>
                <Button
                  variant="contained"
                  color="primary"
                  component={Link}
                  to={role.link}
                  sx={{
                    borderRadius: '20px',
                    px: 4,
                    py: 1,
                    textTransform: 'none',
                    fontWeight: 600,
                  }}
                >
                  Go to Registration
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RoleRegistrationCards;
