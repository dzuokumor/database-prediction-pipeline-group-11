from graphviz import Digraph


def create_erd_diagram():
    dot = Digraph(comment='Cardiovascular Disease Database ERD',
                  format='png',
                  graph_attr={
                      'rankdir': 'TB',
                      'splines': 'ortho',
                      'nodesep': '1',
                      'ranksep': '1.5',
                      'bgcolor': 'white',
                      'fontname': 'Arial',
                      'fontsize': '14'
                  },
                  node_attr={
                      'shape': 'plain',
                      'fontname': 'Arial',
                      'fontsize': '11'
                  })

    patients_table = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lightblue">
            <TR><TD COLSPAN="3" BGCOLOR="darkblue"><FONT COLOR="white"><B>patients</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><U>patient_id</U></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">PK</TD></TR>
            <TR><TD ALIGN="LEFT">age_days</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">age_years</TD><TD ALIGN="LEFT">REAL</TD><TD ALIGN="LEFT"></TD></TR>
            <TR><TD ALIGN="LEFT">gender</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">height</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">weight</TD><TD ALIGN="LEFT">REAL</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">bmi</TD><TD ALIGN="LEFT">REAL</TD><TD ALIGN="LEFT">COMPUTED</TD></TR>
            <TR><TD ALIGN="LEFT">created_at</TD><TD ALIGN="LEFT">TIMESTAMP</TD><TD ALIGN="LEFT">DEFAULT</TD></TR>
        </TABLE>
    >'''

    medical_measurements_table = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lightgreen">
            <TR><TD COLSPAN="3" BGCOLOR="darkgreen"><FONT COLOR="white"><B>medical_measurements</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><U>measurement_id</U></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">PK</TD></TR>
            <TR><TD ALIGN="LEFT"><I>patient_id</I></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">FK</TD></TR>
            <TR><TD ALIGN="LEFT">ap_hi</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">ap_lo</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">cholesterol</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">glucose</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">measurement_date</TD><TD ALIGN="LEFT">TIMESTAMP</TD><TD ALIGN="LEFT">DEFAULT</TD></TR>
        </TABLE>
    >'''

    lifestyle_factors_table = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lightyellow">
            <TR><TD COLSPAN="3" BGCOLOR="orange"><FONT COLOR="white"><B>lifestyle_factors</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><U>lifestyle_id</U></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">PK</TD></TR>
            <TR><TD ALIGN="LEFT"><I>patient_id</I></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">FK</TD></TR>
            <TR><TD ALIGN="LEFT">smoke</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">alcohol</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">physical_activity</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">recorded_at</TD><TD ALIGN="LEFT">TIMESTAMP</TD><TD ALIGN="LEFT">DEFAULT</TD></TR>
        </TABLE>
    >'''

    diagnoses_table = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lightcoral">
            <TR><TD COLSPAN="3" BGCOLOR="darkred"><FONT COLOR="white"><B>diagnoses</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><U>diagnosis_id</U></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">PK</TD></TR>
            <TR><TD ALIGN="LEFT"><I>patient_id</I></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">FK</TD></TR>
            <TR><TD ALIGN="LEFT">cardiovascular_disease</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">diagnosis_date</TD><TD ALIGN="LEFT">TIMESTAMP</TD><TD ALIGN="LEFT">DEFAULT</TD></TR>
        </TABLE>
    >'''

    diagnosis_log_table = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lightgray">
            <TR><TD COLSPAN="3" BGCOLOR="gray"><FONT COLOR="white"><B>diagnosis_log</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><U>log_id</U></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">PK</TD></TR>
            <TR><TD ALIGN="LEFT"><I>diagnosis_id</I></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT"></TD></TR>
            <TR><TD ALIGN="LEFT"><I>patient_id</I></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT"></TD></TR>
            <TR><TD ALIGN="LEFT">action_type</TD><TD ALIGN="LEFT">TEXT</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">cardiovascular_disease</TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT"></TD></TR>
            <TR><TD ALIGN="LEFT">action_timestamp</TD><TD ALIGN="LEFT">TIMESTAMP</TD><TD ALIGN="LEFT">DEFAULT</TD></TR>
        </TABLE>
    >'''

    risk_assessments_table = '''<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lavender">
            <TR><TD COLSPAN="3" BGCOLOR="purple"><FONT COLOR="white"><B>risk_assessments</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><U>assessment_id</U></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">PK</TD></TR>
            <TR><TD ALIGN="LEFT"><I>patient_id</I></TD><TD ALIGN="LEFT">INTEGER</TD><TD ALIGN="LEFT">FK</TD></TR>
            <TR><TD ALIGN="LEFT">risk_score</TD><TD ALIGN="LEFT">REAL</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">risk_level</TD><TD ALIGN="LEFT">TEXT</TD><TD ALIGN="LEFT">NOT NULL</TD></TR>
            <TR><TD ALIGN="LEFT">assessment_date</TD><TD ALIGN="LEFT">TIMESTAMP</TD><TD ALIGN="LEFT">DEFAULT</TD></TR>
        </TABLE>
    >'''

    dot.node('patients', patients_table)
    dot.node('medical_measurements', medical_measurements_table)
    dot.node('lifestyle_factors', lifestyle_factors_table)
    dot.node('diagnoses', diagnoses_table)
    dot.node('diagnosis_log', diagnosis_log_table)
    dot.node('risk_assessments', risk_assessments_table)

    dot.edge('patients', 'medical_measurements',
             label='1:N',
             color='darkgreen',
             penwidth='2',
             arrowhead='crow')

    dot.edge('patients', 'lifestyle_factors',
             label='1:N',
             color='orange',
             penwidth='2',
             arrowhead='crow')

    dot.edge('patients', 'diagnoses',
             label='1:N',
             color='darkred',
             penwidth='2',
             arrowhead='crow')

    dot.edge('patients', 'risk_assessments',
             label='1:N',
             color='purple',
             penwidth='2',
             arrowhead='crow')

    dot.edge('diagnoses', 'diagnosis_log',
             label='TRIGGER\n(auto)',
             color='gray',
             penwidth='2',
             style='dashed',
             arrowhead='normal')

    dot.attr(
        label=r'\n\nCardiovascular Disease Database Schema\nERD Diagram\n\nLegend:\nPK = Primary Key\nFK = Foreign Key\nUnderlined = Primary Key\nItalic = Foreign Key',
        fontsize='16',
        fontname='Arial Bold')

    dot.render('cardiovascular_erd', view=False, cleanup=True)
    print("ERD diagram created: cardiovascular_erd.png")


if __name__ == '__main__':
    create_erd_diagram()