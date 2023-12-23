from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.sighting import Sighting


@app.route('/dashboard')
def dashboard():
    user_full_name = session.get('user_full_name') 
    if 'user_id' not in session:
        return redirect('/')
    
    sightings = Sighting.get_all()
    return render_template('dashboard.html', sightings=sightings, user_full_name=user_full_name)


@app.route('/new/sighting')
def new_sighting():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('report_sighting.html')

@app.route('/create/sighting', methods=['POST'])
def create_sighting():
    if 'user_id' not in session:
        return redirect('/')
    
    data = {
        'location': request.form['location'],
        'date_of_sighting': request.form['date_of_sighting'],
        'number_of_sasquatches': request.form['number_of_sasquatches'],
        'description': request.form['description'],
        'user_id': session['user_id']  
        
    }
    
    Sighting.save(data)
    return redirect('/dashboard')

@app.route('/edit/sighting/<int:sighting_id>')
def edit_sighting(sighting_id):
    if 'user_id' not in session:
        return redirect('/')
    sighting = Sighting.get_one({'sighting_id': sighting_id})
    return render_template('edit_sighting.html', sighting=sighting)

@app.route('/update/sighting/<int:sighting_id>', methods=['POST'])
def update_sighting(sighting_id):
    if 'user_id' not in session:
        return redirect('/')

    data = {
        'location': request.form['location'],
        'date_of_sighting': request.form['date_of_sighting'],
        'number_of_sasquatches': request.form['number_of_sasquatches'],
        'description': request.form['description'],
        'sighting_id': sighting_id 
    }
    
    Sighting.update(data)
    return redirect('/dashboard')

@app.route('/delete/sighting/<int:sighting_id>', methods=['GET', 'POST'])
def delete_sighting(sighting_id):
    if 'user_id' not in session:
        return redirect('/')

    sighting = Sighting.get_by_id(sighting_id)
    if sighting and sighting.user_id == session['user_id']:
        Sighting.delete({'sighting_id': sighting_id})
        return redirect('/dashboard')
    else:
        flash("You are not authorized to delete this sighting.")
        return redirect(f'/show/sighting/{sighting_id}')


@app.route('/show/sighting/<int:sighting_id>')
def view_sighting(sighting_id):
    sighting = Sighting.get_by_id(sighting_id)
    if sighting is None:
        flash("Sighting not found")
        return redirect('/dashboard')
    user_id = session.get('user_id')
    is_skeptic = False
    if user_id:
        is_skeptic = Sighting.is_skeptic(user_id, sighting_id)
    return render_template('show_sighting.html', sighting=sighting, is_skeptic=is_skeptic)


@app.route('/skeptical/<int:sighting_id>', methods=['POST'])
def skeptical(sighting_id):
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    action = request.form.get('action')
    if action == "add_skeptic":
        if not Sighting.is_skeptic(user_id, sighting_id):
            Sighting.add_skeptic(user_id, sighting_id)
    elif action == "remove_skeptic":
        Sighting.remove_skeptic(user_id, sighting_id)
    updated_skeptics = Sighting.get_skeptics_for_sighting(sighting_id)
    sighting = Sighting.get_by_id(sighting_id)
    if sighting:
        sighting.skeptics = updated_skeptics
    return render_template('show_sighting.html', sighting=sighting, is_skeptic=action == "add_skeptic")

