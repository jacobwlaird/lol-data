import React from 'react';
import Dashboard from './components/player/Dashboard';
import TeamDashboard from './components/team/TeamDashboard';
import "bootstrap/dist/css/bootstrap.min.css"
import { BrowserRouter as Router, Route} from 'react-router-dom';

function App() {

    return (<Router>
		<Route exact path="/" component={TeamDashboard} />
		<Route exact path="/:playerId" component={Dashboard} />
	    </Router>);
}

export default App;
