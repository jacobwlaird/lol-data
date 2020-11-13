import React, { useState, useEffect } from 'react';
import DataTable from '../common/DataTable';
import NavBar from '../common/NavBar';
import GamesFilter from './GamesFilter';
import "bootstrap/dist/css/bootstrap.min.css"

/* Represents an individual players dashboard.  Currently only contains a table. */
const Dashboard = (props) => {
    const [userData, setUserData] = useState(0);

    let api_request = "/api/get_user_data?name=" + props.match.params.playerId;
    //We need to do stuff when we have champ card data.
    //What we want to do is... call a function UpdateChampCards?
    //We have to create a champ card component

    useEffect(() => {
    fetch(api_request).then(res => res.json()).then(data => {
	  setUserData(data);
	});
    }, [props.match.params.playerId, api_request]);

    let tableData = Array.from(userData);

    /* updateUserData is used to update the data on the screen after the update script finishes. */
    const updateUserData = () => {
	fetch(api_request).then(res => res.json()).then(data => {
	    setUserData(data);
	    tableData = Array.from(userData);
	});
    }

    //Column settings for the players table.
    const columns = [
        { Header: "Role", accessor: "role", width: "4%"},
        { Header: "Champion Name", accessor: "champion_name", width: "7%"},
        { Header: "Enemy Champ Name", accessor: "enemy_champion_name", width: "7%"},
        { Header: "First Blood", accessor: "first_blood", width: "3%"},
        { Header: "First Blood Assist", accessor: "first_blood_assist", width: "7%"},
        { Header: "Kills", accessor: "kills", width: "3%"},
        { Header: "Deaths", accessor: "deaths", width: "3%"},
        { Header: "Assists", accessor: "assists", width: "3%"},
        { Header: "Damage to Champs", accessor: "damage_to_champs", width: "3%"},
        { Header: "Damage to Turrets", accessor: "damage_to_turrets", width: "3%"},
        { Header: "Gold Per Min", accessor: "gold_per_minute", width: "7%"},
        { Header: "Creeps Per Min", accessor: "creeps_per_minute", width: "3%"},
        { Header: "XP Per Min", accessor: "xp_per_minute", width: "3%"},
        { Header: "Wards Placed", accessor: "wards_placed", width: "3%"},
        { Header: "Pinks Get", accessor: "vision_wards_bought", width: "3%"},
        { Header: "Items", accessor: "items", width: "10%"},
        { Header: "Wonned?", accessor: (values) => {
	    //Converts Win/Fail to true/false
	    const bool = values.win === "Win" ? 'True' : 'False';
	    return bool
	    }, width: "3%"}
    ];

	//We want to add a bunch of cards for each element in an API call?
    return (
	<div className="root" id="PlayerRoot">
	    <NavBar updateState={updateUserData}/>
	    <GamesFilter />
	    <DataTable columns={columns} data={tableData} 
		    getCellProps={cellInfo => ({
			style: {
			    backgroundColor: ((cellInfo.row.cells[16].value ==="True") ? `rgba(0,255,0,.2)`: `rgba(255,0,0,.2)`)
			}})}
	    />
	</div>
    );
}

export default Dashboard;
