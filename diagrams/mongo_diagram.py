from graphviz import Digraph


def create_mongodb_schema_diagram():
    dot = Digraph(comment='MongoDB Schema',
                  format='png',
                  graph_attr={
                      'rankdir': 'LR',
                      'bgcolor': 'white',
                      'fontname': 'Arial',
                      'fontsize': '14'
                  },
                  node_attr={
                      'shape': 'plain',
                      'fontname': 'Courier',
                      'fontsize': '10'
                  })

    patients_collection = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10" BGCOLOR="#E8F4F8">
            <TR><TD COLSPAN="2" BGCOLOR="#0077BE"><FONT COLOR="white" POINT-SIZE="14"><B>patients Collection</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT" BGCOLOR="#F0F8FF">
                <FONT FACE="Courier New" POINT-SIZE="10">
                {<BR/>
                  "_id": ObjectId(),<BR/>
                  "patient_id": 0,<BR/>
                  "demographics": {<BR/>
                    "age_days": 18393,<BR/>
                    "age_years": 50.36,<BR/>
                    "gender": "female",<BR/>
                    "height_cm": 168,<BR/>
                    "weight_kg": 62.0,<BR/>
                    "bmi": 21.97<BR/>
                  },<BR/>
                  "lifestyle": {<BR/>
                    "smoker": false,<BR/>
                    "alcohol_consumption": false,<BR/>
                    "physically_active": true<BR/>
                  },<BR/>
                  "created_at": ISODate()<BR/>
                }<BR/>
                </FONT>
            </TD></TR>
            <TR><TD BGCOLOR="#D0E8F0">
                <FONT POINT-SIZE="9">
                <B>Indexes:</B><BR/>
                • patient_id (unique)<BR/>
                <B>Total Documents:</B> ~70,000
                </FONT>
            </TD></TR>
        </TABLE>
    >'''

    medical_records_collection = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10" BGCOLOR="#E8F8E8">
            <TR><TD COLSPAN="2" BGCOLOR="#228B22"><FONT COLOR="white" POINT-SIZE="14"><B>medical_records Collection</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT" BGCOLOR="#F0FFF0">
                <FONT FACE="Courier New" POINT-SIZE="10">
                {<BR/>
                  "_id": ObjectId(),<BR/>
                  "patient_id": 0,<BR/>
                  "measurements": {<BR/>
                    "blood_pressure": {<BR/>
                      "systolic": 110,<BR/>
                      "diastolic": 80<BR/>
                    },<BR/>
                    "cholesterol_level": 1,<BR/>
                    "cholesterol_label": "normal",<BR/>
                    "glucose_level": 1,<BR/>
                    "glucose_label": "normal"<BR/>
                  },<BR/>
                  "diagnosis": {<BR/>
                    "cardiovascular_disease": false,<BR/>
                    "diagnosis_date": ISODate()<BR/>
                  },<BR/>
                  "recorded_at": ISODate()<BR/>
                }<BR/>
                </FONT>
            </TD></TR>
            <TR><TD BGCOLOR="#D0F0D0">
                <FONT POINT-SIZE="9">
                <B>Indexes:</B><BR/>
                • patient_id<BR/>
                • diagnosis.cardiovascular_disease<BR/>
                <B>Total Documents:</B> ~70,000
                </FONT>
            </TD></TR>
        </TABLE>
    >'''

    dot.node('patients', patients_collection)
    dot.node('medical_records', medical_records_collection)

    dot.edge('patients', 'medical_records',
             label='  Referenced by\n  patient_id  ',
             color='#FF6347',
             penwidth='2',
             style='dashed',
             fontsize='11',
             fontcolor='#FF6347')

    dot.attr(
        label=r'\n\nMongoDB Document Structure\nCardiovascular Disease Database\n\nNote: Collections are linked by patient_id (not enforced by DB)',
        fontsize='14',
        fontname='Arial')

    dot.render('mongodb_schema', view=False, cleanup=True)
    print("MongoDB schema diagram created: mongodb_schema.png")


if __name__ == '__main__':
    create_mongodb_schema_diagram()