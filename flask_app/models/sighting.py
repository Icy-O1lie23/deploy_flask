from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models.user import User


class Sighting:
    db = "sasquatch_reports"
    def __init__(self, data):
        self.sighting_id = data['sighting_id']
        self.location = data['location']
        self.date_of_sighting = data['date_of_sighting']
        self.number_of_sasquatches = data['number_of_sasquatches']
        self.description = data['description']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
        user = User.get_by_id(self.user_id)
        if user:
            self.reporter_full_name = f"{user.first_name} {user.last_name}"
        else:
            self.reporter_full_name = "Unknown User"
    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO sightings (location, date_of_sighting, number_of_sasquatches, description, user_id, created_at, updated_at) VALUES (%(location)s, %(date_of_sighting)s, %(number_of_sasquatches)s, %(description)s, %(user_id)s, NOW(), NOW());"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_all(cls):
        query = "SELECT sightings.*, CONCAT(users.first_name, ' ', users.last_name) AS reporter_full_name, COUNT(skeptics.skeptic_id) AS skeptic_count " \
                "FROM sightings " \
                "LEFT JOIN users ON sightings.user_id = users.user_id " \
                "LEFT JOIN skeptics ON sightings.sighting_id = skeptics.sighting_id " \
                "GROUP BY sightings.sighting_id"
        results = connectToMySQL('sasquatch_reports').query_db(query)
        sightings = []
        for row in results:
            data = {
                'sighting_id': row['sighting_id'],
                'location': row['location'],
                'date_of_sighting': row['date_of_sighting'],
                'number_of_sasquatches': row['number_of_sasquatches'],
                'description': row['description'],
                'user_id': row['user_id'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'reporter_full_name': row['reporter_full_name'],
                'skeptic_count': 0,
            }
            sightings.append(cls(data))
        return sightings


    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM sightings WHERE sighting_id = %(sighting_id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        if not results:
            return None
        return cls(results[0])

    @classmethod
    def update(cls, data):
        query = "UPDATE sightings SET location=%(location)s, date_of_sighting=%(date_of_sighting)s, " \
                "number_of_sasquatches=%(number_of_sasquatches)s, description=%(description)s, " \
                "updated_at=NOW() WHERE sighting_id = %(sighting_id)s;"
        return connectToMySQL(cls.db).query_db(query, data)


    @classmethod
    def delete(cls, data):
        query = "DELETE FROM sightings WHERE sighting_id = %(sighting_id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_by_id(cls, sighting_id):
        query = "SELECT * FROM sightings WHERE sighting_id = %(sighting_id)s;"
        data = {'sighting_id': sighting_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return None

    @classmethod
    def update_skeptic_count(cls, sighting_id):
        query = "UPDATE sightings SET skeptic_count = skeptic_count + 1 WHERE sighting_id = %(sighting_id)s;"
        data = {'sighting_id': sighting_id}
        connectToMySQL('sasquatch_reports').query_db(query, data)
        
    @staticmethod
    def is_skeptic(user_id, sighting_id):
        query = "SELECT * FROM skeptics WHERE user_id = %(user_id)s AND sighting_id = %(sighting_id)s;"
        data = {'user_id': user_id, 'sighting_id': sighting_id}
        result = connectToMySQL('sasquatch_reports').query_db(query, data)
        return bool(result)
        
    @classmethod
    def add_skeptic(cls, user_id, sighting_id):
        query = "INSERT INTO skeptics (user_id, sighting_id) VALUES (%(user_id)s, %(sighting_id)s);"
        data = {'user_id': user_id, 'sighting_id': sighting_id}
        connectToMySQL(cls.db).query_db(query, data)
        updated_skeptics = cls.get_skeptics_for_sighting(sighting_id)
        return updated_skeptics 

    @classmethod
    def remove_skeptic(cls, user_id, sighting_id):
        query = "DELETE FROM skeptics WHERE user_id = %(user_id)s AND sighting_id = %(sighting_id)s;"
        data = {'user_id': user_id, 'sighting_id': sighting_id}
        connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_skeptics_for_sighting(cls, sighting_id):
        query = "SELECT users.first_name, users.last_name " \
                "FROM skeptics " \
                "JOIN users ON skeptics.user_id = users.user_id " \
                "WHERE skeptics.sighting_id = %(sighting_id)s;"
        data = {'sighting_id': sighting_id}
        results = connectToMySQL(cls.db).query_db(query, data)
        skeptics = []
        for row in results:
            full_name = f"{row['first_name']} {row['last_name']}"
            skeptics.append({'full_name': full_name})
        return skeptics