from flask import Flask, render_template, request, Response, abort
import subprocess
from resources.python.apis.get_user_data import get_data
from resources.python.apis.get_team_data import get_team_data


# app = Flask(__name__) # Dev
app = Flask(__name__, static_folder='./build', static_url_path='/') # prod


@app.route("/")
def main():
        return app.send_static_file('index.html')

@app.route("/update", methods=['POST'])
def update():
	# depreciated
	return render_template('data.html', message="")

@app.route("/react_test")
def react_test():
    #return Response({'message': "Hey yeah"}, status=200, mimetype='application/json')
    return {"message": "Hey yeah this is it"}

@app.route("/api/get_user_data")
def returnData():
	name = ""
	if 'name' in request.args:
		name = request.args['name']
	else:
		# create a response object.
		
		res = Response("404: name must be provided. Try adding ?name=dumat to the url.", status=404, mimetype='application/json')
		return res

	json = get_data(name)
	response = Response(json, status=200, mimetype='application/json')
	return response

@app.route("/api/get_team_data")
def returnMatchData():

	#run a script here, get the results from that and send that back as json.
	json = get_team_data()
	response = Response(json, status=200, mimetype='application/json')
	return response

@app.route("/getrole", methods=['POST'])
def getRole():
	# depreciated
	# what = subprocess.check_output(['python', 'resources/python/getrole.py', 'spaynkee&dumat'])	
	return render_template('data.html', message="")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
