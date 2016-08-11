from flask import Flask, jsonify, make_response, request, abort, render_template
import sys
sys.path.append("../")
from configure import ConstExtractor

app = Flask(__name__)


settings = ConstExtractor()
noise_available = {"status": "False"}
input_text = {"speech_text": "no updates"}
command = {
    "type": "none",
    "command": "none1"
}


@app.errorhandler(404)
def not_found(err):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_recognized(err):
    return make_response(jsonify({'error': 'Not recognized command'}), 400)


@app.route('/input/noise', methods=['POST'])
def noise_input():
    global noise_available
    noise_available["status"] = "True"
    if not request.json or not "speech_text" in request.json:
        abort(400)
    else:
        print "Here is Noise"
        return jsonify(request.json), 201


@app.route('/output/noise', methods=['GET'])
def noise_output():
    global noise_available
    tmp_noise = noise_available
    noise_available["status"] = "False"
    return jsonify(noise_available)


@app.route('/input', methods=['POST'])
def speech_text_input():
    global input_text
    if not request.json or not 'speech_text' in request.json:
        abort(400)
    else:
        input_text = {"speech_text": request.json['speech_text']}
        print input_text
        return jsonify(input_text), 201


@app.route('/core/input', methods=['GET'])
def get_speech_text():
    global input_text
    tmp_text = input_text
    input_text = {"speech_text": "no updates"}
    return jsonify(tmp_text)


@app.route('/core/output', methods=['POST'])
def command_input():
    global command
    print request.json
    if not request.json or not 'type' in request.json or not 'command' in request.json:
        abort(400)
    else:
        command = {
            'type': request.json['type'],
            'command': request.json['command']
        }
        print command
        return jsonify(command), 201


@app.route('/output', methods=['GET'])
def get_command():
    global command
    tmp_command = command
    print tmp_command
    command = {
        "type": "none",
        "command": "none"
    }
    return jsonify(tmp_command)


@app.route('/screens/idle/')
def idle():
    return render_template("idle.html", background=settings.getValue("arius_screen_idle_background"))


@app.route('/screens/error/')
def error():
    return render_template("error.html", background=settings.getValue("arius_screen_error_background"))


@app.route('/screens/search/')
def search():
    return render_template("search.html", background=settings.getValue("arius_screen_search_background"))

if __name__ == '__main__':
    app.run(debug=True)
