import React, { useState, useEffect} from 'react';
import AppBar from '@material-ui/core/AppBar';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import MenuIcon from '@material-ui/icons/Menu';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import { makeStyles } from '@material-ui/core/styles';

const NavBar = ({props, updateState}) => {
	//I may not need updateState anymore.
	const [navBarState, setNavBarState] = useState({
		chipColor: 'green',
		chipDisplay: 'none',
		buttonDisabled: false,
		updateClicked: false
	});

	useEffect(() => {
		document.title = "loldat";

		getScriptStatus();
		setInterval(() => {
			getScriptStatus();

		}, 5000);
	}, []);

        const getScriptStatus = () => {
	    fetch('/api/get_script_status').then(res => res.json()).then(data => {

		if(data[0]['status'] === "Running")
		{
			setNavBarState({chipColor: "yellow", buttonDisabled: true, chipDisplay: "inline"});
		}
		else if (data[0]['status'] === "Success") {
			setNavBarState({chipColor: "green", buttonDisabled: false, chipDisplay: "none"});
			//If its a success and also the script ran int he last 5 seconds, we should 
			// refresh the data. 
			
			var current_time = new Date();
			var end_time = new Date(data[0]['end_time']);
			if (current_time - end_time < 5000)
			{
				updateState()
			}

		}

		});
        }  

	function update()
	{
	        setNavBarState({buttonDisabled: true, updateClicked:true});
		
		fetch('/api/get_script_status').then(res => res.json()).then(data => {
			if (data.hasOwnProperty('status') === false || data[0]['status'] !== "Running" )
			{
				setNavBarState({chipColor: "yellow", buttonDisabled: true, chipDisplay: "inline"});
				fetch('/api/update_data').then(res => res.json()).then(data => {

				});
			}
		});
	}
	const useStyles = makeStyles((theme) => ({
		  root: {
			      flexGrow: 1,
			    },
		  menuButton: {
			      marginRight: theme.spacing(2),
			    },
		  title: {
			      flexGrow: 1,
			    },
	}));

	const classes = useStyles();


	return (<AppBar position="static">
		  <Toolbar variant="dense">
		    <IconButton edge="start" color="inherit" aria-label="menu">
		      <MenuIcon />
		    </IconButton>
		    <Typography variant="h6" className={classes.title} color="inherit">
		    Hell yeah bröther
		    </Typography>
		    <Chip style={{backgroundColor:navBarState.chipColor, display:navBarState.chipDisplay}} label="&nbsp;" />
		    <Button color="inherit" disabled={navBarState.buttonDisabled} onClick={update}>Update</Button>
		  </Toolbar>
		</AppBar>)
}

export default NavBar
