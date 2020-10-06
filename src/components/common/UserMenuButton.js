import React from 'react';
import Button from '@material-ui/core/Button';
import Link from '@material-ui/core/Link';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import Dashboard from '../player/Dashboard';
import { Filter } from './Filter.js'


export default function UserMenuButton() {
  const [anchorEl, setAnchorEl] = React.useState(null);

  let users = ['Spaynkee', 'Dumat', 'Archemlis']

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div>
      <Button aria-controls="simple-menu" aria-haspopup="true" onClick={handleClick}>
	   <IconButton edge="start" aria-label="menu">
	     <MenuIcon style={{fill: "white"}}/>
	   </IconButton>
      </Button>
      <Menu
        id="simple-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
	  {users.map((user, index) =>
	      <MenuItem key={index} value={user} primaryText={user}><Link href={user}>{user}</Link></MenuItem>
	  )}
      </Menu>
    </div>
  );
}
