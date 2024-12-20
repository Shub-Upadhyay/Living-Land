from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration for the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/spatial_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Global flag to ensure tables are created only once
tables_initialized = False

# Models
class PointData(db.Model):
    """
    Represents a single point in the spatial dataset with attributes for name, latitude, and longitude.

    Attributes:
        id (int): Unique identifier for the point.
        name (str): Name or label for the point.
        latitude (float): Latitude of the point.
        longitude (float): Longitude of the point.
    """
    __tablename__ = 'point_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class PolygonData(db.Model):
    """
    Represents a polygon in the spatial dataset with attributes for name and coordinates.

    Attributes:
        id (int): Unique identifier for the polygon.
        name (str): Name or label for the polygon.
        coordinates (str): JSON string representing the polygon's coordinates.
    """
    __tablename__ = 'polygon_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.Text, nullable=False)  # Store coordinates as a string

# Ensure tables are created before handling any requests
@app.before_request
def create_tables():
    """
    Ensures that the necessary tables in the database are created before handling any requests.
    This is executed only once when the first request is received.
    """
    global tables_initialized
    if not tables_initialized:
        with app.app_context():
            db.create_all()
        tables_initialized = True

# API Endpoints

# Create or Update Point Data
@app.route('/point', methods=['POST', 'PUT'])
def handle_point():
    """
    Handles creation (POST) or update (PUT) of point data.

    Request:
        - POST: {"name": "Point Name", "latitude": 12.34, "longitude": 56.78}
        - PUT: {"id": 1, "name": "Updated Point Name", "latitude": 23.45, "longitude": 67.89}

    Response:
        - Success: {"message": "Point saved successfully"}
        - Error (PUT): {"error": "Point not found"}
    """
    data = request.json
    if request.method == 'POST':
        point = PointData(name=data['name'], latitude=data['latitude'], longitude=data['longitude'])
        db.session.add(point)
    elif request.method == 'PUT':
        point = PointData.query.get(data['id'])
        if not point:
            return jsonify({'error': 'Point not found'}), 404
        point.name = data['name']
        point.latitude = data['latitude']
        point.longitude = data['longitude']
    db.session.commit()
    return jsonify({'message': 'Point saved successfully'})

# Retrieve Point Data
@app.route('/point/<int:point_id>', methods=['GET'])
def get_point(point_id):
    """
    Retrieves details of a specific point using its ID.

    Request:
        - GET /point/<point_id>

    Response:
        - Success: {"id": 1, "name": "Point Name", "latitude": 12.34, "longitude": 56.78}
        - Error: {"error": "Point not found"}
    """
    point = PointData.query.get(point_id)
    if not point:
        return jsonify({'error': 'Point not found'}), 404
    return jsonify({
        'id': point.id,
        'name': point.name,
        'latitude': point.latitude,
        'longitude': point.longitude
    })

# Create or Update Polygon Data
@app.route('/polygon', methods=['POST', 'PUT'])
def handle_polygon():
    """
    Handles creation (POST) or update (PUT) of polygon data.

    Request:
        - POST: {"name": "Polygon Name", "coordinates": "[[[x1, y1], [x2, y2], ...]]"}
        - PUT: {"id": 1, "name": "Updated Polygon Name", "coordinates": "[[[x1, y1], [x2, y2], ...]]"}

    Response:
        - Success: {"message": "Polygon saved successfully"}
        - Error (PUT): {"error": "Polygon not found"}
    """
    data = request.json
    if request.method == 'POST':
        polygon = PolygonData(name=data['name'], coordinates=data['coordinates'])
        db.session.add(polygon)
    elif request.method == 'PUT':
        polygon = PolygonData.query.get(data['id'])
        if not polygon:
            return jsonify({'error': 'Polygon not found'}), 404
        polygon.name = data['name']
        polygon.coordinates = data['coordinates']
    db.session.commit()
    return jsonify({'message': 'Polygon saved successfully'})

# Retrieve Polygon Data
@app.route('/polygon/<int:polygon_id>', methods=['GET'])
def get_polygon(polygon_id):
    """
    Retrieves details of a specific polygon using its ID.

    Request:
        - GET /polygon/<polygon_id>

    Response:
        - Success: {"id": 1, "name": "Polygon Name", "coordinates": "[[[x1, y1], [x2, y2], ...]]"}
        - Error: {"error": "Polygon not found"}
    """
    polygon = PolygonData.query.get(polygon_id)
    if not polygon:
        return jsonify({'error': 'Polygon not found'}), 404
    return jsonify({
        'id': polygon.id,
        'name': polygon.name,
        'coordinates': polygon.coordinates
    })

if __name__ == '__main__':
    app.run(debug=True)
