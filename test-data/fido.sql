/* ***************************************************************************** 
******************************************************************************** 

SCRIPT NAME:  DDL_For_CTOM_Tables_For_Oracle.sql 
PURPOSE:      Create or recreate tables based on Clinical Trial Object Model. 
AUTHOR:		  ScenPro, Inc.
DATE CREATED:	  March, 2006 
VERSION: 	  CTOM v0.53Plus 
NOTE:		  This script was created in Toad and is best viewed through that tool.

******************************************************************************** 
***************************************************************************** */ 

SET ECHO ON

SET DEFINE OFF

SPOOL DDL_For_CTOM_Tables.lst


--  Drop Tables 
DROP TABLE Activity CASCADE CONSTRAINTS
;

DROP TABLE Activity_Relationship CASCADE CONSTRAINTS
;

DROP TABLE Adverse_Event CASCADE CONSTRAINTS
;

DROP TABLE Adverse_Event_Therapy CASCADE CONSTRAINTS
;

DROP TABLE Agent CASCADE CONSTRAINTS
;

DROP TABLE Agent_Occurrence CASCADE CONSTRAINTS
;

DROP TABLE Assessment CASCADE CONSTRAINTS
;

DROP TABLE Assessment_Relationship CASCADE CONSTRAINTS
;

DROP TABLE Cancer_Stage CASCADE CONSTRAINTS
;

DROP TABLE Central_Laboratory CASCADE CONSTRAINTS
;

DROP TABLE Clinical_Result CASCADE CONSTRAINTS
;

DROP TABLE Concept_Descriptor CASCADE CONSTRAINTS
;

DROP TABLE Death_Summary CASCADE CONSTRAINTS
;

DROP TABLE Diagnosis CASCADE CONSTRAINTS
;

DROP TABLE Disease_Response CASCADE CONSTRAINTS
;

DROP TABLE Eligibility_Checklist_Criteria CASCADE CONSTRAINTS
;

DROP TABLE Eligibility_Criteria CASCADE CONSTRAINTS
;

DROP TABLE Eligibility_Checklist CASCADE CONSTRAINTS
;

DROP TABLE Female_Reproductve_Charactrstc CASCADE CONSTRAINTS
;

DROP TABLE Healthcare_Site CASCADE CONSTRAINTS
;

DROP TABLE Healthcare_Site_Investigator CASCADE CONSTRAINTS
;

DROP TABLE Healthcare_Site_Prtcpnt CASCADE CONSTRAINTS
;

DROP TABLE Healthcare_Site_Prtcpnt_Role CASCADE CONSTRAINTS
;

DROP TABLE Histopathology CASCADE CONSTRAINTS
;

DROP TABLE Histopathology_Grade CASCADE CONSTRAINTS
;

DROP TABLE Imaging CASCADE CONSTRAINTS
;

DROP TABLE Identifier CASCADE CONSTRAINTS
;

DROP TABLE Investigator CASCADE CONSTRAINTS
;

DROP TABLE Lab_Viewer_Status CASCADE CONSTRAINTS
;

DROP TABLE Lesion_Description CASCADE CONSTRAINTS
;

DROP TABLE Lesion_Evaluation CASCADE CONSTRAINTS
;

DROP TABLE Metastasis_Site CASCADE CONSTRAINTS
;

DROP TABLE Neoplasm CASCADE CONSTRAINTS
;

DROP TABLE Observation CASCADE CONSTRAINTS
;

DROP TABLE OBSERVATION_ASSESSMENT CASCADE CONSTRAINTS
;

DROP TABLE Observation_Relationship CASCADE CONSTRAINTS
;

DROP TABLE Participant CASCADE CONSTRAINTS
;

DROP TABLE Participant_Eligibility_Answer CASCADE CONSTRAINTS
;

DROP TABLE Performing_Laboratory CASCADE CONSTRAINTS
;

DROP TABLE Person_Occupation CASCADE CONSTRAINTS
;

DROP TABLE Procedure CASCADE CONSTRAINTS
;

DROP TABLE Protocol CASCADE CONSTRAINTS
;

DROP TABLE Protocol_Participant_Eligiblty CASCADE CONSTRAINTS
;

DROP TABLE Protocol_Status CASCADE CONSTRAINTS
;

DROP TABLE Qualitative_Evaluation CASCADE CONSTRAINTS
;

DROP TABLE Radiation CASCADE CONSTRAINTS
;

DROP TABLE Specimen CASCADE CONSTRAINTS
;

DROP TABLE Specimen_Collection CASCADE CONSTRAINTS
;

DROP TABLE Study_Agent CASCADE CONSTRAINTS
;

DROP TABLE Study_Investigator CASCADE CONSTRAINTS
;

DROP TABLE Study_Participant_Assignment CASCADE CONSTRAINTS
;

DROP TABLE Study_Site CASCADE CONSTRAINTS
;

DROP TABLE Study_Time_Point CASCADE CONSTRAINTS
;

DROP TABLE Substance_Administration CASCADE CONSTRAINTS
;

DROP TABLE Surgery CASCADE CONSTRAINTS
;


--  Create Tables 
CREATE TABLE Activity ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	name VARCHAR2(200),    --  Values include: Bone Scan, Colonoscopy, CAT Scan, etc. 
	type VARCHAR2(200),
	description_Text VARCHAR2(200),
	start_Date DATE,
	start_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	stop_Date DATE,
	stop_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	duration_Value NUMBER(12,2),
	duration_Value_orig VARCHAR2(200),    --  added to handle invalid values 
	duration_Unit_Of_Measure_Code VARCHAR2(200),    --  Values include: MN-Minutes, HR-Hours, DY-Days, etc. 
	planned_Indicator VARCHAR2(200),
	reason_Code VARCHAR2(200),    --  Values include: Diagnostic, Research, Treatment.  
        AGE_AT_VISIT                                       NUMBER(12,2),
        AGE_AT_VISIT_UNITS                                 VARCHAR2(200),
        PLANNED_DURATION                                   VARCHAR2(200),
        PLANNED_DURATION_DESCRIPTION                       VARCHAR2(200),
	SUBTYPE_CODE VARCHAR2(200),
	STUDY_PARTICIPANT_ASSIGNMNT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from STUDYPARTICIPANTASSIGNMENTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Activity.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Activity.name
    IS 'Values include: Bone Scan, Colonoscopy, CAT Scan, etc.'
;
COMMENT ON COLUMN Activity.start_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Activity.stop_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Activity.duration_Value_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Activity.duration_Unit_Of_Measure_Code
    IS 'Values include: MN-Minutes, HR-Hours, DY-Days, etc.'
;
COMMENT ON COLUMN Activity.reason_Code
    IS 'Values include: Diagnostic, Research, Treatment. '
;
COMMENT ON COLUMN Activity.STUDY_PARTICIPANT_ASSIGNMNT_ID
    IS 'Foreign key from STUDYPARTICIPANTASSIGNMENTS table.'
;
COMMENT ON COLUMN Activity.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Activity.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Activity.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Activity.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Activity_Relationship ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	type_Code VARCHAR2(200),    --  values such as, component, is sequel, etc. 
	sequence_Number NUMBER(12,2),
	comment_Text VARCHAR2(200),
	ACTIVITY_ID_1 NUMBER(12,2) NOT NULL,    --  Foreign key from ACTIVITIES table. 
	ACTIVITY_ID_2 NUMBER(12,2) NOT NULL,    --  Foreign key from ACTIVITIES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON TABLE Activity_Relationship
    IS '[Additional Documentation] In the particular case where the activities are analysis tasks, this is a verb phrase that specifies the semantic link between two Analysis_Tasks. [BRIDG] Examples: (1) specification that a particular value in the response to one Analysis_Task dictates navigation to another Analysis_Task (e.g., if analysis of the distribution of the data shows that it is not normally distributed, you would navigate to the non-parametric version of the statistical test) (2) the value of a response may be determined from the value of a set of other fields (e.g., the standard error of the mean is derived from the mean, the standard deviation and the sample size). (3) the behavior of a field for another Analysis_Task is determined by the value of a response (e.g., the choice of prior distribution changes your Bayesian model). [End Documentation]'
;
COMMENT ON COLUMN Activity_Relationship.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Activity_Relationship.type_Code
    IS 'values such as, component, is sequel, etc.'
;
COMMENT ON COLUMN Activity_Relationship.ACTIVITY_ID_1
    IS 'Foreign key from ACTIVITIES table.'
;
COMMENT ON COLUMN Activity_Relationship.ACTIVITY_ID_2
    IS 'Foreign key from ACTIVITIES table.'
;
COMMENT ON COLUMN Activity_Relationship.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Activity_Relationship.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Activity_Relationship.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Activity_Relationship.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Adverse_Event ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	onset_Date DATE,
	onset_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	resolved_Date DATE,
	resolved_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	ctc_Category_Code VARCHAR2(200),    --  Values include: Pain, Infection, Allergy/Immunology, etc. 
	ctc_Category_Code_System VARCHAR2(200),
	ctc_Term_Type_Code VARCHAR2(200),
	ctc_Term_Type_Code_System VARCHAR2(200),
	ctc_Attribution_Code VARCHAR2(200),    --  Values include: Definite, Possible, Probable, Unlikely, Unrelated	. 
	ctc_Attribution_Code_System VARCHAR2(200),
	ctc_Code VARCHAR2(200),     
	ctc_Code_System VARCHAR2(200),
	ctc_Grade_Code VARCHAR2(200),    --  Values include: 0-No Adverse Event Or Within Normal Limits, 1- Mild Adverse Event, 2- Moderate Adverse Event, 3- Severe and Undesirable Adverse Event, etc. 
	ctc_Grade_Code_System VARCHAR2(200),
	serious_Reason_Code VARCHAR2(200),    --  Values include: 1-No, 2-Life-Threatening, 3-Death, 4-Disability, etc. 
	outcome_Code VARCHAR2(200),    --  Values include: 1-Recovered, 2-Still Under Treatment/Observation, 3-Alive With Sequelae, 4-Died, etc. 
	action_Taken_Code VARCHAR2(200),    --  Values include: 2-Dose Reduced, 1-None, 3-Regimen Interrupted, 4-Therapy_Discontinued/Interrupted/ Reduced, etc. 
	condition_Pattern_Code VARCHAR2(200),    --  Values include: 1 single episode, 2 intermittent, 3 continuous. 
	dose_Limiting_Toxicity_Ind VARCHAR2(200),
	dose_Limiting_Tox_Descrptn_Txt VARCHAR2(200),
	description_Text VARCHAR2(200),
	filed_Indicator VARCHAR2(200),  -- added per change made by CTOM API or caCTUS project 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Adverse_Event.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Adverse_Event.onset_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Adverse_Event.resolved_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Adverse_Event.ctc_Category_Code
    IS 'Values include: Pain, Infection, Allergy/Immunology, etc.'
;
COMMENT ON COLUMN Adverse_Event.ctc_Attribution_Code
    IS 'Values include: Definite, Possible, Probable, Unlikely, Unrelated	.'
;
COMMENT ON COLUMN Adverse_Event.ctc_Grade_Code
    IS 'Values include: 0-No Adverse Event Or Within Normal Limits, 1- Mild Adverse Event, 2- Moderate Adverse Event, 3- Severe and Undesirable Adverse Event, etc.'
;
COMMENT ON COLUMN Adverse_Event.serious_Reason_Code
    IS 'Values include: 1-No, 2-Life-Threatening, 3-Death, 4-Disability, etc.'
;
COMMENT ON COLUMN Adverse_Event.outcome_Code
    IS 'Values include: 1-Recovered, 2-Still Under Treatment/Observation, 3-Alive With Sequelae, 4-Died, etc.'
;
COMMENT ON COLUMN Adverse_Event.action_Taken_Code
    IS 'Values include: 2-Dose Reduced, 1-None, 3-Regimen Interrupted, 4-Therapy_Discontinued/Interrupted/ Reduced, etc.'
;
COMMENT ON COLUMN Adverse_Event.condition_Pattern_Code
    IS 'Values include: 1 single episode, 2 intermittent, 3 continuous.'
;
COMMENT ON COLUMN Adverse_Event.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Adverse_Event.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Adverse_Event.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Adverse_Event.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Adverse_Event_Therapy ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	treatment_Date DATE,
	treatment_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	delay_Duration NUMBER(12,2),
	delay_Duration_orig VARCHAR2(200),    --  added to handle invalid values 
	delay_Duration_Uom_Code VARCHAR2(200),
	intensity_Code VARCHAR2(200),    --  Values include: None, Symptomatic, Supportive, Vigorous, Supportive. 
	ADVERSE_EVENT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from ADVERSEEVENTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Adverse_Event_Therapy.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Adverse_Event_Therapy.treatment_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Adverse_Event_Therapy.delay_Duration_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Adverse_Event_Therapy.intensity_Code
    IS 'Values include: None, Symptomatic, Supportive, Vigorous, Supportive.'
;
COMMENT ON COLUMN Adverse_Event_Therapy.ADVERSE_EVENT_ID
    IS 'Foreign key from ADVERSEEVENTS table.'
;
COMMENT ON COLUMN Adverse_Event_Therapy.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Adverse_Event_Therapy.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Adverse_Event_Therapy.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Adverse_Event_Therapy.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Agent ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	name VARCHAR2(200),
	description_Text VARCHAR2(200),
	status_Code VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Agent.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Agent.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Agent.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Agent.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Agent.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Agent_Occurrence ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	lot_Number VARCHAR2(200),
	form_Code VARCHAR2(200),
	expiration_Date DATE,
	expiration_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	AGENT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from AGENTS table. 
	SUBSTANCE_ADMINISTRATION_ID NUMBER(12,2) NOT NULL,    --  Foreign key from SUBSTANCEADMINISTRATIONS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Agent_Occurrence.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Agent_Occurrence.expiration_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Agent_Occurrence.AGENT_ID
    IS 'Foreign key from AGENTS table.'
;
COMMENT ON COLUMN Agent_Occurrence.SUBSTANCE_ADMINISTRATION_ID
    IS 'Foreign key from SUBSTANCEADMINISTRATIONS table.'
;
COMMENT ON COLUMN Agent_Occurrence.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Agent_Occurrence.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Agent_Occurrence.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Agent_Occurrence.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Assessment ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	evaluation_Date DATE,
	evaluation_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	SUBTYPE_CODE VARCHAR2(200),
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON TABLE Assessment
    IS ' 
--  '
;
COMMENT ON COLUMN Assessment.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Assessment.evaluation_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Assessment.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Assessment.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Assessment.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Assessment.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Assessment_Relationship ( 
	id NUMBER(12,2) NOT NULL,
	type_Code VARCHAR2(200),
	comment_Text VARCHAR2(200),
	ASSESSMENT_ID_1 NUMBER(12,2),    --  Foreign key from ASSESSMENTS table. 
	ASSESSMENT_ID_2 NUMBER(12,2) NOT NULL,    --  Foreign key from ASSESSMENTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Assessment_Relationship.ASSESSMENT_ID_1
    IS 'Foreign key from ASSESSMENTS table.'
;
COMMENT ON COLUMN Assessment_Relationship.ASSESSMENT_ID_2
    IS 'Foreign key from ASSESSMENTS table.'
;
COMMENT ON COLUMN Assessment_Relationship.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Assessment_Relationship.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Assessment_Relationship.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Assessment_Relationship.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Cancer_Stage ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	tnm_Stage VARCHAR2(200),
	tnm_Stage_Code_System VARCHAR2(200),
	stage_Code VARCHAR2(200),
	stage_Code_System VARCHAR2(200),
	DIAGNOSIS_ID NUMBER(12,2) NOT NULL,    --  Foreign key from DIAGNOSIS table 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Cancer_Stage.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Cancer_Stage.DIAGNOSIS_ID
    IS 'Foreign key from DIAGNOSIS table'
;
COMMENT ON COLUMN Cancer_Stage.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Cancer_Stage.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Cancer_Stage.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Cancer_Stage.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;


CREATE TABLE central_laboratory (
 ID                                                 NUMBER(12,2) NOT NULL,
 IDENTIFIER                                         VARCHAR2(200),
 NAME                                               VARCHAR2(200),
 SOURCE                                             VARCHAR2(200),
 SOURCE_EXTRACT_DATE                                DATE,
 CTOM_INSERT_DATE                                   DATE,
 CTOM_UPDATE_DATE                                   DATE
)
;


CREATE TABLE Clinical_Result ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	panel_Name VARCHAR2(200),
	value VARCHAR2(1000),
	value_Unit_Of_Measure_Code VARCHAR2(200),    --  [Additional Documentation] In case of  laboratory test results, this element maps to CDE Lab Unit Of Measure Name; public_ID 2003753; version 3.0. [End Documentation] 
	assay_Method_Code VARCHAR2(200),    --  Values include: ER-Estrogen Receptor Assay, PR-Progesterone Receptor Assay, p53 Assay, etc. 
	body_Position_Code VARCHAR2(200),    --  Values include: Unknown, Semiprone, Prone, Sitting, etc. 
	lab_Reference_Range_Code VARCHAR2(200),    --  Values include: Lower than reference range, High- greater than normal in degree or intensity or amount, Normal, etc 
	lab_Technique_Code VARCHAR2(200),    --  Values include: IHC-Immunohistochemistry, PCR- Polymerase Chain Reaction, Manual Differentiation, etc. 
	means_Vital_Status_Obtained_Cd VARCHAR2(200),    --  Values include: Conference notes, Hospital Information System (electronic transfer), Hard copy, etc. 
	normal_Abnormal_Indicator VARCHAR2(200),
	biomarker_Indicator VARCHAR2(200),
	significance_Indicator VARCHAR2(200),
 	ADDITIONAL_TEST_DESCRIPTION                        VARCHAR2(1000),
 	REFERENCE_FLAG                                     VARCHAR2(200),
 	NUMERIC_PRECISION                                  NUMBER(24,12),
 	NUMERIC_PRECISION_ORIG                             VARCHAR2(200),
 	REFERENCE_RANGE_LOW                                NUMBER(24,12),
 	REFERENCE_RANGE_LOW_ORIG                           VARCHAR2(200),
 	REFERENCE_RANGE_HIGH                               NUMBER(24,12),
 	REFERENCE_RANGE_HIGH_ORIG                          VARCHAR2(200),
 	REFERENCE_RANGE_COMMENT                            VARCHAR2(200),
 	REFERENCE_TEXT_LIST                                VARCHAR2(200),
 	LAB_TEST_CONCEPT_DESCRIPTOR_ID        /*NOT NULL*/ NUMBER(12,2),  -- temporarily commented out not null, will uncomment in CTOM 1.0
 	PERFORMING_LABORATORY_ID                           NUMBER(12,2),
 	VALUEUOM_CONCEPT_DESCRIPTOR_ID                     NUMBER(12,2),
	CONCEPT_DESCRIPTOR_ID NUMBER(12,2)/*NOT NULL*/,    --  Foreign key from CONCEPTDESCRIPTORS table. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Clinical_Result.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Clinical_Result.value_Unit_Of_Measure_Code
    IS '[Additional Documentation] In case of  laboratory test results, this element maps to CDE Lab Unit Of Measure Name; public_ID 2003753; version 3.0. [End Documentation]'
;
COMMENT ON COLUMN Clinical_Result.assay_Method_Code
    IS 'Values include: ER-Estrogen Receptor Assay, PR-Progesterone Receptor Assay, p53 Assay, etc.'
;
COMMENT ON COLUMN Clinical_Result.body_Position_Code
    IS 'Values include: Unknown, Semiprone, Prone, Sitting, etc.'
;
COMMENT ON COLUMN Clinical_Result.lab_Reference_Range_Code
    IS 'Values include: Lower than reference range, High- greater than normal in degree or intensity or amount, Normal, etc'
;
COMMENT ON COLUMN Clinical_Result.lab_Technique_Code
    IS 'Values include: IHC-Immunohistochemistry, PCR- Polymerase Chain Reaction, Manual Differentiation, etc.'
;
COMMENT ON COLUMN Clinical_Result.means_Vital_Status_Obtained_Cd
    IS 'Values include: Conference notes, Hospital Information System (electronic transfer), Hard copy, etc.'
;
COMMENT ON COLUMN Clinical_Result.CONCEPT_DESCRIPTOR_ID
    IS 'Foreign key from CONCEPTDESCRIPTORS table.'
;
COMMENT ON COLUMN Clinical_Result.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Clinical_Result.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Clinical_Result.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Clinical_Result.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Concept_Descriptor ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	code VARCHAR2(200),
	code_System VARCHAR2(200),
	code_System_Name VARCHAR2(200),
	code_System_Version NUMBER(12,2),
	display_Text VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Concept_Descriptor.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Concept_Descriptor.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Concept_Descriptor.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Concept_Descriptor.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Concept_Descriptor.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Death_Summary ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	death_Date DATE,
	death_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	death_Cause_Code VARCHAR2(200),    --  Values include: I-Infection, M-Malignant Disease, O-Other, T-Toxicity From Protocol Treatment. 
	death_Cause_Text VARCHAR(200),    --   
	autopsied_Indicator VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Death_Summary.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Death_Summary.death_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Death_Summary.death_Cause_Code
    IS 'Values include: I-Infection, M-Malignant Disease, O-Other, T-Toxicity From Protocol Treatment.'
;
COMMENT ON COLUMN Death_Summary.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Death_Summary.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Death_Summary.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Death_Summary.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Diagnosis ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	name VARCHAR2(200),
	disease_Diagnosis_Code VARCHAR2(200),
	disease_Diagnosis_Code_System VARCHAR2(200),
	age_At_Diagnosis NUMBER(12,2),
	age_At_Diagnosis_orig VARCHAR2(200),    --  added to handle invalid values 
	confirmation_Date DATE,
	confirmation_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	primary_Anatomic_Site_Code VARCHAR2(200),    --  Values include: Appendix, Bladder, Cervix, etc. 
	prim_Anatomic_Site_Code_System VARCHAR2(200),
	prim_Anatomic_Ste_Lateralty_Cd VARCHAR2(200),    --  Values include: Bilateral, Both, Left, Right, etc.  
	recurrence_Indicator VARCHAR2(200),
	disease_Status_Code VARCHAR2(200),    --  Values include: metastatic, disease free. 
	source_Code VARCHAR2(200),    --  Values Include: Pathology Report, Self-Report, etc. 
	source_Other VARCHAR2(200),
	disease_Extent_Text VARCHAR2(200),    --  [Additional Documentation] Definition of the extent of the disease in the body (e.g., in-situ, localized, invasion, regional, etc.) [End Documentation] 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Diagnosis.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Diagnosis.age_At_Diagnosis_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Diagnosis.confirmation_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Diagnosis.primary_Anatomic_Site_Code
    IS 'Values include: Appendix, Bladder, Cervix, etc.'
;
COMMENT ON COLUMN Diagnosis.prim_Anatomic_Ste_Lateralty_Cd
    IS 'Values include: Bilateral, Both, Left, Right, etc. '
;
COMMENT ON COLUMN Diagnosis.disease_Status_Code
    IS 'Values include: metastatic, disease free.'
;
COMMENT ON COLUMN Diagnosis.source_Code
    IS 'Values Include: Pathology Report, Self-Report, etc.'
;
COMMENT ON COLUMN Diagnosis.disease_Extent_Text
    IS '[Additional Documentation] Definition of the extent of the disease in the body (e.g., in-situ, localized, invasion, regional, etc.) [End Documentation]'
;
COMMENT ON COLUMN Diagnosis.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Diagnosis.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Diagnosis.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Diagnosis.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Disease_Response ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	response_Code VARCHAR2(200),    --  Values include: DU-Disease Unchanged, CR-Complete Response, etc. 
	response_Code_System VARCHAR2(200),
	best_Response_Code VARCHAR2(200),    --  Values include: CR-Complete Response, PD-Progressive Disease, etc. 
	best_Response_Date DATE,
	best_Response_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	progression_Date DATE,
	progression_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	progression_Period NUMBER(12,2),
	progression_Period_orig VARCHAR2(200),    --  added to handle invalid values 
	progression_Period_Uom_Cd VARCHAR2(200),
	dose_Change_Indicator_Code NUMBER(12,2),    --  Values include: 9-Unknown, 3-No, 1-Yes Planned, 2-Yes Unplanned. 
	dose_Change_Indicator_Cd_orig VARCHAR2(200),    --  added to handle invalid values 
	course_Disposition_Code VARCHAR2(200),    --  Values include: Completed, Discontinued. 
	comment_Text VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Disease_Response.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Disease_Response.response_Code
    IS 'Values include: DU-Disease Unchanged, CR-Complete Response, etc.'
;
COMMENT ON COLUMN Disease_Response.best_Response_Code
    IS 'Values include: CR-Complete Response, PD-Progressive Disease, etc.'
;
COMMENT ON COLUMN Disease_Response.best_Response_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Disease_Response.progression_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Disease_Response.progression_Period_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Disease_Response.dose_Change_Indicator_Code
    IS 'Values include: 9-Unknown, 3-No, 1-Yes Planned, 2-Yes Unplanned.'
;
COMMENT ON COLUMN Disease_Response.dose_Change_Indicator_Cd_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Disease_Response.course_Disposition_Code
    IS 'Values include: Completed, Discontinued.'
;
COMMENT ON COLUMN Disease_Response.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Disease_Response.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Disease_Response.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Disease_Response.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Eligibility_Checklist_Criteria ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	question_Number NUMBER(12,2),
	question_Number_orig VARCHAR2(200),    --  added to handle invalid values 
	expected_Answer_Indicator VARCHAR2(200),    --  Values include: Yes, No. 
	INCLUSION_EXCLUSION_TYPE VARCHAR2(200),
	ELIGIBILITY_CHECKLIST_ID NUMBER(12,2),    --  Foreign key from ELIGIBILITY_CHECKLIST table. 
	ELIGIBILITY_CRITERIA_ID NUMBER(12,2),    --  Foreign key column from ELIGIBILITY_CRITERIA table. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.question_Number_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.expected_Answer_Indicator
    IS 'Values include: Yes, No.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.ELIGIBILITY_CHECKLIST_ID
    IS 'Foreign key from ELIGIBILITY_CHECKLIST table.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.ELIGIBILITY_CRITERIA_ID
    IS 'Foreign key column from ELIGIBILITY_CRITERIA table.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Checklist_Criteria.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Eligibility_Criteria ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	question_Text VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Eligibility_Criteria.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Eligibility_Criteria.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Criteria.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Criteria.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Criteria.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Eligibility_Checklist ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	checklist_Number VARCHAR2(200),
	PROTOCOL_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PROTOCOL table. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Eligibility_Checklist.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Eligibility_Checklist.PROTOCOL_ID
    IS 'Foreign key from PROTOCOL table.'
;
COMMENT ON COLUMN Eligibility_Checklist.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Checklist.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Checklist.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Eligibility_Checklist.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Female_Reproductve_Charactrstc ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	first_Live_Birth_Age NUMBER(12,2),
	first_Live_Birth_Age_orig VARCHAR2(200),    --  added to handle invalid values 
	live_Birth_Count NUMBER(12,2),
	live_Birth_Count_orig VARCHAR2(200),    --  added to handle invalid values 
	still_Birth_Count NUMBER(12,2),
	still_Birth_Count_orig VARCHAR2(200),    --  added to handle invalid values 
	abortion_Indicator VARCHAR2(200),
	menopause_Start_Date DATE,
	menopause_Start_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	menopause_Age NUMBER(12,2),
	menopause_Age_orig VARCHAR2(200),    --  added to handle invalid values 
	menopause_Reason_Code VARCHAR2(200),    --  Values include:  Natural Menopause, Surgery Stopped Period, etc. 
	menopause_Reason_Other_Text VARCHAR2(200),
	PARTICIPANT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PARTICIPANTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.first_Live_Birth_Age_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.live_Birth_Count_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.still_Birth_Count_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.menopause_Start_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.menopause_Age_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.menopause_Reason_Code
    IS 'Values include:  Natural Menopause, Surgery Stopped Period, etc.'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.PARTICIPANT_ID
    IS 'Foreign key from PARTICIPANTS table.'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Female_Reproductve_Charactrstc.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Healthcare_Site ( 
	id NUMBER(12,2) NOT NULL,
	name VARCHAR2(200),
	description_Text VARCHAR2(200),
	status_Code VARCHAR2(200),
	status_Date DATE,
	status_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	street_Address VARCHAR2(200),
	city VARCHAR2(200),
	state_Code VARCHAR2(200),
	postal_Code VARCHAR2(200),
	country_Code VARCHAR2(200),
	telecom_Address VARCHAR2(200),
	nci_Institute_Code VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Healthcare_Site.status_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Healthcare_Site.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Healthcare_Site_Investigator ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	role_code VARCHAR2(200),
	INVESTIGATOR_ID NUMBER(12,2) NOT NULL,    --  Foreign key from INVESTIGATORS table. 
	HEALTHCARE_SITE_ID NUMBER(12,2) NOT NULL,    --  Foreign key from HEALTHCARESITES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Healthcare_Site_Investigator.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Healthcare_Site_Investigator.investigator_id
    IS 'Foreign key from INVESTIGATORS table.'
;
COMMENT ON COLUMN Healthcare_Site_Investigator.healthcare_site_id
    IS 'Foreign key from HEALTHCARE_SITES table.'
;
COMMENT ON COLUMN Healthcare_Site_Investigator.source
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Investigator.source_extract_date
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Investigator.ctom_insert_date
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Investigator.ctom_update_date
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Healthcare_Site_Prtcpnt ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	participant_Identifier VARCHAR2(200),
	HEALTHCARE_SITE_ID NUMBER(12,2) NOT NULL,    --  Foreign key from HEALTHCARESITES table. 
	PARTICIPANT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PARTICIPANTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.HEALTHCARE_SITE_ID
    IS 'Foreign key from HEALTHCARESITES table.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.PARTICIPANT_ID
    IS 'Foreign key from PARTICIPANTS table.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Healthcare_Site_Prtcpnt_Role ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	role_Code VARCHAR2(200),
	HEALTHCARE_SITE_PRTCPNT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from HEALTHCARESITEPARTICIPANTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt_Role.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt_Role.HEALTHCARE_SITE_PRTCPNT_ID
    IS 'Foreign key from HEALTHCARESITEPARTICIPANTS table.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt_Role.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt_Role.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt_Role.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Healthcare_Site_Prtcpnt_Role.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Histopathology ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	gross_Exam_Result_Code VARCHAR2(200),    --  Values include: Positive, Negative, Indeterminate, Not Done. 
	report_Descriptive_Text VARCHAR2(200),
	involved_Surgical_Margin_Ind VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Histopathology.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Histopathology.gross_Exam_Result_Code
    IS 'Values include: Positive, Negative, Indeterminate, Not Done.'
;
COMMENT ON COLUMN Histopathology.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Histopathology.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Histopathology.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Histopathology.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Histopathology_Grade ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	grade_Code VARCHAR2(200),
	grade_Code_System VARCHAR2(200),    --  Example: Nottingham. 
	comment_Text VARCHAR2(200),
	HISTOPATHOLOGY_ID NUMBER(12,2) NOT NULL,    --  Foreign key from HISTOPATHOLOGIES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Histopathology_Grade.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Histopathology_Grade.grade_Code_System
    IS 'Example: Nottingham.'
;
COMMENT ON COLUMN Histopathology_Grade.HISTOPATHOLOGY_ID
    IS 'Foreign key from HISTOPATHOLOGIES table.'
;
COMMENT ON COLUMN Histopathology_Grade.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Histopathology_Grade.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Histopathology_Grade.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Histopathology_Grade.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;


CREATE TABLE identifier (
 id                                           number(12,2),
 root                                         varchar2(200),
 extension                                    varchar2(200),
 assigning_authority_name                     varchar2(200),
 displayable_indicator                        varchar2(200),
 protocol_id                                  number(12,2),
 participant_id                               number(12,2),
 study_participant_assignmnt_id               number(12,2),
 source                                       varchar2(200),
 source_extract_date                          date,
 ctom_insert_date                             date,
 ctom_update_date                             date
)
;


CREATE TABLE Imaging ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	image_Identifier VARCHAR2(200),
	contrast_Agent_Enhancement_Ind VARCHAR2(200),    --  Values include: Not Applicable, No, Yes. 
	enhancement_Rate_Value NUMBER(12,2),
	enhancement_Rate_Value_orig VARCHAR2(200),    --  added to handle invalid values 
	enhancement_Description_Text VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Imaging.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Imaging.contrast_Agent_Enhancement_Ind
    IS 'Values include: Not Applicable, No, Yes.'
;
COMMENT ON COLUMN Imaging.enhancement_Rate_Value_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Imaging.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Imaging.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Imaging.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Imaging.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Investigator ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key 
	last_Name VARCHAR2(200),
	first_Name VARCHAR2(200),
	middle_Name VARCHAR2(200),
	birth_Date DATE,
	birth_Date_orig VARCHAR(200),    --  added to handle invalid values 
	telecom_Address VARCHAR2(200),
	administrative_Gender_Code VARCHAR2(200),    --  Values include: Female, Male, Unknown. - Keep until CTOM 1.0
	street_address VARCHAR2(200),
	city VARCHAR2(200),
	state VARCHAR2(200),
	zip_Code VARCHAR2(200),
	country_Code VARCHAR2(200),
	phone VARCHAR2(200),
	education_Level_Code VARCHAR2(200),    --  Values include: Less than High School Diploma, High School Diploma, Some College, etc. 
	ethnic_Group_Code VARCHAR2(200),    --  Values include: Hispanic Or Latino, Unknown, Not reported, Not Hispanic Or Latino. 
	household_Income_Code VARCHAR2(200),    --  Values include: Less than $25,000, $25,000 to $50,000, etc. 
	marital_Status_Code VARCHAR2(200),    --  Values include: Married, Widowed, Single, Separated, etc. 
	race_Code VARCHAR2(200),    --  Values include: Not Reported, Unknown, Asian, White, etc. - Keep until CTOM 1.0
	employment_Status_Code VARCHAR2(200),    --  Values include: Disabled, Employed, Homemaker, Retired, etc. 
	employment_Status_Other_Text VARCHAR2(200),
	nci_Identifier VARCHAR2(200),
	INITIALS                                           VARCHAR2(200),
	ADM_GNDR_CONCEPT_DESCRIPTOR_ID                     NUMBER(12,2),
	RACE_CONCEPT_DESCRIPTOR_ID                         NUMBER(12,2),
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Investigator.id
    IS 'System generated primary key'
;
COMMENT ON COLUMN Investigator.birth_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Investigator.administrative_Gender_Code
    IS 'Values include: Female, Male, Unknown.'
;
COMMENT ON COLUMN Investigator.education_Level_Code
    IS 'Values include: Less than High School Diploma, High School Diploma, Some College, etc.'
;
COMMENT ON COLUMN Investigator.ethnic_Group_Code
    IS 'Values include: Hispanic Or Latino, Unknown, Not reported, Not Hispanic Or Latino.'
;
COMMENT ON COLUMN Investigator.household_Income_Code
    IS 'Values include: Less than $25,000, $25,000 to $50,000, etc.'
;
COMMENT ON COLUMN Investigator.marital_Status_Code
    IS 'Values include: Married, Widowed, Single, Separated, etc.'
;
COMMENT ON COLUMN Investigator.race_Code
    IS 'Values include: Not Reported, Unknown, Asian, White, etc.'
;
COMMENT ON COLUMN Investigator.employment_Status_Code
    IS 'Values include: Disabled, Employed, Homemaker, Retired, etc.'
;
COMMENT ON COLUMN Investigator.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Investigator.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Investigator.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Investigator.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Lesion_Description ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	lesion_Number VARCHAR2(200),
	evaluation_Number NUMBER(12,2),
	evaluation_Number_orig VARCHAR2(200),    --  added to handle invalid values 
	appearance_Type_Code VARCHAR2(200),    --  Values include: Flat Lesion, Nodular Lesion.  
	target_Non_Target_Code VARCHAR2(200),    --  Values include: Target Lesion, Nontarget Lesion. 
	measurable_Indicator VARCHAR2(200),
	method_Code VARCHAR2(200),    --  Values include: PET scan, Gallium scan, etc. 
	x_Dimension NUMBER(12,2),
	x_Dimension_orig VARCHAR2(200),    --  added to handle invalid values 
	y_Dimension NUMBER(12,2),    --    
	y_Dimension_orig VARCHAR2(200),    --  added to handle invalid values 
	z_Dimension NUMBER(12,2),    --    
	z_Dimension_orig VARCHAR2(200),    --  added to handle invalid values  
	dimension_Product NUMBER(12,2),
	dimension_Product_orig VARCHAR2(200),    --  added to handle invalid values 
	anatomic_Site_Code VARCHAR2(200),
	anatomic_Site_Code_System VARCHAR2(200),
	contact_Anatomic_Site_Code VARCHAR2(200),
	contact_Anatomic_Ste_Cd_System VARCHAR2(200),
	previously_Irradiated_Site_Ind VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Lesion_Description.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Lesion_Description.evaluation_Number_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Lesion_Description.appearance_Type_Code
    IS 'Values include: Flat Lesion, Nodular Lesion. '
;
COMMENT ON COLUMN Lesion_Description.target_Non_Target_Code
    IS 'Values include: Target Lesion, Nontarget Lesion.'
;
COMMENT ON COLUMN Lesion_Description.method_Code
    IS 'Values include: PET scan, Gallium scan, etc.'
;
COMMENT ON COLUMN Lesion_Description.x_Dimension_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Lesion_Description.y_Dimension
    IS ' '
;
COMMENT ON COLUMN Lesion_Description.y_Dimension_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Lesion_Description.z_Dimension
    IS ' '
;
COMMENT ON COLUMN Lesion_Description.z_Dimension_orig
    IS 'added to handle invalid values '
;
COMMENT ON COLUMN Lesion_Description.dimension_Product_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Lesion_Description.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Lesion_Description.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Lesion_Description.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Lesion_Description.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Lesion_Evaluation ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	evaluation_Code VARCHAR2(200),    --  Values include: N-New, R-Resolved, etc. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Lesion_Evaluation.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Lesion_Evaluation.evaluation_Code
    IS 'Values include: N-New, R-Resolved, etc.'
;
COMMENT ON COLUMN Lesion_Evaluation.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Lesion_Evaluation.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Lesion_Evaluation.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Lesion_Evaluation.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;


-- The LAB_VIEWER_STATUS (formerly lv_adverse_events) table is used by the caXchange
-- Lab Viewer to track what things  have been submitted to caAERS or C3D in the
-- CTMSi/CCTS Suite applications.  It is at least for now literally part of the CTOM
-- model per se.
CREATE TABLE LAB_VIEWER_STATUS (
 ID                                                 NUMBER(12,2),
 ADVERSE_EVENT_INDICATOR                            VARCHAR2(200),
 ADVERSE_EVENT_SENT_DATE                            DATE,
 CDMS_INDICATOR                                     VARCHAR2(200),
 CDMS_SENT_DATE                                     DATE,
 CLINICAL_RESULT_ID                                 NUMBER(12,2),
 CTOM_INSERT_DATE                                   DATE,
 CTOM_UPDATE_DATE                                   DATE
)
;


CREATE TABLE Metastasis_Site ( 
	id NUMBER(12,2) NOT NULL,
	anatomic_Site_Code VARCHAR2(200),
	anatomic_Site_Code_System VARCHAR2(200),
	CANCER_STAGE_ID NUMBER(12,2) NOT NULL,    --  Foreign key from CANCERSTAGES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Metastasis_Site.CANCER_STAGE_ID
    IS 'Foreign key from CANCERSTAGES table.'
;
COMMENT ON COLUMN Metastasis_Site.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Metastasis_Site.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Metastasis_Site.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Metastasis_Site.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Neoplasm ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	cell_Type_Code VARCHAR2(200),
	HISTOPATHOLOGY_ID NUMBER(12,2) NOT NULL,    --  Foreign key from HISTOPATHOLOGIES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Neoplasm.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Neoplasm.HISTOPATHOLOGY_ID
    IS 'Foreign key from HISTOPATHOLOGIES table.'
;
COMMENT ON COLUMN Neoplasm.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Neoplasm.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Neoplasm.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Neoplasm.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Observation ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	reporting_Date DATE,    --  [Additional Documentation] The date the observation was reported. [End Documentation]  
	reporting_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	confidentiality_Code VARCHAR2(200),
	uncertainty_Code VARCHAR2(200),    --  [Additional Documentation] For example, a patient might have had a cholecystectomy procedure in the past (but isn''t sure). [End Documentation] 
	status_Code VARCHAR2(200),
 	COMMENTS                                           VARCHAR2(1000),
	SUBTYPE_CODE VARCHAR2(200),
	ACTIVITY_ID NUMBER(12,2),    --  Added foreign key column to Activity table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Observation.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Observation.reporting_Date
    IS '[Additional Documentation] The date the observation was reported. [End Documentation] '
;
COMMENT ON COLUMN Observation.reporting_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Observation.uncertainty_Code
    IS '[Additional Documentation] For example, a patient might have had a cholecystectomy procedure in the past (but isn''t sure). [End Documentation]'
;
COMMENT ON COLUMN Observation.ACTIVITY_ID
    IS 'Added foreign key column to Activity table.'
;
COMMENT ON COLUMN Observation.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Observation.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Observation.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Observation.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE OBSERVATION_ASSESSMENT ( 
	id NUMBER(12,2),    --  System generated primary key. 
	OBSERVATION_ID NUMBER(12,2) NOT NULL,    --  Foreign key from OBSERVATION table 
	ASSESSMENT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from ASSESSMENT table. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.OBSERVATION_ID
    IS 'Foreign key from OBSERVATION table'
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.ASSESSMENT_ID
    IS 'Foreign key from ASSESSMENT table.'
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN OBSERVATION_ASSESSMENT.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Observation_Relationship ( 
	id NUMBER(12,2) NOT NULL,
	type_Code VARCHAR2(200),
	comment_Text VARCHAR2(200),
	OBSERVATION_ID_1 NUMBER(12,2) NOT NULL,    --  Foreign key from OBSERVATIONS table. 
	OBSERVATION_ID_2 NUMBER(12,2) NOT NULL,    --  Foreign key from OBSERVATIONS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Observation_Relationship.OBSERVATION_ID_1
    IS 'Foreign key from OBSERVATIONS table.'
;
COMMENT ON COLUMN Observation_Relationship.OBSERVATION_ID_2
    IS 'Foreign key from OBSERVATIONS table.'
;
COMMENT ON COLUMN Observation_Relationship.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Observation_Relationship.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Observation_Relationship.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Observation_Relationship.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Participant ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	last_Name VARCHAR2(200),
	first_Name VARCHAR2(200),
	middle_Name VARCHAR2(200),
	birth_Date DATE,
	birth_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	telecom_Address VARCHAR2(200),
	administrative_Gender_Code VARCHAR2(200),    --  Values include: Female, Male, Unknown. - Keep until CTOM 1.0
	street_address VARCHAR2(200),
	city VARCHAR2(200),
	state VARCHAR2(200),
	zip_Code VARCHAR2(200),
	country_Code VARCHAR2(200),
	phone VARCHAR2(200),
	education_Level_Code VARCHAR2(200),    --  Values include: Less than High School Diploma, High School Diploma, Some College, etc. 
	ethnic_Group_Code VARCHAR2(200),    --  Values include: Hispanic Or Latino, Unknown, Not reported, Not Hispanic Or Latino. 
	household_Income_Code VARCHAR2(200),    --  Values include: Less than $25,000, $25,000 to $50,000, etc. 
	marital_Status_Code VARCHAR2(200),    --  Values include: Married, Widowed, Single, Separated, etc. 
	race_Code VARCHAR2(200),    --  Values include: Not Reported, Unknown, Asian, White, etc. - Keep until CTOM 1.0
	employment_Status_Code VARCHAR2(200),    --  Values include: Disabled, Employed, Homemaker, Retired, etc. 
	employment_Status_Other_Text VARCHAR2(200),
	initials VARCHAR2(200),    --  [Additional Documentation] NOTE: This should be considered as identifying information and should not be part of research database --(Still TBD). [End Documentation] 
	payment_Method_Code VARCHAR2(200),    --  Values include: 1-Private Insurance, 2-Medicare, 3- Medicare And Private Insurance, 4-Medicaid, etc.  
	confidentiality_Indicator VARCHAR2(200),
	ADM_GNDR_CONCEPT_DESCRIPTOR_ID                     NUMBER(12,2),
	RACE_CONCEPT_DESCRIPTOR_ID                         NUMBER(12,2),
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Participant.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Participant.birth_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Participant.administrative_Gender_Code
    IS 'Values include: Female, Male, Unknown.'
;
COMMENT ON COLUMN Participant.education_Level_Code
    IS 'Values include: Less than High School Diploma, High School Diploma, Some College, etc.'
;
COMMENT ON COLUMN Participant.ethnic_Group_Code
    IS 'Values include: Hispanic Or Latino, Unknown, Not reported, Not Hispanic Or Latino.'
;
COMMENT ON COLUMN Participant.household_Income_Code
    IS 'Values include: Less than $25,000, $25,000 to $50,000, etc.'
;
COMMENT ON COLUMN Participant.marital_Status_Code
    IS 'Values include: Married, Widowed, Single, Separated, etc.'
;
COMMENT ON COLUMN Participant.race_Code
    IS 'Values include: Not Reported, Unknown, Asian, White, etc.'
;
COMMENT ON COLUMN Participant.employment_Status_Code
    IS 'Values include: Disabled, Employed, Homemaker, Retired, etc.'
;
COMMENT ON COLUMN Participant.initials
    IS '[Additional Documentation] NOTE: This should be considered as identifying information and should not be part of research database --(Still TBD). [End Documentation]'
;
COMMENT ON COLUMN Participant.payment_Method_Code
    IS 'Values include: 1-Private Insurance, 2-Medicare, 3- Medicare And Private Insurance, 4-Medicaid, etc. '
;
COMMENT ON COLUMN Participant.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Participant.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Participant.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Participant.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Participant_Eligibility_Answer ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	answer_Text VARCHAR2(200),
	ELIGIBILITY_CHECKLIST_CRITR_ID NUMBER(12,2) NOT NULL,    --  Foreign key from ELIGIBILITY_CHECKLIST_CRITERIA table. 
	PARTICIPANT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PARTICIPANTS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Participant_Eligibility_Answer.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Participant_Eligibility_Answer.ELIGIBILITY_CHECKLIST_CRITR_ID
    IS 'Foreign key from ELIGIBILITY_CHECKLIST_CRITERIA table.'
;
COMMENT ON COLUMN Participant_Eligibility_Answer.PARTICIPANT_ID
    IS 'Foreign key from PARTICIPANTS table.'
;
COMMENT ON COLUMN Participant_Eligibility_Answer.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Participant_Eligibility_Answer.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Participant_Eligibility_Answer.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Participant_Eligibility_Answer.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;


CREATE TABLE performing_laboratory (
 ID                                                 NUMBER(12,2) NOT NULL,
 IDENTIFIER                                         VARCHAR2(200),
 NAME                                               VARCHAR2(200),
 SOURCE                                             VARCHAR2(200),
 SOURCE_EXTRACT_DATE                                DATE,
 CTOM_INSERT_DATE                                   DATE,
 CTOM_UPDATE_DATE                                   DATE
)
;


CREATE TABLE Person_Occupation ( 
	id NUMBER(12,2) NOT NULL,
	primary_Type_Code VARCHAR2(200),    --  [Additional Documentation] www.osha.gov/cgi-bin/sic/sicser5 - This is paired with Occupation Primary-Industry. 4 Digit SIC Codes. [End Documentation] 
	primary_Type_Code_System VARCHAR2(200),
	start_Date DATE,
	start_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	stop_Date DATE,
	stop_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	PERSON_ID NUMBER(12,2),    --  Foreign key value from INVESTIGATORS or PARTICIPANTS table. (no foreign key constraint exists) 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Person_Occupation.primary_Type_Code
    IS '[Additional Documentation] www.osha.gov/cgi-bin/sic/sicser5 - This is paired with Occupation Primary-Industry. 4 Digit SIC Codes. [End Documentation]'
;
COMMENT ON COLUMN Person_Occupation.start_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Person_Occupation.stop_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Person_Occupation.PERSON_ID
    IS 'Foreign key value from INVESTIGATORS or PARTICIPANTS table. (no foreign key constraint exists)'
;
COMMENT ON COLUMN Person_Occupation.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Person_Occupation.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Person_Occupation.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Person_Occupation.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Procedure ( 
	id NUMBER(12,2) NOT NULL,
	anatomic_Site_Code VARCHAR2(200),
	anatomic_Site_Code_System VARCHAR2(200),
	 FASTING_STATUS                                     VARCHAR2(200),
	SUBTYPE_CODE VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Procedure.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Procedure.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Procedure.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Procedure.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Protocol ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	nci_Identifier VARCHAR2(200),
	amendment_Identifier NUMBER(12,2),
	amendment_Identifier_orig VARCHAR2(200),    --  added to handle invalid values 
	amendment_Date DATE,
	amendment_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	navy_Nci_Identifier VARCHAR2(200),
	long_Title_Text VARCHAR2(500),
	short_Title_Text VARCHAR2(200),    --  [Additional Documentation] A name or abbreviated title by which the document is known. [BRIDG] [End Documentation] 
	precis_Text VARCHAR2(200),
	description_Text VARCHAR2(200),
	disease_Code VARCHAR2(200),    --  Values Include: A-AIDS, B-Benign, C-Cancer. 
	intent_Code VARCHAR2(200),    --  Values include: D-Diagnostic Protocol, GN-Genetic Non-therapeutic Protocol, etc. 
	monitor_Code VARCHAR2(200),    --  Values include: CTEP, CTEP-CTMS, CTEP-CDUS Complete, etc. 
	phase_Code VARCHAR2(200),    --  Values include: I, I/II, II, III, NA. 
	sponsor_Code VARCHAR2(200),    --  Values include: AB-Abbott Labs, AL-Alkermes, Inc., APH- Angiotech, AM- Amgen, etc. 
	blinded_Indicator VARCHAR2(200),
	multi_Institution_Indicator VARCHAR2(200),
	randomized_Indicator VARCHAR2(200),
	target_Accrual_Number NUMBER(12,2),
	target_Accrual_Number_orig VARCHAR2(200),    --  added to handle invalid values 
	identifier_assigning_authority varchar2(200), 
	document_uri VARCHAR2(200),    --  The location of the protocol document 
	sponsor_monitor VARCHAR2(200),    --  The organizational entity that will be monitoring the execution of the study.  For example, CTEP, DCP, a pharma company 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_USER VARCHAR2(200), --  Added audit column for data tracking.
	CTOM_UPDATE_USER VARCHAR2(200) --  Added audit column for data tracking.
) 
;
COMMENT ON TABLE Protocol
    IS '[Additional Documentation] A systematic evaluation of an observation or an intervention (for example, treatment, drug, device, procedure or system) in one or more subjects. Frequently this is a test of a particular hypothesis about the treatment, drug, device, procedure or system. [CDAM]  A study can be either primary or correlative. A study is considered a primary study if it has one or more correlative studies. A correlative study extends the objectives or observations of a primary study, enrolling the same, or a subset of the same, subjects as the primary study. A Clinical Trial is a Study with type= "intervention" with subjects of type="human". [BRIDG] [End Documentation]'
;
COMMENT ON COLUMN Protocol.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Protocol.amendment_Identifier_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Protocol.amendment_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Protocol.short_Title_Text
    IS '[Additional Documentation] A name or abbreviated title by which the document is known. [BRIDG] [End Documentation]'
;
COMMENT ON COLUMN Protocol.disease_Code
    IS 'Values Include: A-AIDS, B-Benign, C-Cancer.'
;
COMMENT ON COLUMN Protocol.intent_Code
    IS 'Values include: D-Diagnostic Protocol, GN-Genetic Non-therapeutic Protocol, etc.'
;
COMMENT ON COLUMN Protocol.monitor_Code
    IS 'Values include: CTEP, CTEP-CTMS, CTEP-CDUS Complete, etc.'
;
COMMENT ON COLUMN Protocol.phase_Code
    IS 'Values include: I, I/II, II, III, NA.'
;
COMMENT ON COLUMN Protocol.sponsor_Code
    IS 'Values include: AB-Abbott Labs, AL-Alkermes, Inc., APH- Angiotech, AM- Amgen, etc.'
;
COMMENT ON COLUMN Protocol.target_Accrual_Number_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Protocol.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Protocol_Participant_Eligiblty ( 
	id NUMBER(12,2) NOT NULL,
	eligible_Indicator VARCHAR2(200),
	ineligibility_Reason_Text VARCHAR2(200),
	eligibility_Waiver_Reason_Text VARCHAR2(200),
	PROTOCOL_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PROTOCOLS table. 
	PARTICIPANT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PARTICIPANTS table. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Protocol_Participant_Eligiblty.PROTOCOL_ID
    IS 'Foreign key from PROTOCOLS table.'
;
COMMENT ON COLUMN Protocol_Participant_Eligiblty.PARTICIPANT_ID
    IS 'Foreign key from PARTICIPANTS table.'
;
COMMENT ON COLUMN Protocol_Participant_Eligiblty.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol_Participant_Eligiblty.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol_Participant_Eligiblty.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol_Participant_Eligiblty.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Protocol_Status ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	status_Code VARCHAR2(200),    --  Values include: C-Closed, O-Open, S-Suspended, T-Terminated.  
	status_Date DATE,    --    
	status_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	PROTOCOL_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PROTOCOLS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Protocol_Status.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Protocol_Status.status_Code
    IS 'Values include: C-Closed, O-Open, S-Suspended, T-Terminated. '
;
COMMENT ON COLUMN Protocol_Status.status_Date
    IS ' '
;
COMMENT ON COLUMN Protocol_Status.status_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Protocol_Status.PROTOCOL_ID
    IS 'Foreign key from PROTOCOLS table.'
;
COMMENT ON COLUMN Protocol_Status.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol_Status.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol_Status.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Protocol_Status.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Qualitative_Evaluation ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	survival_Status_Code VARCHAR2(200),    --  Values include: 3-Alive Disease Status Unknown, 1-Alive With Disease, 2-Alive With No Evidence Of Disease, 5-Died, 4-Unknown. 
	survival_Status_Descriptin_Txt VARCHAR2(200),
	performance_Status_Code VARCHAR2(200),    --  Values include: 100 Normal, 90 Able to carry on normal activity, 80 Normal activity with effort, 70 Cares for self, etc. 
	performance_Status_Code_System VARCHAR2(200),
	pain_Index_Code VARCHAR2(200),
	pain_Index_Code_System VARCHAR2(200),
	anam_Result_Accuracy_Percent NUMBER(12,2),
	anam_Result_Accurcy_Prcnt_orig VARCHAR2(200),    --  added to handle invalid values 
	menstrual_Pattern_Type_Code VARCHAR2(200),    --  Values include: Always Regular, Never Regular, Usually Regular. 
	menstrual_Indicator VARCHAR2(200),    --  Values include: Yes, No. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Qualitative_Evaluation.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Qualitative_Evaluation.survival_Status_Code
    IS 'Values include: 3-Alive Disease Status Unknown, 1-Alive With Disease, 2-Alive With No Evidence Of Disease, 5-Died, 4-Unknown.'
;
COMMENT ON COLUMN Qualitative_Evaluation.performance_Status_Code
    IS 'Values include: 100 Normal, 90 Able to carry on normal activity, 80 Normal activity with effort, 70 Cares for self, etc.'
;
COMMENT ON COLUMN Qualitative_Evaluation.anam_Result_Accurcy_Prcnt_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Qualitative_Evaluation.menstrual_Pattern_Type_Code
    IS 'Values include: Always Regular, Never Regular, Usually Regular.'
;
COMMENT ON COLUMN Qualitative_Evaluation.menstrual_Indicator
    IS 'Values include: Yes, No.'
;
COMMENT ON COLUMN Qualitative_Evaluation.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Qualitative_Evaluation.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Qualitative_Evaluation.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Qualitative_Evaluation.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Radiation ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	dose VARCHAR2(200),
	dose_Unit_Of_Measure_Code VARCHAR2(200),    --  Values include: Gray, Centigray, Radiation Absorbed Dose. 
	schedule_Text VARCHAR2(200),
	therapy_Extent_Code VARCHAR2(200),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Radiation.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Radiation.dose_Unit_Of_Measure_Code
    IS 'Values include: Gray, Centigray, Radiation Absorbed Dose.'
;
COMMENT ON COLUMN Radiation.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Radiation.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Radiation.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Radiation.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Specimen ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	sample_Identifier NUMBER(12,2),
	sample_Identifier_orig VARCHAR2(200),    --  added to handle invalid values 
	sample_Type_Code VARCHAR2(200),    --  Values include: V-Saliva, A-Aphaeresis Cells, B-Whole Blood, C-CSF, etc. 
	volume NUMBER(12,2),
	volume_orig VARCHAR2(200),    --  added to handle invalid values 
	volume_Unit_Of_Measure_Code VARCHAR2(200),
	 ACCESSION_NUMBER                                   VARCHAR2(200),
	 CONDITION                                          VARCHAR2(200),
	 COMMENTS_FROM_LABORATORY                           VARCHAR2(1000),
 	COMMENTS_FROM_INVESTIGATOR                         VARCHAR2(1000),
 	SMPLTYPE_CONCEPT_DESCRIPTOR_ID                     NUMBER(12,2),
	SPECIMEN_COLLECTION_ID NUMBER(12,2) NOT NULL,    --  Foreign key from SPECIMENCOLLECTIONS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Specimen.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Specimen.sample_Identifier_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Specimen.sample_Type_Code
    IS 'Values include: V-Saliva, A-Aphaeresis Cells, B-Whole Blood, C-CSF, etc.'
;
COMMENT ON COLUMN Specimen.volume_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Specimen.SPECIMEN_COLLECTION_ID
    IS 'Foreign key from SPECIMENCOLLECTIONS table.'
;
COMMENT ON COLUMN Specimen.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Specimen.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Specimen.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Specimen.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Specimen_Collection ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	site_Condition_Code VARCHAR2(200),    --  Values include: Normal or Abnormal. 
	method_Code VARCHAR(200),    --  Values include: Abdominal/ ascites effusion, Biopsy, Bronchial alveolar lavage (BAL), etc. 
 	CENTRAL_LABORATORY_ID                          NUMBER(12,2),
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON TABLE Specimen_Collection
    IS ' 
--  '
;
COMMENT ON COLUMN Specimen_Collection.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Specimen_Collection.site_Condition_Code
    IS 'Values include: Normal or Abnormal.'
;
COMMENT ON COLUMN Specimen_Collection.method_Code
    IS 'Values include: Abdominal/ ascites effusion, Biopsy, Bronchial alveolar lavage (BAL), etc.'
;
COMMENT ON COLUMN Specimen_Collection.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Specimen_Collection.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Specimen_Collection.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Specimen_Collection.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Study_Agent ( 
	id NUMBER(12,2) NOT NULL,
	investigational_Indicator VARCHAR2(200),
	investigational_New_Drug_Id VARCHAR2(200),
	status_Code VARCHAR2(200),
	status_Date DATE,
	status_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	AGENT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from AGENTS table. 
	PROTOCOL_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PROTOCOLS table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Study_Agent.status_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Agent.AGENT_ID
    IS 'Foreign key from AGENTS table.'
;
COMMENT ON COLUMN Study_Agent.PROTOCOL_ID
    IS 'Foreign key from PROTOCOLS table.'
;
COMMENT ON COLUMN Study_Agent.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Agent.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Agent.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Agent.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Study_Investigator ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	responsibility_Role_Code VARCHAR2(200),    --  Examples include: Primary Investigator, Co-Investigator, etc. 
	start_Date DATE,
	start_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	stop_Date DATE,
	stop_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	status_Code VARCHAR2(200),
	signature_Indicator VARCHAR2(200),    --  [Additional Documentation] A code specifying whether and how the participant has attested his participation through a signature and or whether such a signature is needed. [BRIDG] [End Documentation] 
	signature_Text VARCHAR2(200),    --  [Additional Documentation] A textual or multimedia depiction of the signature by which the participant endorses his or her participation in the Act as specified in the Participation.type_Code and that he or she agrees to assume the associated accountability. [BRIDG] [End Documentation] 
	PROTOCOL_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PROTOCOLS table. 
	INVESTIGATOR_ID NUMBER(12,2) NOT NULL,    --  Foreign key from INVESTIGATOR table. 
        STUDY_SITE_ID NUMBER(12,2), -- Foreign key from STUDY_SITE_table. PROBABLY A TEMPORARY ADDITION
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Study_Investigator.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Study_Investigator.responsibility_Role_Code
    IS 'Examples include: Primary Investigator, Co-Investigator, etc.'
;
COMMENT ON COLUMN Study_Investigator.start_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Investigator.stop_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Investigator.signature_Indicator
    IS '[Additional Documentation] A code specifying whether and how the participant has attested his participation through a signature and or whether such a signature is needed. [BRIDG] [End Documentation]'
;
COMMENT ON COLUMN Study_Investigator.signature_Text
    IS '[Additional Documentation] A textual or multimedia depiction of the signature by which the participant endorses his or her participation in the Act as specified in the Participation.type_Code and that he or she agrees to assume the associated accountability. [BRIDG] [End Documentation]'
;
COMMENT ON COLUMN Study_Investigator.PROTOCOL_ID
    IS 'Foreign key from PROTOCOLS table.'
;
COMMENT ON COLUMN Study_Investigator.INVESTIGATOR_ID
    IS 'Foreign key from INVESTIGATORS table.'
;
COMMENT ON COLUMN Study_Investigator.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Investigator.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Investigator.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Investigator.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Study_Participant_Assignment ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	study_Participant_Identifier NUMBER(12,2),
	study_Participant_Identfr_orig VARCHAR2(200),    --  added to handle invalid values 
	arm_Identifier VARCHAR2(200),    --  [Additional Documentation] NOTE:  When the epoch_Name is "Prior" or "Baseline" -- the arm value will be defaulted to NULL. [End Documentation] 
	subgroup_Code VARCHAR2(200),
	informed_Consent_Frm_Signed_Dt DATE,
	informd_Cnsnt_Frm_Sgnd_Dt_orig VARCHAR2(200),    --  added to handle invalid values 
	enrollment_Age NUMBER(12,2),
	enrollment_Age_orig VARCHAR2(200),    --  added to handle invalid values 
	study_Agent_Dose_Level NUMBER(12,2),
	study_Agent_Dose_Level_orig VARCHAR2(200),    --  added to handle invalid values 
	study_Agent_Dose_Level_Uom_Cd VARCHAR2(200),
	off_Study_Date DATE,
	off_Study_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	off_Study_Reason_Code VARCHAR2(200),    --  Added for CTMS requirement 
	off_Study_Reason_Other_Text VARCHAR2(200),
 	TYPE                                               VARCHAR2(200),
	PARTICIPANT_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PARTICIPANTS table. 
	STUDY_SITE_ID NUMBER(12,2) NOT NULL,    --  Foreign key from STUDYSITES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Study_Participant_Assignment.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Study_Participant_Assignment.study_Participant_Identfr_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Participant_Assignment.arm_Identifier
    IS '[Additional Documentation] NOTE:  When the epoch_Name is "Prior" or "Baseline" -- the arm value will be defaulted to NULL. [End Documentation]'
;
COMMENT ON COLUMN Study_Participant_Assignment.informd_Cnsnt_Frm_Sgnd_Dt_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Participant_Assignment.enrollment_Age_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Participant_Assignment.study_Agent_Dose_Level_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Participant_Assignment.off_Study_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Participant_Assignment.off_Study_Reason_Code
    IS 'Added for CTMS requirement'
;
COMMENT ON COLUMN Study_Participant_Assignment.PARTICIPANT_ID
    IS 'Foreign key from PARTICIPANTS table.'
;
COMMENT ON COLUMN Study_Participant_Assignment.STUDY_SITE_ID
    IS 'Foreign key from STUDYSITES table.'
;
COMMENT ON COLUMN Study_Participant_Assignment.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Participant_Assignment.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Participant_Assignment.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Participant_Assignment.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Study_Site ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	role_Code VARCHAR2(200),    --  Examples include: Lead organization, participating organization, etc. 
	status_Code VARCHAR2(200),
	target_Accrual_Number VARCHAR2(200),
	start_Date DATE,
	start_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	stop_Date DATE,
	stop_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	irb_Approval_Date DATE,
	irb_Approval_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	local_protocol_identifier VARCHAR2(200),    --  The identifier used by the local site to identify a protocol  
	HEALTHCARE_SITE_ID NUMBER(12,2) NOT NULL,    --  Foreign key from HEALTHCARESITES table. 
	PROTOCOL_ID NUMBER(12,2) NOT NULL,    --  Foreign key from PROTOCOLS Table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Study_Site.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Study_Site.role_Code
    IS 'Examples include: Lead organization, participating organization, etc.'
;
COMMENT ON COLUMN Study_Site.start_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Site.stop_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Site.irb_Approval_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Site.HEALTHCARE_SITE_ID
    IS 'Foreign key from HEALTHCARESITES table.'
;
COMMENT ON COLUMN Study_Site.PROTOCOL_ID
    IS 'Foreign key from PROTOCOLS Table.'
;
COMMENT ON COLUMN Study_Site.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Site.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Site.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Site.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Study_Time_Point ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	visit_Name VARCHAR2(200),
	course_Number NUMBER(12,2),
	course_Number_orig VARCHAR(200),    --  added to handle invalid values 
	epoch_Name VARCHAR2(200),    --  Values include: Baseline, Screening, Run-in, Treatment, Follow-Up, etc. 
--  NOTE: When pre-study or medical history information is collected -- the epoch would be "Pre-Study";  relevant attributes in Activity, Observation and Assessment will be defaulted accordingly.  
	course_Start_Date DATE,
	course_Start_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	course_Stop_Date DATE,
	course_Stop_Date_orig VARCHAR2(200),    --  added to handle invalid values 
	ACTIVITY_ID NUMBER(12,2) NOT NULL,    --  Foreign key from ACTIVITIES table. 
	SECURITY_KEY NUMBER,    --  Added column per CTOMAPI project security scheme. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Study_Time_Point.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Study_Time_Point.course_Number_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Time_Point.epoch_Name
    IS 'Values include: Baseline, Screening, Run-in, Treatment, Follow-Up, etc. 
--  NOTE: When pre-study or medical history information is collected -- the epoch would be "Pre-Study";  relevant attributes in Activity, Observation and Assessment will be defaulted accordingly. '
;
COMMENT ON COLUMN Study_Time_Point.course_Start_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Time_Point.course_Stop_Date_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Study_Time_Point.ACTIVITY_ID
    IS 'Foreign key from ACTIVITIES table.'
;
COMMENT ON COLUMN Study_Time_Point.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Time_Point.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Time_Point.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Study_Time_Point.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Substance_Administration ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	single_Dose NUMBER(12,2),
	single_Dose_orig VARCHAR2(200),    --  added to handle invalid values 
	single_Dose_Unit_Of_Measure_Cd VARCHAR2(200),
	dose_Frequency_Code VARCHAR2(200),    --  Values include: Daily, Weekly, Monthly, Yearly, etc. 
	dose_Frequency_Text VARCHAR2(200),
	total_Dose NUMBER(12,2),
	total_Dose_orig VARCHAR2(200),    --  added to handle invalid values 
	total_Dose_Unit_Of_Measure_Cd VARCHAR2(200),
	dose_Change_Code VARCHAR2(200),    --  Values include: Agent Added, Agent Dose Decreased, Agent Dose Increased, etc. 
	dose_Change_Indicator_Code NUMBER(12,2),    --  Values include: 9-Unknown, 3-No, 1-Yes Planned, 2-Yes Unplanned. 
	dose_Change_Indicator_Cd_orig VARCHAR2(200),    --  added to handle invalid values 
	route_Code VARCHAR2(200),    --  Values include:  Gastrostomy Tube, CIV- Continuous Intravenous Infusion, IA- Intra-Arterial, etc. 
	AGENT_ID NUMBER(12,2),    --  Foreign key from AGENTS table. 
	STUDY_AGENT_ID NUMBER(12,2),    --  Foreign key from STUDYAGENTS table. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Substance_Administration.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Substance_Administration.single_Dose_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Substance_Administration.dose_Frequency_Code
    IS 'Values include: Daily, Weekly, Monthly, Yearly, etc.'
;
COMMENT ON COLUMN Substance_Administration.total_Dose_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Substance_Administration.dose_Change_Code
    IS 'Values include: Agent Added, Agent Dose Decreased, Agent Dose Increased, etc.'
;
COMMENT ON COLUMN Substance_Administration.dose_Change_Indicator_Code
    IS 'Values include: 9-Unknown, 3-No, 1-Yes Planned, 2-Yes Unplanned.'
;
COMMENT ON COLUMN Substance_Administration.dose_Change_Indicator_Cd_orig
    IS 'added to handle invalid values'
;
COMMENT ON COLUMN Substance_Administration.route_Code
    IS 'Values include:  Gastrostomy Tube, CIV- Continuous Intravenous Infusion, IA- Intra-Arterial, etc.'
;
COMMENT ON COLUMN Substance_Administration.AGENT_ID
    IS 'Foreign key from AGENTS table.'
;
COMMENT ON COLUMN Substance_Administration.STUDY_AGENT_ID
    IS 'Foreign key from STUDYAGENTS table.'
;
COMMENT ON COLUMN Substance_Administration.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Substance_Administration.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Substance_Administration.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Substance_Administration.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;

CREATE TABLE Surgery ( 
	id NUMBER(12,2) NOT NULL,    --  System generated primary key. 
	SOURCE VARCHAR2(200),    --  Added audit column for data tracking. 
	SOURCE_EXTRACT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_INSERT_DATE DATE,    --  Added audit column for data tracking. 
	CTOM_UPDATE_DATE DATE    --  Added audit column for data tracking. 
) 
;
COMMENT ON COLUMN Surgery.id
    IS 'System generated primary key.'
;
COMMENT ON COLUMN Surgery.SOURCE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Surgery.SOURCE_EXTRACT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Surgery.CTOM_INSERT_DATE
    IS 'Added audit column for data tracking.'
;
COMMENT ON COLUMN Surgery.CTOM_UPDATE_DATE
    IS 'Added audit column for data tracking.'
;


--  Create Primary Key Constraints 
ALTER TABLE Activity ADD CONSTRAINT PK_Activity 
PRIMARY KEY (id) 
;

ALTER TABLE Activity_Relationship ADD CONSTRAINT PK_Activity_Relationship 
PRIMARY KEY (id) 
;

ALTER TABLE Adverse_Event ADD CONSTRAINT PK_Adverse_Event 
PRIMARY KEY (id) 
;

ALTER TABLE Adverse_Event_Therapy ADD CONSTRAINT PK_Adverse_Event_Therapy 
PRIMARY KEY (id) 
;

ALTER TABLE Agent ADD CONSTRAINT PK_Agent 
PRIMARY KEY (id) 
;

ALTER TABLE Agent_Occurrence ADD CONSTRAINT PK_Agent_Occurrence 
PRIMARY KEY (id) 
;

ALTER TABLE Assessment ADD CONSTRAINT PK_Assessment 
PRIMARY KEY (id) 
;

ALTER TABLE Assessment_Relationship ADD CONSTRAINT PK_Assessment_Relationship 
PRIMARY KEY (id) 
;

ALTER TABLE Cancer_Stage ADD CONSTRAINT PK_Cancer_Stage 
PRIMARY KEY (id) 
;

ALTER TABLE Clinical_Result ADD CONSTRAINT PK_Clinical_Result 
PRIMARY KEY (id) 
;

ALTER TABLE Concept_Descriptor ADD CONSTRAINT PK_Concept_Descriptor 
PRIMARY KEY (id) 
;

ALTER TABLE Death_Summary ADD CONSTRAINT PK_Death_Summary 
PRIMARY KEY (id) 
;

ALTER TABLE Diagnosis ADD CONSTRAINT PK_Diagnosis 
PRIMARY KEY (id) 
;

ALTER TABLE Disease_Response ADD CONSTRAINT PK_Disease_Response 
PRIMARY KEY (id) 
;

ALTER TABLE Eligibility_Checklist_Criteria ADD CONSTRAINT PK_Eligibility_Checklist_Critr 
PRIMARY KEY (id) 
;

ALTER TABLE Eligibility_Criteria ADD CONSTRAINT PK_Eligibility_Criteria 
PRIMARY KEY (id) 
;

ALTER TABLE Eligibility_Checklist ADD CONSTRAINT PK_Eligibility_Checklist 
PRIMARY KEY (id) 
;

ALTER TABLE Female_Reproductve_Charactrstc ADD CONSTRAINT PK_Female_Reprodctve_Chrctrstc 
PRIMARY KEY (id) 
;

ALTER TABLE Healthcare_Site ADD CONSTRAINT PK_Healthcare_Site 
PRIMARY KEY (id) 
;

ALTER TABLE Healthcare_Site_Investigator ADD CONSTRAINT PK_Healthcare_Site_Investigatr 
PRIMARY KEY (id) 
;

ALTER TABLE Healthcare_Site_Prtcpnt ADD CONSTRAINT PK_Healthcare_Site_Participant 
PRIMARY KEY (id) 
;

ALTER TABLE Healthcare_Site_Prtcpnt_Role ADD CONSTRAINT PK_Healthcare_Site_Prtcpnt_Rl  
PRIMARY KEY (id) 
;

ALTER TABLE Histopathology ADD CONSTRAINT PK_Histopathology 
PRIMARY KEY (id) 
;

ALTER TABLE Histopathology_Grade ADD CONSTRAINT PK_Histopathology_Grade 
PRIMARY KEY (id) 
;

ALTER TABLE Identifier ADD CONSTRAINT PK_Identifier 
PRIMARY KEY (id) 
;

ALTER TABLE Imaging ADD CONSTRAINT PK_Imaging 
PRIMARY KEY (id) 
;

ALTER TABLE Investigator ADD CONSTRAINT PK_Investigator 
PRIMARY KEY (id) 
;

ALTER TABLE Lesion_Description ADD CONSTRAINT PK_Lesion_Description 
PRIMARY KEY (id) 
;

ALTER TABLE Lesion_Evaluation ADD CONSTRAINT PK_Lesion_Evaluation 
PRIMARY KEY (id) 
;

ALTER TABLE Metastasis_Site ADD CONSTRAINT PK_Metastasis_Site 
PRIMARY KEY (id) 
;

ALTER TABLE Neoplasm ADD CONSTRAINT PK_Neoplasm 
PRIMARY KEY (id) 
;

ALTER TABLE Observation ADD CONSTRAINT PK_Observation 
PRIMARY KEY (id) 
;

ALTER TABLE Observation_Relationship ADD CONSTRAINT PK_Observation_Relationship 
PRIMARY KEY (id) 
;

ALTER TABLE Participant ADD CONSTRAINT PK_Participant 
PRIMARY KEY (id) 
;

ALTER TABLE Participant_Eligibility_Answer ADD CONSTRAINT PK_Participant_Eligiblty_Answr 
PRIMARY KEY (id) 
;

ALTER TABLE Person_Occupation ADD CONSTRAINT PK_Person_Occupation 
PRIMARY KEY (id) 
;

ALTER TABLE Procedure ADD CONSTRAINT PK_Procedure 
PRIMARY KEY (id) 
;

ALTER TABLE Protocol ADD CONSTRAINT PK_Protocol 
PRIMARY KEY (id) 
;

ALTER TABLE Protocol_Participant_Eligiblty ADD CONSTRAINT PK_PROTOCOL_PARTICIPNT_ELGBLTY 
PRIMARY KEY (id) 
;

ALTER TABLE Protocol_Status ADD CONSTRAINT PK_Protocol_Status 
PRIMARY KEY (id) 
;

ALTER TABLE Qualitative_Evaluation ADD CONSTRAINT PK_Qualitative_Evaluation 
PRIMARY KEY (id) 
;

ALTER TABLE Radiation ADD CONSTRAINT PK_Radiation 
PRIMARY KEY (id) 
;

ALTER TABLE Specimen ADD CONSTRAINT PK_Specimen 
PRIMARY KEY (id) 
;

ALTER TABLE Specimen_Collection ADD CONSTRAINT PK_Specimen_Collection 
PRIMARY KEY (id) 
;

ALTER TABLE Study_Agent ADD CONSTRAINT PK_Study_Agent 
PRIMARY KEY (id) 
;

ALTER TABLE Study_Investigator ADD CONSTRAINT PK_Study_Investigator 
PRIMARY KEY (id) 
;

ALTER TABLE Study_Participant_Assignment ADD CONSTRAINT pk_Study_Participant_Assignmnt 
PRIMARY KEY (id) 
;

ALTER TABLE Study_Site ADD CONSTRAINT PK_Study_Site 
PRIMARY KEY (id) 
;

ALTER TABLE Study_Time_Point ADD CONSTRAINT PK_Study_Time_Point 
PRIMARY KEY (id) 
;

ALTER TABLE Substance_Administration ADD CONSTRAINT PK_Substance_Administration 
PRIMARY KEY (id) 
;

ALTER TABLE Surgery ADD CONSTRAINT PK_Surgery 
PRIMARY KEY (id) 
;


--  Create Indexes 
CREATE INDEX IDX_ACT_STDY_PRTCPNT_ASGNMT_ID
ON Activity (STUDY_PARTICIPANT_ASSIGNMNT_ID ASC)
;

CREATE BITMAP INDEX IDX_ACTIVITY_SEC ON ACTIVITY
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_ACR_ACTIVITY_ID_1
ON Activity_Relationship (ACTIVITY_ID_1 ASC)
;

CREATE INDEX IDX_ACR_ACTIVITY_ID_2
ON Activity_Relationship (ACTIVITY_ID_2 ASC)
;

CREATE BITMAP INDEX IDX_ACTIVITY_RELATIONSHIP_SEC ON ACTIVITY_RELATIONSHIP
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_AET_ADVERSE_EVENT_ID
ON Adverse_Event_Therapy (ADVERSE_EVENT_ID ASC)
;

CREATE BITMAP INDEX IDX_ADVERSE_EVENT_THERAPY_SEC ON ADVERSE_EVENT_THERAPY
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_AO_AGENT_ID
ON Agent_Occurrence (AGENT_ID ASC)
;

CREATE INDEX IDX_AO_SUBSTANCE_ADMINSTRTN_ID
ON Agent_Occurrence (SUBSTANCE_ADMINISTRATION_ID ASC)
;

CREATE BITMAP INDEX IDX_AGENT_OCCURRENCE_SEC ON AGENT_OCCURRENCE
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE BITMAP INDEX IDX_ASSESSMENT_SEC ON ASSESSMENT
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_ASR_ASSESSMENT_ID_1
ON Assessment_Relationship (ASSESSMENT_ID_1 ASC)
;

CREATE INDEX IDX_ASR_ASSESSMENT_ID_2
ON Assessment_Relationship (ASSESSMENT_ID_2 ASC)
;

CREATE BITMAP INDEX IDX_ASSESSMENT_R_SEC ON ASSESSMENT_RELATIONSHIP
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_CS_DIAGNOSIS_ID
ON Cancer_Stage (DIAGNOSIS_ID ASC)
;

CREATE BITMAP INDEX IDX_CANCER_STAGE_SEC ON CANCER_STAGE
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_CR_CONCEPT_DESCRIPTOR_ID
ON Clinical_Result (CONCEPT_DESCRIPTOR_ID ASC)
;

CREATE INDEX IDX_DIAGNOSIS_PAT ON DIAGNOSIS
(PRIMARY_ANATOMIC_SITE_CODE)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_ECC_ELIGIBILITY_CHCKLST_ID
ON Eligibility_Checklist_Criteria (ELIGIBILITY_CHECKLIST_ID ASC)
;

CREATE INDEX IDX_ECC_ELIGIBILITY_CRITER_ID
ON Eligibility_Checklist_Criteria (ELIGIBILITY_CRITERIA_ID ASC)
;

CREATE INDEX IDX_ECL_PROTOCOL_ID
ON Eligibility_Checklist (PROTOCOL_ID ASC)
;

CREATE INDEX IDX_FRC_PARTICIPANT_ID
ON Female_Reproductve_Charactrstc (PARTICIPANT_ID ASC)
;

CREATE BITMAP INDEX IDX_FEMALE_R_C_SEC ON FEMALE_REPRODUCTVE_CHARACTRSTC
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_HSI_INVESTIGATOR_ID
ON Healthcare_Site_Investigator (INVESTIGATOR_ID ASC)
;

CREATE INDEX IDX_HSI_HEALTHCARE_SITE_ID
ON Healthcare_Site_Investigator (HEALTHCARE_SITE_ID ASC)
;

CREATE INDEX IDX_HSP_HEALTHCARE_SITE_ID
ON Healthcare_Site_Prtcpnt (HEALTHCARE_SITE_ID ASC)
;

CREATE INDEX IDX_HSP_PARTICIPANT_ID
ON Healthcare_Site_Prtcpnt (PARTICIPANT_ID ASC)
;

CREATE BITMAP INDEX IDX_HEALTHCARE_SITE_P_SEC ON HEALTHCARE_SITE_PRTCPNT
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_HSPR_HLTHCR_SIT_PRTCPNT_ID
ON Healthcare_Site_Prtcpnt_Role (HEALTHCARE_SITE_PRTCPNT_ID ASC)
;

CREATE BITMAP INDEX IDX_HEALTHCARE_SITE_P_R_SEC ON HEALTHCARE_SITE_PRTCPNT_ROLE
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_HG_HISTOPATHOLOGY_ID
ON Histopathology_Grade (HISTOPATHOLOGY_ID ASC)
;

CREATE BITMAP INDEX IDX_HISTOPATHOLOGY_GRADE_SEC ON HISTOPATHOLOGY_GRADE
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE BITMAP INDEX IDX_INVESTIGATOR_SEC ON INVESTIGATOR
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_MS_CANCER_STAGE_ID
ON Metastasis_Site (CANCER_STAGE_ID ASC)
;

CREATE BITMAP INDEX IDX_METASTASIS_SITE_SEC ON METASTASIS_SITE
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_NEO_HISTOPATHOLOGY_ID
ON Neoplasm (HISTOPATHOLOGY_ID ASC)
;

CREATE BITMAP INDEX IDX_NEOPLASM_SEC ON NEOPLASM
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_OBS_ACTIVITY_ID
ON Observation (ACTIVITY_ID ASC)
;

CREATE BITMAP INDEX IDX_OBSERVATION_SEC ON OBSERVATION
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_OA_OBSERVATION_ID
ON OBSERVATION_ASSESSMENT (OBSERVATION_ID ASC)
;

CREATE INDEX IDX_OA_ASSESSMENT_ID
ON OBSERVATION_ASSESSMENT (ASSESSMENT_ID ASC)
;

CREATE INDEX IDX_OR_OBSERVATION_ID_1
ON Observation_Relationship (OBSERVATION_ID_1 ASC)
;

CREATE INDEX IDX_OR_OBSERVATION_ID_2
ON Observation_Relationship (OBSERVATION_ID_2 ASC)
;

CREATE BITMAP INDEX IDX_OBSERVATION_R_SEC ON OBSERVATION_RELATIONSHIP
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE BITMAP INDEX IDX_PARTICIPANT_SEC ON PARTICIPANT
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_PEA_ELIGIBILITY_CRITR_ID
ON Participant_Eligibility_Answer (ELIGIBILITY_CHECKLIST_CRITR_ID ASC)
;

CREATE INDEX IDX_PEA_PARTICIPANT_ID
ON Participant_Eligibility_Answer (PARTICIPANT_ID ASC)
;

CREATE BITMAP INDEX IDX_PARTICIPANT_E_A_SEC ON PARTICIPANT_ELIGIBILITY_ANSWER
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_PO_PERSON_ID
ON Person_Occupation (PERSON_ID ASC)
;

CREATE BITMAP INDEX IDX_PERSON_OCCUPATION_SEC ON PERSON_OCCUPATION
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE BITMAP INDEX IDX_PROTOCOL_SEC ON PROTOCOL
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_PPE_PROTOCOL_ID
ON Protocol_Participant_Eligiblty (PROTOCOL_ID ASC)
;

CREATE INDEX IDX_PPE_PARTICIPANT_ID
ON Protocol_Participant_Eligiblty (PARTICIPANT_ID ASC)
;

CREATE INDEX IDX_PS_PROTOCOL_ID
ON Protocol_Status (PROTOCOL_ID ASC)
;

CREATE BITMAP INDEX IDX_PROTOCOL_STATUS_SEC ON PROTOCOL_STATUS
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_SPEC_SPECIMEN_COLLECTN_ID
ON Specimen (SPECIMEN_COLLECTION_ID ASC)
;

CREATE BITMAP INDEX IDX_SPECIMEN_SEC ON SPECIMEN
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_SAG_AGENT_ID
ON Study_Agent (AGENT_ID ASC)
;

CREATE INDEX IDX_SAG_PROTOCOL_ID
ON Study_Agent (PROTOCOL_ID ASC)
;

CREATE BITMAP INDEX IDX_STUDY_AGENT_SEC ON STUDY_AGENT
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_SI_PROTOCOL_ID
ON Study_Investigator (PROTOCOL_ID ASC)
;

CREATE INDEX IDX_SI_INVESTIGATOR_ID
ON Study_Investigator (INVESTIGATOR_ID ASC)
;

CREATE BITMAP INDEX IDX_STUDY_INVESTIGATOR_SEC ON STUDY_INVESTIGATOR
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_SPA_PARTICIPANT_ID
ON Study_Participant_Assignment (PARTICIPANT_ID ASC)
;

CREATE INDEX IDX_SPA_STUDY_SITE_ID
ON Study_Participant_Assignment (STUDY_SITE_ID ASC)
;

CREATE BITMAP INDEX IDX_STUDY_PARTICIPANT_ASS_SEC ON STUDY_PARTICIPANT_ASSIGNMENT
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_SS_HEALTHCARE_SITE_ID
ON Study_Site (HEALTHCARE_SITE_ID ASC)
;

CREATE INDEX IDX_SS_PROTOCOL_ID
ON Study_Site (PROTOCOL_ID ASC)
;

CREATE BITMAP INDEX IDX_STUDY_SITE_SEC ON STUDY_SITE
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_STP_ACTIVITY_ID
ON Study_Time_Point (ACTIVITY_ID ASC)
;

CREATE BITMAP INDEX IDX_STUDY_TIME_POINT_SEC ON STUDY_TIME_POINT
(SECURITY_KEY)
LOGGING
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            MINEXTENTS       1
            MAXEXTENTS       2147483645
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
NOPARALLEL;

CREATE INDEX IDX_SAD_AGENT_ID
ON Substance_Administration (AGENT_ID ASC)
;

CREATE INDEX IDX_SAD_STUDY_AGENT_ID
ON Substance_Administration (STUDY_AGENT_ID ASC)
;



-- Create Check Constraint
ALTER TABLE Substance_Administration
ADD CONSTRAINT CK_SUBSTANCE_ADMINISTRATN_ARC CHECK ((AGENT_ID is null and 
STUDY_AGENT_ID is null) or 
(AGENT_ID is not null and 
STUDY_AGENT_ID is null) or
(AGENT_ID is null and
STUDY_AGENT_ID is not null))
;



--  Create Foreign Key Constraints 
ALTER TABLE Activity ADD CONSTRAINT FK_Stdy_Prtcpnt_Asgnmt_Actvty 
FOREIGN KEY (STUDY_PARTICIPANT_ASSIGNMNT_ID) REFERENCES Study_Participant_Assignment (id)
ON DELETE CASCADE;

ALTER TABLE Activity_Relationship ADD CONSTRAINT FK_Activity_Activity_Reltnshp 
FOREIGN KEY (ACTIVITY_ID_1) REFERENCES Activity (id)
ON DELETE CASCADE;

ALTER TABLE Activity_Relationship ADD CONSTRAINT FK_Activity_Activity_Reltnshp2 
FOREIGN KEY (ACTIVITY_ID_2) REFERENCES Activity (id)
ON DELETE CASCADE;

ALTER TABLE Adverse_Event ADD CONSTRAINT FK_Assessment_Adverse_Event 
FOREIGN KEY (ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Adverse_Event_Therapy ADD CONSTRAINT FK_Advrs_Evnt_Advrs_Evnt_Thrpy 
FOREIGN KEY (ADVERSE_EVENT_ID) REFERENCES Adverse_Event (id)
ON DELETE CASCADE;

ALTER TABLE Agent_Occurrence ADD CONSTRAINT FK_Agent_Agent_Occurrence 
FOREIGN KEY (AGENT_ID) REFERENCES Agent (id)
ON DELETE CASCADE;

ALTER TABLE Agent_Occurrence ADD CONSTRAINT FK_Substnc_Admnstrn_Agnt_Occrn 
FOREIGN KEY (SUBSTANCE_ADMINISTRATION_ID) REFERENCES Substance_Administration (id)
ON DELETE CASCADE;

ALTER TABLE Assessment_Relationship ADD CONSTRAINT FK_Assessmnt_Assessmnt_Rlnshp 
FOREIGN KEY (ASSESSMENT_ID_1) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Assessment_Relationship ADD CONSTRAINT FK_Assessmnt_Assessmnt_Rlnshp2 
FOREIGN KEY (ASSESSMENT_ID_2) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Cancer_Stage ADD CONSTRAINT FK_Diagnosis_Cancer_Stage 
FOREIGN KEY (DIAGNOSIS_ID) REFERENCES Diagnosis (id)
ON DELETE CASCADE;

ALTER TABLE Clinical_Result ADD CONSTRAINT FK_Concept_Dscrptr_Clncl_Rsult 
FOREIGN KEY (CONCEPT_DESCRIPTOR_ID) REFERENCES Concept_Descriptor (id)
ON DELETE CASCADE;

ALTER TABLE Clinical_Result ADD CONSTRAINT FK_Observation_Clinical_Result 
FOREIGN KEY (ID) REFERENCES Observation (id)
ON DELETE CASCADE;

ALTER TABLE Death_Summary ADD CONSTRAINT FK_Assessment_Death_Summary 
FOREIGN KEY (ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Diagnosis ADD CONSTRAINT FK_Assessment_Diagnosis 
FOREIGN KEY (ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Disease_Response ADD CONSTRAINT FK_Assessment_Disease_Response 
FOREIGN KEY (ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Eligibility_Checklist_Criteria ADD CONSTRAINT FK_Elig_Cklst_Elig_Cklst_Critr 
FOREIGN KEY (ELIGIBILITY_CHECKLIST_ID) REFERENCES Eligibility_Checklist (id)
ON DELETE CASCADE;

ALTER TABLE Eligibility_Checklist_Criteria ADD CONSTRAINT FK_Elig_Critr_Elig_Cklst_Critr 
FOREIGN KEY (ELIGIBILITY_CRITERIA_ID) REFERENCES Eligibility_Criteria (id)
ON DELETE CASCADE;

ALTER TABLE Eligibility_Checklist ADD CONSTRAINT FK_Protocol_Eligibility_Chklst 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Female_Reproductve_Charactrstc ADD CONSTRAINT FK_Partcpnt_Fml_Rprdctv_Chrstc 
FOREIGN KEY (PARTICIPANT_ID) REFERENCES Participant (id)
ON DELETE CASCADE;

ALTER TABLE Healthcare_Site_Investigator ADD CONSTRAINT FK_Invstgt_Healthcr_St_Invstgt 
FOREIGN KEY (INVESTIGATOR_ID) REFERENCES Investigator (id)
ON DELETE CASCADE;

ALTER TABLE Healthcare_Site_Investigator ADD CONSTRAINT FK_Hlthcr_St_Hlthcr_St_Invstgt 
FOREIGN KEY (HEALTHCARE_SITE_ID) REFERENCES Healthcare_Site (id)
ON DELETE CASCADE;

ALTER TABLE Healthcare_Site_Prtcpnt ADD CONSTRAINT FK_Hlthcr_St_Hlthcr_St_Prtcpnt 
FOREIGN KEY (HEALTHCARE_SITE_ID) REFERENCES Healthcare_Site (id)
ON DELETE CASCADE;

ALTER TABLE Healthcare_Site_Prtcpnt ADD CONSTRAINT FK_Prtcpnt_Healthcr_St_Prtcpnt 
FOREIGN KEY (PARTICIPANT_ID) REFERENCES Participant (id)
ON DELETE CASCADE;

ALTER TABLE Healthcare_Site_Prtcpnt_Role ADD CONSTRAINT FK_Hlthcr_St_Hcr_St_Prtcpnt_Rl 
FOREIGN KEY (HEALTHCARE_SITE_PRTCPNT_ID) REFERENCES Healthcare_Site_Prtcpnt (id)
ON DELETE CASCADE;

ALTER TABLE Histopathology ADD CONSTRAINT FK_Observation_Histopathology 
FOREIGN KEY (ID) REFERENCES Observation (id)
ON DELETE CASCADE;

ALTER TABLE Histopathology_Grade ADD CONSTRAINT FK_Histopatholgy_Hstpthlgy_Grd 
FOREIGN KEY (HISTOPATHOLOGY_ID) REFERENCES Histopathology (id)
ON DELETE CASCADE;

ALTER TABLE Identifier ADD CONSTRAINT FK_Protocol_Identifier 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Identifier ADD CONSTRAINT FK_Participant_Identifier 
FOREIGN KEY (PARTICIPANT_ID) REFERENCES Participant (id)
ON DELETE CASCADE;

ALTER TABLE Identifier ADD CONSTRAINT FK_SPA_Identifier 
FOREIGN KEY (STUDY_PARTICIPANT_ASSIGNMNT_ID) REFERENCES Study_Participant_Assignment (id)
ON DELETE CASCADE;

ALTER TABLE Imaging ADD CONSTRAINT FK_Procedure_Imaging 
FOREIGN KEY (ID) REFERENCES Procedure (id)
ON DELETE CASCADE;

ALTER TABLE Lab_Viewer_Status ADD CONSTRAINT FK_Clinical_Result_Lb_Vwr_Stts 
FOREIGN KEY (CLINICAL_RESULT_ID) REFERENCES Clinical_Result (id)
ON DELETE CASCADE;

ALTER TABLE Lesion_Description ADD CONSTRAINT FK_Observation_Lesion_Descrptn 
FOREIGN KEY (ID) REFERENCES Observation (id)
ON DELETE CASCADE;

ALTER TABLE Lesion_Evaluation ADD CONSTRAINT FK_Assessmnt_Lesion_Evaluation 
FOREIGN KEY (ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Metastasis_Site ADD CONSTRAINT FK_Cancer_Stage_Metastasis_Sit 
FOREIGN KEY (CANCER_STAGE_ID) REFERENCES Cancer_Stage (id)
ON DELETE CASCADE;

ALTER TABLE Neoplasm ADD CONSTRAINT FK_Histopathology_Neoplasm 
FOREIGN KEY (HISTOPATHOLOGY_ID) REFERENCES Histopathology (id)
ON DELETE CASCADE;

ALTER TABLE Observation ADD CONSTRAINT FK_Activity_Observation 
FOREIGN KEY (ACTIVITY_ID) REFERENCES Activity (id)
ON DELETE CASCADE;

ALTER TABLE OBSERVATION_ASSESSMENT ADD CONSTRAINT FK_Assessmnt_Obsrvtn_Assessmnt 
FOREIGN KEY (ASSESSMENT_ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE OBSERVATION_ASSESSMENT ADD CONSTRAINT FK_Observatn_Obsrvtn_Assessmnt 
FOREIGN KEY (OBSERVATION_ID) REFERENCES Observation (id)
ON DELETE CASCADE;

ALTER TABLE Observation_Relationship ADD CONSTRAINT FK_Observation_Obsrvtn_Rltnshp 
FOREIGN KEY (OBSERVATION_ID_1) REFERENCES Observation (id)
ON DELETE CASCADE;

ALTER TABLE Observation_Relationship ADD CONSTRAINT FK_Observtion_Obsrvtn_Rltnshp2 
FOREIGN KEY (OBSERVATION_ID_2) REFERENCES Observation (id)
ON DELETE CASCADE;

ALTER TABLE Participant_Eligibility_Answer ADD CONSTRAINT FK_Elg_Cklt_Crt_Prtcpt_Elg_Ans 
FOREIGN KEY (ELIGIBILITY_CHECKLIST_CRITR_ID) REFERENCES Eligibility_Checklist_Criteria (id)
ON DELETE CASCADE;

ALTER TABLE Participant_Eligibility_Answer ADD CONSTRAINT FK_Prtcpnt_Prtcpnt_Elgblt_Ansr 
FOREIGN KEY (PARTICIPANT_ID) REFERENCES Participant (id)
ON DELETE CASCADE;

ALTER TABLE Procedure ADD CONSTRAINT FK_Activity_Procedure 
FOREIGN KEY (ID) REFERENCES Activity (id)
ON DELETE CASCADE;

ALTER TABLE Protocol_Participant_Eligiblty ADD CONSTRAINT FK_PRTCL_PRTCL_PRTCPNT_ELGBLTY 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Protocol_Participant_Eligiblty ADD CONSTRAINT FK_PRTCPNT_PRTCL_PRTCPNT_ELGBL 
FOREIGN KEY (PARTICIPANT_ID) REFERENCES Participant (id)
ON DELETE CASCADE;

ALTER TABLE Protocol_Status ADD CONSTRAINT FK_Protocol_Protocol_Status 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Qualitative_Evaluation ADD CONSTRAINT FK_Assessment_Qualitatve_Evltn 
FOREIGN KEY (ID) REFERENCES Assessment (id)
ON DELETE CASCADE;

ALTER TABLE Radiation ADD CONSTRAINT FK_Procedure_Radiation 
FOREIGN KEY (ID) REFERENCES Procedure (id)
ON DELETE CASCADE;

ALTER TABLE Specimen ADD CONSTRAINT FK_Specimen_Collection_Specimn 
FOREIGN KEY (SPECIMEN_COLLECTION_ID) REFERENCES Specimen_Collection (id)
ON DELETE CASCADE;

ALTER TABLE Specimen_Collection ADD CONSTRAINT FK_Procedure_Specimen_Collectn 
FOREIGN KEY (ID) REFERENCES Procedure (id)
ON DELETE CASCADE;

ALTER TABLE Study_Agent ADD CONSTRAINT FK_Agent_Study_Agent 
FOREIGN KEY (AGENT_ID) REFERENCES Agent (id)
ON DELETE CASCADE;

ALTER TABLE Study_Agent ADD CONSTRAINT FK_Protocol_Study_Agent 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Study_Investigator ADD CONSTRAINT FK_Protocol_Study_Investigator 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Study_Investigator ADD CONSTRAINT FK_Investigator_Study_Invstgtr 
FOREIGN KEY (INVESTIGATOR_ID) REFERENCES Investigator (id)
ON DELETE CASCADE;

ALTER TABLE Study_Investigator ADD CONSTRAINT FK_Study_Site_Study_Invstgtr 
FOREIGN KEY (STUDY_SITE_ID) REFERENCES Study_Site (id)
ON DELETE CASCADE;

ALTER TABLE Study_Participant_Assignment ADD CONSTRAINT FK_Stdy_Ste_Stdy_Prtcpt_Assgnt 
FOREIGN KEY (STUDY_SITE_ID) REFERENCES Study_Site (id)
ON DELETE CASCADE;

ALTER TABLE Study_Participant_Assignment ADD CONSTRAINT FK_Prtcpnt_Stdy_Prtcpnt_Asgnmt 
FOREIGN KEY (PARTICIPANT_ID) REFERENCES Participant (id)
ON DELETE CASCADE;

ALTER TABLE Study_Site ADD CONSTRAINT FK_Healthcare_Site_Study_Site 
FOREIGN KEY (HEALTHCARE_SITE_ID) REFERENCES Healthcare_Site (id)
ON DELETE CASCADE;

ALTER TABLE Study_Site ADD CONSTRAINT FK_Protocol_Study_Site 
FOREIGN KEY (PROTOCOL_ID) REFERENCES Protocol (id)
ON DELETE CASCADE;

ALTER TABLE Study_Time_Point ADD CONSTRAINT FK_Activity_Study_Time_Point 
FOREIGN KEY (ACTIVITY_ID) REFERENCES Activity (id)
ON DELETE CASCADE;

ALTER TABLE Substance_Administration ADD CONSTRAINT FK_Study_Agnt_Substnc_Admnstrn 
FOREIGN KEY (STUDY_AGENT_ID) REFERENCES Study_Agent (id)
ON DELETE CASCADE;

ALTER TABLE Substance_Administration ADD CONSTRAINT FK_Activity_Substanc_Admnstrtn 
FOREIGN KEY (ID) REFERENCES Activity (id)
ON DELETE CASCADE;

ALTER TABLE Substance_Administration ADD CONSTRAINT FK_Agent_Substance_Administrtn 
FOREIGN KEY (AGENT_ID) REFERENCES Agent (id)
ON DELETE CASCADE;

ALTER TABLE Surgery ADD CONSTRAINT FK_Procedure_Surgery 
FOREIGN KEY (ID) REFERENCES Procedure (id)
ON DELETE CASCADE;


SPOOL OFF

SET DEFINE ON

SET ECHO OFF
