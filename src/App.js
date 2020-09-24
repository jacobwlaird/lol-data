import React, { useState, useEffect } from 'react';
//import './App.css';
import MyTable from './components/MyTable';
import NavBar from './components/NavBar';
import Dashboard from './components/Dashboard';
import TeamDashboard from './components/TeamDashboard';
import "bootstrap/dist/css/bootstrap.min.css"
import { BrowserRouter as Router, Route} from 'react-router-dom';

function App() {

    return (<Router>
		<Route exact path="/" component={TeamDashboard} />
		<Route exact path="/:playerId" component={Dashboard} />
	    </Router>);
}

export default App;
