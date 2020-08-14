import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import AppBar from '@material-ui/core/AppBar';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import MenuIcon from '@material-ui/icons/Menu';
import { makeStyles } from '@material-ui/core/styles';
import MyTable from './components/MyTable';
import { Container } from "reactstrap"
import "bootstrap/dist/css/bootstrap.min.css"

function NavBar(props) {
	return (<AppBar position="static">
		  <Toolbar variant="dense">
		    <IconButton edge="start" color="inherit" aria-label="menu">
		      <MenuIcon />
		    </IconButton>
		    <Typography variant="h6" color="inherit">
		    Hell yeah brøther
		    </Typography>
		  </Toolbar>
		</AppBar>)
}

function App() {

    //For our teams table.
    const [teamData, setTeamData] = useState(0);

    useEffect(() => {
    fetch('/api/get_team_data').then(res => res.json()).then(data => {
          setTeamData(data);
        });
    }, []);

    const data = Array.from(teamData);
    console.dir(data);

    const columns = [
        { Header: "Day Played", accessor: (values) => {
		const day = values.start_time.substring(0, 10);
	    return day
	}},
	//
        { Header: "Game Version", accessor: (values) => {
	    const vers = 0;
	    if (values.game_version != null)
	    {
		const vers = values.game_version.substring(0, 5);
	    }
	    return vers
	}},
        { Header: "Participants", accessor: "participants"},
        { Header: "First Blood", accessor: "first_blood"},
        { Header: "First Dragon", accessor: "first_dragon"},
        { Header: "First Tower", accessor: "first_tower"},
        { Header: "First Herald", accessor: "first_rift_herald"},
        { Header: "First Inhib", accessor: "first_inhib"},
        { Header: "Dragon Kills", accessor: "dragon_kills"},
        { Header: "Rift Heralds", accessor: "rift_herald_kills"},
        { Header: "Inhibs", accessor: "inhib_kills"},
        { Header: "Allies", accessor: "allies"},
        { Header: "Enemies", accessor: "enemies"},
        { Header: "Wonnered?", accessor: (values) => {
	    const bool = values.win == "Win" ? 'True' : 'False';
	    return bool
	    }
	}
    ];

    const root = (
		    <div className="App" id="root">
		    <NavBar />
			<MyTable columns={columns} data={data} 
			    getCellProps={cellInfo => ({
			      style: {
			      backgroundColor: ((cellInfo.row.cells[13].value ==="True") ? `rgba(0,255,0,.1)`: `rgba(255,0,0,.1)`)
			    	}})}
			    />
		    </div>
    );

    return root

}

export default App;
