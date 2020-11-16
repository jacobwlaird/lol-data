import React, { useState, useEffect} from 'react';
import "./NavBar.css";
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import UserMenuButton from './UserMenuButton';

/* Contains our nav bar and all its related logic. */
const NavBar = ({label, updateState}) => {

	//Holds the state of our navbar and its elements
	const [navBarState, setNavBarState] = useState({
		chipColor: 'green',
		chipDisplay: 'none',
		buttonDisabled: false
	});

	useEffect(() => {
		document.title = "loldat";

		getScriptStatus();
		setInterval(() => {
			getScriptStatus();

		}, 5000);
		//not sure what to do about the lint error here.
		// eslint-disable-next-line
	}, []); 

	/*getScriptStatus makes a call to our script status API, and shows or hides the update chip
	as needed. When the update is finished, we call the passed updateState method. */
        const getScriptStatus = () => {
	    fetch('/api/get_script_status').then(res => res.json()).then(data => {

	    if(data[0]['status'] === "Running")
	    {
		setNavBarState({chipColor: "yellow", buttonDisabled: true, chipDisplay: "inline"});
	    }
	    else if (data[0]['status'] === "Success") {
		setNavBarState({chipColor: "green", buttonDisabled: false, chipDisplay: "none"});
		var current_time = new Date();
		var end_time = new Date(data[0]['end_time']);
		if (current_time - end_time < 5000)
		{
		    updateState()
		}
	    }});
        }  
	/* update runs the update script by sending a request to our update_data api.*/
	function update()
	{
	    setNavBarState({buttonDisabled: true});
		
	    fetch('/api/get_script_status').then(res => res.json()).then(data => {

		//If our script is not currently "Running", then we start it.
	        if (data.hasOwnProperty('status') === false || data[0]['status'] !== "Running" ) {
		   setNavBarState({chipColor: "yellow", buttonDisabled: true, chipDisplay: "inline"});
		   fetch('/api/update_data');
		}});
	}

	return (<AppBar position="static">
		  <Toolbar variant="dense">
		    <UserMenuButton />
		    <a className="nostyle" href="/">
			<Typography variant="h6" style={{flexGrow: 1}} color="inherit">
			    Hell yeah bröther
			</Typography>
		    </a>
		    <div>
		        <Chip style={{backgroundColor:navBarState.chipColor, display:navBarState.chipDisplay}} label="&nbsp;" />
		        <Button color="inherit" disabled={navBarState.buttonDisabled} onClick={update}>Update</Button>
		  </div>
		  </Toolbar>
		</AppBar>)
}

export default NavBar
