//this will run my server,
//The plan is to have a front end with a list of all 6 players
//for each player, select a role
//after each player/role is selected, select how many games to look at for history,
//then recommend champs
//or if roles are not selected, recommend a role and a champ.
//NICE

let {PythonShell} = require('python-shell');

const express = require("express");
const app = express();

app.set("view engine", "pug");
app.set('views', 'views');
app.use(express.static('resources'));

app.get('/', function(req, res) {
	res.render('data', {
	});
});

app.get('/getRole', function(req, res){
	console.log(req.query.passed);
	PythonShell.run('./resources/python/test.py', null, function (err, results) {
			if (err) throw err;
			console.log(results[0]);
		});
	res.render('data', {});
})

const server = app.listen(6112, function() {
	console.log(`Server started on port ${server.address().port}`);
});