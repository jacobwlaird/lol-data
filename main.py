from flask import Flask, render_template, request, Response, abort
import subprocess
from resources.python.apis.get_user_data import get_data
from resources.python.apis.get_team_data import get_team_data


app = Flask(__name__)

@app.route("/")
def main():
	return render_template('data.html')


@app.route("/update", methods=['POST'])
def update():
	apiKey = request.form['apiKey']
	#subprocess for whole scripts.
	subprocess.check_output(['python', 'resources/python/loldata.py', apiKey])	
	what = "Update complete! Nice!" # this should return more useful data.
	return render_template('data.html', message=what)

@app.route("/api/get_user_data")
def returnData():
	name = ""
	if 'name' in request.args:
		name = request.args['name']
	else:
		# create a response object.
		
		res = Response("404: name must be provided. Try adding ?name=dumat to the url.", status=404, mimetype='application/json')
		return res

	# gotta get the name from.. something in here.
	#run a script here, get the results from that and send that back as json.
	json = get_data(name)
	response = Response(json, status=200, mimetype='application/json')
	return response

@app.route("/api/get_team_data")
def returnMatchData():
	# gotta get the name from.. something in here.
	#run a script here, get the results from that and send that back as json.
	json = get_team_data()
	response = Response(json, status=200, mimetype='application/json')
	return response

@app.route("/getrole", methods=['POST'])
def getRole():
	# gonna need a hidden input to hold the name of the player we're getting the role for?
	# apiKey = request.form['hidNames'] # We need to pass in a list of players, right? get roles should work for 1 person, for two people, for 3, etc. More info in the file itself.
	what = subprocess.check_output(['python', 'resources/python/getrole.py', 'spaynkee&dumat'])	
	return render_template('data.html', message=what)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
