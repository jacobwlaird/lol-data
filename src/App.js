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

//All table imports here
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';


const useStyles = makeStyles((theme) => ({
	  root: {
		      flexGrow: 1,
		    },
	  menuButton: {
		      marginRight: theme.spacing(2),
		    },
}));

//function MyTable(props) {
//	const [teamData, setTeamData] = useState(0);
//	const classes = useStyles();
//
//	useEffect(() => {
//	fetch('/api/get_team_data').then(res => res.json()).then(data => {
//		    setTeamData(data);
//		  });
//	}, []);
//
//	//Declare a header, then append all this, and then return it?
//	// need a list of game. info.
//	return (
//	<TableContainer component={Paper}>
//		      <Table className={classes.table} aria-label="simple table">
//		        <TableHead>
//		          <TableRow>
//		            <TableCell>Match ID</TableCell>
//		            <TableCell align="right">Participants</TableCell>
//		            <TableCell align="right">Enemies</TableCell>
//		            <TableCell align="right">Allies</TableCell>
//		            <TableCell align="right">Win</TableCell>
//		          </TableRow>
//		        </TableHead>
//		        <TableBody>
//		          {Array.from(teamData).map(game =>  (
//				              <TableRow key={game.match_id}>
//				                <TableCell component="th" scope="row">
//				                  {game.match_id}
//				                </TableCell>
//				                <TableCell align="right">{game.participants}</TableCell>
//				                <TableCell align="right">{game.enemies}</TableCell>
//				                <TableCell align="right">{game.allies}</TableCell>
//				                <TableCell align="right">{game.win}</TableCell>
//				              </TableRow>
//				            ))}
//	        </TableBody>
//		      </Table>
//		    </TableContainer>
//		
//		
//	)
//}

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

	const root = (
			<div className="App" id="root">
			<NavBar />
			<MyTable />
			</div>
	);
	//<NavBar />

	return root

}

export default App;
