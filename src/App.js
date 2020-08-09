import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

function Table(props) {
	const [teamData, setTeamData] = useState(0);

	useEffect(() => {
	fetch('/api/get_team_data').then(res => res.json()).then(data => {
		    setTeamData(data);
		  });
	}, []);

	//Declare a header, then append all this, and then return it?
	// need a list of game. info.
	return Array.from(teamData).map(game => (
		<tr key={game.match_id}>
			<td>{game.match_id}</td>
			<td>{game.version}</td>
			<td>{game.first_blood === 1 ? 'True' : 'False'}</td>
			<td>{game.participants}</td>
		</tr>
	))
}

function App() {

	const root = (
		<div className="App" id="root">
		<Table />
		</div>
	);


	return root

// move the old stuff for now.
//  return (
//    <div className="App">
//      <header className="App-header">
//        <img src={logo} className="App-logo" alt="logo" />
//        <p>
//          Edit <code>src/App.js</code> and save to reload.
//        </p>
//        <a
//          className="App-link"
//          href="https://reactjs.org"
//          target="_blank"
//          rel="noopener noreferrer"
//        >
//          Learn React
//        </a>
//
//	  <p>The server message is {currentTime}.</p>
//      </header>
//    </div>
//  );
}

export default App;
