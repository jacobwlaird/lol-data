import React, { useState, useEffect } from 'react';
import './TeamDashboard.css';
import DataTable from '../common/DataTable';
import NavBar from '../common/NavBar';
import "bootstrap/dist/css/bootstrap.min.css"
import ReactHtmlParser from 'react-html-parser';

/* Represents our shared player dashboard.  Currently only contains a table. */
const TeamDashboard = () => {

    const [teamData, setTeamData] = useState(0);

    useEffect(() => {
    fetch('/api/get_team_data').then(res => res.json()).then(data => {
	  setTeamData(data);
	});
    }, []);

    let tableData = Array.from(teamData);

    /* updateTeamData is used to update the data on the screen after the update script finishes. */
    const updateTeamData = () => {
	fetch('/api/get_team_data').then(res => res.json()).then(data => {
	    setTeamData(data);
	    tableData = Array.from(teamData);
	});
    }

    //Column settings for the team table.
    const columns = [
        { Header: "Day Played", accessor: (values) => {
	    const day = values.start_time.substring(0, 10);
	    return day
	}, width: "7%"},
        { Header: "Game Version", accessor: (values) => {
	    //Capture the first 2 sections of game version
	    var vers = "";
	    if (values.game_version !== null)
	    {
		let re = new RegExp(/(\d*.\d*\.)/g);
		vers = values.game_version.match(re)[0];
		vers = vers.substring(0, vers.length-1);
	    }

	    return vers
	}, width: "4%"},
        { Header: "Participants", accessor: "participants", Cell: ({ cell }) => {

	    //Replaces participants names with links to their profiles.
	    let { value } = cell;
	    let particips = value.replace(" ", "");
	    particips = particips.split(",");
	    let newstring = "";	
	    particips.forEach(person => newstring+= buildParticipantLink(person));
	    return <div>{ ReactHtmlParser(newstring) }</div>;

	}, width: "10%"},
        { Header: "First Blood", accessor: "first_blood", width: "3%"},
        { Header: "First Dragon", accessor: "first_dragon", width: "3%"},
        { Header: "First Tower", accessor: "first_tower", width: "3%"},
        { Header: "First Herald", accessor: "first_rift_herald", width: "3%"},
        { Header: "First Inhib", accessor: "first_inhib", width: "3%"},
        { Header: "Ally Dragon Kills", accessor: "ally_dragon_kills", width: "3%"},
        { Header: "Ally Rift Heralds", accessor: "ally_rift_herald_kills", width: "3%"},
        { Header: "Enemy Dragon Kills", accessor: "enemy_dragon_kills", width: "3%"},
        { Header: "Enemy Rift Heralds", accessor: "enemy_rift_herald_kills", width: "3%"},
        { Header: "Inhibs", accessor: "inhib_kills", width: "3%"},
        { Header: "Allies", accessor: "allies", width: "10%"},
        { Header: "Enemies", accessor: "enemies", width: "10%"},
        { Header: "Wonned?", accessor: (values) => {
	    //Converts Win/Fail to true/false
	    const bool = values.win === "Win" ? 'True' : 'False';
	    return bool
	    }, width: "3%"}
    ];

    return (
	<div className="root" id="root">
	    <NavBar updateState={updateTeamData}/>
	    <DataTable columns={columns} data={tableData} 
	        getCellProps={cellInfo => ({
		    style: {
		        backgroundColor: ((cellInfo.row.cells[15].value ==="True") ? `rgba(0,255,0,.2)`: `rgba(255,0,0,.2)`)
		     }})}
	    />
	</div>
    );
}

export default TeamDashboard;

//A helper function to return an <a> element with a link to the passed players profile.
function buildParticipantLink(playerName){
    return("<a href='/"+playerName+"'>"+playerName+"</a> ");
};
