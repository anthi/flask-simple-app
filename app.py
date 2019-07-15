from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
from flask_mysqldb import MySQL
import time
import datetime
import  yaml
import json

app = Flask(__name__)

#Configure DB
db = yaml.load(open('db_timeDiscountingExp.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']
mysql = MySQL(app)

api = Api(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})



def abort_if_participant_doesnt_exist(participant_id):
    cur = mysql.connection.cursor()
    length = cur.execute("SELECT * FROM Participants WHERE Id = %s", (participant_id))
    print(length)
    if length == 0 :
        abort(404, message="Participant {} doesn't exist".format(participant_id))


parser = reqparse.RequestParser()
parser.add_argument('member')


# member
# shows a single member item and lets you delete a member item
class Participant(Resource):
    def get(self, participant_id):
        abort_if_participant_doesnt_exist(participant_id)
        cur = mysql.connection.cursor()
        length = cur.execute("SELECT * FROM Participants WHERE Id = %s", (participant_id))
        if length > 0 :
            participants = cur.fetchall()
            row = participants[0]
            participant = {'id':row[0], 'name':row[1], 'age':row[2]}
            return participant, 204
        return False

    def delete(self, participant_id):
        abort_if_participant_doesnt_exist(participant_id)
        cur = mysql.connection.cursor()
        cur.execute("DELETE  FROM Participants WHERE Id = %s", (participant_id))
        mysql.connection.commit()
        cur.close()
        return True, 204

    def put(self, participant_id):
        abort_if_participant_doesnt_exist(participant_id)
        jsdata = request.get_json(force=True)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE Members SET Name = %s , Age = %s WHERE Id = %s", (jsdata['name'], jsdata['age'], participant_id))
        mysql.connection.commit()
        cur.close()
        return jsdata , 201


# ParticipantList
# shows a list of all Members, and lets you POST to add new members
class ParticipantList(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        length = cur.execute("SELECT `ParticipantId`, `ExpCondition`, `Age`, `Preference`, `Comments`, `ExpStartTime`, `ExpEndTime`, `ExpStartTimeNumber`, `ExpEndTimeNumber` FROM Participants;")
        items  = [ ]
        if length > 0 :
            participants = cur.fetchall()
            for row in participants:
                if row[6]:
                    timeEnd = row[6].strftime("%d-%b-%Y (%H:%M:%S.%f)") 
                else:
                    timeEnd =   'NULL'
                items.append({'participantId':row[0], 'expCondition':row[1], 'age':row[2], 'preference':row[3], 'comments':row[4],'expStartTime': row[5].strftime("%d-%b-%Y (%H:%M:%S.%f)"),'expEndTime': timeEnd, 
               'expStartTimeNumber':row[7],  'expEndTimeNumber':row[8] })
            return items      
        return False

    def post(self):
        jsdata = request.get_json(force=True)
        cur = mysql.connection.cursor()
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(timestamp)
        cur.execute("INSERT INTO Participants(ExpCondition, ExpStartTime,ExpStartTimeNumber) VALUES(%s,%s,%s)", (jsdata['expCondition'],timestamp,int(ts) ))
        length = cur.execute("SELECT  LAST_INSERT_ID()")
        result = {}
        if length > 0 :
            participantId = cur.fetchall()
            result = {
                'id': participantId[0][0],
                'expCondition': jsdata['expCondition']
            }
        mysql.connection.commit()
        cur.close()
        return result , 201


# InteractionLogList
# shows a list of all Members, and lets you POST to add new members
class InteractionLogList(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        length = cur.execute("SELECT `ParticipantId`, `ExpCondition`, `Age`, `Preference`, `Comments`, `ExpStartTime`, `ExpEndTime`, `ExpStartTimeNumber`, `ExpEndTimeNumber` FROM Participants;")
        items  = [ ]
        if length > 0 :
            interactionLogs = cur.fetchall()
            for row in interactionLogs:
                if row[6]:
                    timeEnd = row[6].strftime("%d-%b-%Y (%H:%M:%S.%f)") 
                else:
                    timeEnd =   'NULL'
                items.append({'participantId':row[0], 'expCondition':row[1], 'age':row[2], 'preference':row[3], 'comments':row[4],'expStartTime': row[5].strftime("%d-%b-%Y (%H:%M:%S.%f)"),'expEndTime': timeEnd, 
               'expStartTimeNumber':row[7],  'expEndTimeNumber':row[8] })
            return items      
        return False

    def post(self):
        jsdata = request.get_json(force=True)
        cur = mysql.connection.cursor()
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(timestamp)
        cur.execute("INSERT INTO InteractionLogs(`BlockId`, `TrialId`, `ParticipantId`, `InteractionTimestamp`, `InteractionTimeNumber`, `TargetId`, `TargetPosition`, `TargetPanel`, `ExpCondition`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (jsdata['blockId'],jsdata['trialId'],jsdata['participantId'],timestamp, int(ts), jsdata['targetId'],jsdata['targetPosition'],jsdata['targetPanel'],jsdata['expCondition']))
        mysql.connection.commit()
        cur.close()
        return  201

##
# Actually setup the Api resource routing here
##
api.add_resource(InteractionLogList, '/interactionlogs')
api.add_resource(ParticipantList, '/participants')
api.add_resource(Participant, '/participant/<participant_id>')

if __name__ == '__main__':
    app.run()
