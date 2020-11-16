import React, { useState } from 'react';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import { makeStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import "bootstrap/dist/css/bootstrap.min.css"

/* Holds all the filters for our player data. */

	const useStyles = makeStyles((theme) => ({
		  formControl: {
			      margin: theme.spacing(1),
			      minWidth: 120,
			    },
		  selectEmpty: {
			      marginTop: theme.spacing(2),
			    },
	}));
const Selector = (props) => {
    const classes = useStyles();
	// get the updateFunction
	

	function update(event)
	{
		props.updateData(event);
	}
    return (
	    <div>
	    <FormControl variant="outlined" className={classes.formControl}>
	            <InputLabel id="demo-simple-select-outlined-label">{props.label}</InputLabel>
	            <Select
	              labelId="demo-simple-select-outlined-label"
	              id="demo-simple-select-outlined"
	              value={props.value}
	              onChange={update}
	              label="Passed"
	            >
	              <MenuItem value="">
	                <em>None</em>
	              </MenuItem>
	    {props.values.map( (item,keyIndex) =>
		                     <MenuItem  key={keyIndex} value={item}>{item}</MenuItem>)}
	            </Select>
	          </FormControl>
	    </div>
    );
}

export default Selector;
