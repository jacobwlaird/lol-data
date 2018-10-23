//this will run my server,
//The plan is to have a front end with a list of all 6 players
//for each player, select a role
//after each player/role is selected, select how many games to look at for history,
//then recommend champs
//or if roles are not selected, recommend a role and a champ.
//NICE

const express = require("express");
const app = express();

app.set("view engine", "pug");
app.set('views', 'views');
app.use(express.static('resources'));

app.get('/', function(req, res) {
	res.render('data', {
	});
});

app.use(express.static('resources'));

const server = app.listen(6112, function() {
	console.log(`Server started on port ${server.address().port}`);
});