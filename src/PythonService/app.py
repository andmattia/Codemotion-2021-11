from flask import Flask
from flask import request
from flask import jsonify, abort
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "store"})
    )
)
zipkin_exporter = ZipkinExporter(
    endpoint="http://zipkin:9411/api/v2/spans",
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(zipkin_exporter)
)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
CORS(app)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
connectionString = "mssql+pyodbc://sa:m1Password[12J@sqlserver/Store?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString

from models import db, Store, metadata

try:
    engine = create_engine(connectionString)
    if not database_exists(engine.url):
        create_database(engine.url)
        metadata.create_all(engine)
        print('Create database!')
except:
    print('Create database error!')

SQLAlchemyInstrumentor().instrument(
    engine=engine,
)

db.init_app(app)

@app.route('/store/', methods = ['GET'])
@cross_origin()
def GetAllStore():
    result = db.session.query(Store).all()
    return jsonify([{"productId":r.productId, "availability":r.availability} for r in result])

@app.route('/store/<productId>')
@cross_origin()
def GetProductAvailability(productId):
    result = db.session.query(Store).filter_by(productId=productId).one_or_none()
    if result:
        return jsonify({"productId":result.productId, "availability":result.availability})
    else:
        abort(404)

@app.route('/store/', methods = ['POST','OPTIONS'])
@cross_origin()
def SetProductAvailability():
    productAvailability = request.get_json()
    productId = productAvailability["productId"]
    availability = productAvailability["availability"]
    find = db.session.query(Store).filter_by(productId=productId).one_or_none()
    if find: 
        find.productId = productId
        find.availability = availability
    else:
        find = Store(productId = productId, availability = availability)

    db.session.add(find)
    db.session.commit()
    return jsonify({"Message": "Ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=600)