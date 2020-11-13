import React from 'react';
import FormLabel from '@material-ui/core/FormLabel';
import { makeStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import Checkbox from '@material-ui/core/Checkbox';
import "bootstrap/dist/css/bootstrap.min.css"

/* Holds all the filters for our player data. */

	const useStyles = makeStyles((theme) => ({
		  formControl: {
			      margin: theme.spacing(1),
			      minWidth: 120,
			    }
	}));
const FormCheckbox = (props) => {
    const classes = useStyles();

	function update(event){
		props.updateData(event);
	}
    return (
	    <div>
	    <FormControl variant="outlined" className={classes.formControl}>
	            <FormLabel id="demo-simple-select-outlined-label">{props.label}</FormLabel>
	    	    <Checkbox checked={props.value} onChange={update}/>
	    </FormControl>
	    </div>
    );
}

export default FormCheckbox;
