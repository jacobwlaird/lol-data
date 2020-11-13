import React, {useState} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import "bootstrap/dist/css/bootstrap.min.css"
import Button from '@material-ui/core/Button';
import FormGroup from '@material-ui/core/FormGroup';
import Selector from './Selector';
import FormCheckbox from './FormCheckbox';

const useStyles = makeStyles((theme) => ({
	  root: {
		      '& > *': {
				    margin: theme.spacing(2)
				  },
		    },
	checkbox: { display: "flex" ,
		    textAlign: "center"}
}));
/* Holds all the filters for our player data. */
const GamesFilter = (props) => {
	//Declare dates options and role options, os we can pass them to the component
	const classes = useStyles();
        const [dateValue, setDateVal] = useState("");
        const [roleValue, setRoleVal] = useState("");
	const [incNone, setIncNone] = useState(true);

	let dateValues = ["This week", "This Patch", "Last 20 Games"];
	let roleValues = ["Top", "Jungle", "Mid", "Support", "Bot"];

	//Do I need a state var for each filter thing?

	//I will clear all filters and reset the data.
	function clear()
	{
		setDateVal("");
		setRoleVal("");
		setIncNone(false);
	}
	function submit()
	{
		alert("Not yet implemented :)");
		//I guess we send a request to a new API, and return.. something.
		//It will be a list of json objects that contains all the info for our cards?
		//So, I have to make a new endpoint that accepts several params, and then 
		// how do we send that data to another component?

	}
	const updateDate = (event) => {
		setDateVal(event.target.value);
	}

	const updateRole = (event) => {
		setRoleVal(event.target.value);
	}

	const updateIncNone = (event) => {
		setIncNone(event.target.checked);
	}


	//2 dropdowns, a checkbox, a button
    return (
	    <div>
	    	<FormGroup row="true">
	    	    <Selector value={dateValue} updateData={updateDate} label="Date" values={dateValues}/>
	    	    <Selector value={roleValue} updateData={updateRole} label="Role" values={roleValues}/>
	    	    <FormCheckbox value={incNone} updateData={updateIncNone} className={classes.checkbox} label="Include 'None'"/>
	    	    <div className={classes.root}>
			    <Button variant="contained" type="reset" color="secondary" onClick={clear}>Clear</Button>
			    <Button variant="contained" color="secondary" onClick={submit}>Filter</Button>
	    	    </div>
	    	</FormGroup>
	    </div>
    );
}

export default GamesFilter;
