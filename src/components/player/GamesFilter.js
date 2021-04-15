import React, {useState, useEffect} from 'react';
import { Container, Row, Col } from 'reactstrap';
import { makeStyles } from '@material-ui/core/styles';
import "bootstrap/dist/css/bootstrap.min.css"
import Button from '@material-ui/core/Button';
import FormGroup from '@material-ui/core/FormGroup';
import Selector from './Selector';
import FormCheckbox from './FormCheckbox';
import ChampCard from './ChampCard';
import './GamesFilter.css';

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
const GamesFilter = ({player}) => {
	const classes = useStyles();
        const [maxGamesValue, setGamesVal] = useState("50");
        const [roleValue, setRoleVal] = useState("All");
	const [incNone, setIncNone] = useState(false);
	const [champData, setChampData] = useState("");

	//determines options for our filters
	let gameValues = ['10', '20', '50', '100', 'All']
	let roleValues = ["All", "Top", "Jungle", "Middle", "Support", "Bottom"];

	    useEffect(() => {
	    fetch('/api/get_champ_card_data?name='+player+"&role="+roleValue).then(res => res.json()).then(data => {

		  setChampData(data);
		});
	    }, []);

	    let dataArray = Array.from(champData);

	function clear()
	{
		setGamesVal("50");
		setRoleVal("All");
		setIncNone(false);
		setChampData("");
		dataArray = [];
	}
	function submit()
	{
		    fetch('/api/get_champ_card_data?name='+player+'&role='+roleValue+'&maxgames='+maxGamesValue+'&incnone='+incNone).then(res => res.json()).then(data => {
			  setChampData(data);
		});

	        let dataArray = Array.from(champData);
	    

	}

	//Rename this at some point when I remember what it does.
	function checkIndex(data){
		return (<div><Col><ChampCard className="card" data={data}/></Col></div>)

	}

	function newRow() {
		return 

	}

	const updateMaxGames = (event) => {
		setGamesVal(event.target.value);
	}

	const updateRole = (event) => {
		setRoleVal(event.target.value);
	}

	const updateIncNone = (event) => {
		setIncNone(event.target.checked);
	}


    return (
	    <div>
	    	<FormGroup row="true">
	    	    <Selector value={maxGamesValue} updateData={updateMaxGames} label="Games" values={gameValues}/>
	    	    <Selector value={roleValue} updateData={updateRole} label="Role" values={roleValues}/>
	    	    <FormCheckbox value={incNone} updateData={updateIncNone} className={classes.checkbox} label="Include 'None' Role"/>
	    	    <div className={classes.root}>
			    <Button variant="contained" type="reset" color="secondary" onClick={clear}>Clear</Button>
			    <Button variant="contained" color="secondary" onClick={submit}>Filter</Button>
	    	    </div>
	    	</FormGroup>
	    	<Container>
	    	    <div>
	    		{dataArray.map((row_array, index) => (
				<Row className="row">
				{row_array.map((data, inner_index) => (
					checkIndex(data)
				))}
				</Row>
			))}
	    	    </div>
	    	</Container>
	    </div>
    );
}

export default GamesFilter;
