from flask import Flask, render_template, request, redirect

app = Flask(__name__)


trips = []

@app.route('/')
def index():
    return render_template('index.html', trips=trips)

@app.route('/add_trip', methods=['POST'])
def add_trip():

    destination = request.form.get('destination')
    budget = int(request.form.get('budget'))
    

    new_trip = {
        'id': len(trips) + 1,
        'destination': destination,
        'budget': budget,
        'spent': 0
    }
    trips.append(new_trip)
    
   
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)