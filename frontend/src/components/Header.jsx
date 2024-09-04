import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';
import styled from 'styled-components';
import { theme } from '../App';

const StyledAppBar = styled(AppBar)`
  background-color: ${theme.palette.secondary.main};
`;

const Header = () => {
  return (
    <StyledAppBar position="static">
      <Toolbar>
        <Typography variant="h6">Cheque Parser Dashboard</Typography>
      </Toolbar>
    </StyledAppBar>
  );
};

export default Header;