import React, { useState, useEffect } from 'react';
import MyTable from './MyTable';
import NavBar from './NavBar';
import "bootstrap/dist/css/bootstrap.min.css"

const Dashboard = (props) => {

    const [userData, setUserData] = useState(0);
    let api_request = "";
    if (props.match.params.playerId !== undefined)
    {
	    api_request = "/api/get_user_data?name=" + props.match.params.playerId;
    }
    else {
	    api_request = "/api/get_user_data?name=spaynkee";
    }

    useEffect(() => {
	    let api_request = "";
	    if (props.match.params.playerId !== undefined)
	    {
		    api_request = "/api/get_user_data?name=" + props.match.params.playerId;
	    }
	    else {
		    api_request = "/api/get_user_data?name=spaynkee";
	    }
    fetch(api_request).then(res => res.json()).then(data => {
	  setUserData(data);
	});
    }, []);

    let tableData = Array.from(userData);

    //function for our component to update the page data when possible.
    const updateUserData = () => {
		    fetch(api_request).then(res => res.json()).then(data => {
		    setUserData(data);
		    tableData = Array.from(userData);
		});
    }

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
	    const bool = values.win === "Win" ? 'True' : 'False';
	    return bool
	    }, width: "3%"}
    ];

    const root = (
		    <div className="root" id="root">
		    <NavBar updateState={updateUserData}/>
			<MyTable columns={columns} data={tableData} 
			    getCellProps={cellInfo => ({
			      style: {
			      backgroundColor: ((cellInfo.row.cells[16].value ==="True") ? `rgba(0,255,0,.2)`: `rgba(255,0,0,.2)`)
			    	}})}
			    />
		    </div>
    );

    return root

}

export default Dashboard;
