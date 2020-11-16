import React, { useState, useEffect } from 'react';
import Button from '@material-ui/core/Button';
import Link from '@material-ui/core/Link';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import MenuIcon from '@material-ui/icons/Menu';

export default function UserMenuButton() {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [leagueUserNames, setLeagueUserNames] = useState(0);

  let users = [];

  useEffect(() => {
      fetch('/api/get_league_users').then(res => res.json()).then(data => {
          setLeagueUserNames(data);
      });
  }, []);

  let leagueNames = Array.from(leagueUserNames);
  leagueNames.forEach(element => users.push(element.summoner_name));

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div>
      <Button aria-controls="simple-menu" aria-haspopup="true" onClick={handleClick}>
	     <MenuIcon style={{fill: "white"}}/>
      </Button>
      <Menu
        id="simple-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
	  {users.map((user, index) =>
	      <MenuItem key={index} value={user}><Link href={user}>{user}</Link></MenuItem>
	  )}
      </Menu>
    </div>
  );
}
