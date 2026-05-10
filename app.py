from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

trips = []

@app.route('/')
def index():
    return render_template('index.html', trips=trips)

@app.route('/add_trip', methods=['POST'])
def add_trip():
   
    destination = request.form.get('destination')
    budget = request.form.get('budget')
    
    
    trips.append({'destination': destination, 'budget': budget})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)