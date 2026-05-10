from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# List to store trips. Each trip is a dictionary.
trips = []

@app.route('/')
def index():
    # Calculate totals for each trip before displaying
    for trip in trips:
        trip['total_spent'] = sum(exp['amount'] for exp in trip['expenses'])
        trip['balance'] = trip['budget'] - trip['total_spent']
    return render_template('index.html', trips=trips)

@app.route('/add_trip', methods=['POST'])
def add_trip():
    destination = request.form.get('destination')
    budget = request.form.get('budget')
    
    if destination and budget:
        new_trip = {
            'id': len(trips) + 1,
            'destination': destination,
            'budget': int(budget),
            'expenses': [],
            'total_spent': 0,
            'balance': int(budget)
        }
        trips.append(new_trip)
    return redirect(url_for('index'))

@app.route('/add_expense/<int:trip_id>', methods=['POST'])
def add_expense(trip_id):
    item = request.form.get('item')
    amount = request.form.get('amount')
    
    if item and amount:
        for trip in trips:
            if trip['id'] == trip_id:
                trip['expenses'].append({'item': item, 'amount': int(amount)})
                break
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Using port 5001 for M2 MacBook compatibility
    app.run(debug=True, port=5001)