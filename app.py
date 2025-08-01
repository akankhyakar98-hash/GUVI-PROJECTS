import streamlit as st 
import pandas as pd     
import sqlite3          
import os               

DB_NAME = 'placement_data.db'

class DatabaseManager:
    
    def __init__(self, db_name):
        
        self.db_name = db_name
        self.conn = None 
    @st.cache_resource 
    def get_connection(_self):
        
        if _self.conn is None: 
            try:
                _self.conn = sqlite3.connect(_self.db_name, check_same_thread=False)
                st.success(f"Successfully connected to database: {_self.db_name}")
            except sqlite3.Error as e:
                
                st.error(f"Error connecting to database: {e}")
                st.stop() 
        return _self.conn 

    def execute_query(self, query, params=None):
        
        conn = self.get_connection() 
        try:
            if params: 
                df = pd.read_sql_query(query, conn, params=params)
            else: 
                df = pd.read_sql_query(query, conn)
            return df 
        except pd.io.sql.DatabaseError as e:
            
            st.error(f"Error executing query: {e}")
            return pd.DataFrame() 
        except Exception as e:
            
            st.error(f"An unexpected error occurred: {e}")
            return pd.DataFrame()


if not os.path.exists(DB_NAME):
    st.error(f"Database file '{DB_NAME}' not found. "
             f"Please run your Jupyter Notebook (`data_generation_notebook.ipynb`) first to create the database.")
    st.stop() 


db_manager = DatabaseManager(DB_NAME)


SQL_QUERIES = {
    "Total Students": "SELECT COUNT(*) FROM Students;",
    "Average Age of Students": "SELECT AVG(age) FROM Students;",
    "Students by Course Batch": "SELECT course_batch, COUNT(*) AS count FROM Students GROUP BY course_batch ORDER BY count DESC;",
    "Average Programming Problems Solved": """
        SELECT AVG(P.problem_solved)
        FROM Programming P;
    """,
    "Top 5 Students by Latest Project Score": """
        SELECT S.name, P.latest_project_score
        FROM Students S
        JOIN Programming P ON S.student_id = P.student_id
        ORDER BY P.latest_project_score DESC
        LIMIT 5;
    """,
    "Average Soft Skills Score (Overall)": """
        SELECT AVG(
            COALESCE(communication, 0) +
            COALESCE(team_work, 0) +
            COALESCE(presentation, 0) +
            COALESCE(leadership, 0) +
            COALESCE(Critical_thinking, 0) +
            COALESCE(interpersonal_skill, 0)
        ) / 6 AS avg_soft_skills_score
        FROM SoftSkills;
    """,
    "Students with Internship Completed": """
        SELECT S.name, S.course_batch
        FROM Students S
        JOIN Placements PL ON S.student_id = PL.student_id
        WHERE PL.internship_complted = 'yes';
    """,
    "Distribution of Mock Interview Scores": """
        SELECT
            CASE # SQL's CASE statement allows defining categories based on score ranges
                WHEN mock_interview_score BETWEEN 0 AND 49 THEN '0-49 (Poor)'
                WHEN mock_interview_score BETWEEN 50 AND 69 THEN '50-69 (Average)'
                WHEN mock_interview_score BETWEEN 70 AND 89 THEN '70-89 (Good)'
                WHEN mock_interview_score BETWEEN 90 AND 100 THEN '90-100 (Excellent)'
                ELSE 'N/A'
            END AS score_range,
            COUNT(*) AS num_students
        FROM Placements
        GROUP BY score_range # Group results by the defined score ranges
        ORDER BY score_range;
    """,
    "Students Ready for Placement": """
        SELECT S.name, S.course_batch, PL.mock_interview_score, PL.Placement_status, PL.Company_name
        FROM Students S
        JOIN Placements PL ON S.student_id = PL.student_id
        WHERE PL.Placement_status = 'Ready' OR PL.Placement_status = 'Placed';
    """,
    "Average Placement Package by Batch": """
        SELECT S.course_batch, AVG(PL.placement_package) AS avg_package
        FROM Students S
        JOIN Placements PL ON S.student_id = PL.student_id
        WHERE PL.Placement_status = 'Placed'
        GROUP BY S.course_batch
        ORDER BY avg_package DESC;
    """,
    "Students with High Mock Interview Scores and Placement Status": """
        SELECT
            S.name,
            S.course_batch,
            PL.mock_interview_score,
            PL.Placement_status,
            PL.Company_name
        FROM
            Students S
        JOIN
            Placements PL ON S.student_id = PL.student_id
        WHERE
            PL.Placement_status IN ('Ready', 'Placed')
        ORDER BY
            PL.mock_interview_score DESC;
    """,
    "Student with Highest Placement Package": """
        SELECT
            S.name,
            S.course_batch,
            PL.Company_name,
            PL.placement_package
        FROM
            Students S
        JOIN
            Placements PL ON S.student_id = PL.student_id
        WHERE
            PL.Placement_status = 'Placed'
        ORDER BY
            PL.placement_package DESC
        LIMIT 1;
    """,
    "Count Students by City": """
        SELECT city, COUNT(student_id) AS NumberOfStudents
        FROM Students
        GROUP BY city
        ORDER BY NumberOfStudents DESC;
    """,
}




st.set_page_config(layout="wide", page_title="Placement Eligibility App")


st.title(" Placement Eligibility Streamlit Application")
st.markdown("---") 

st.sidebar.header("Navigation") 
page = st.sidebar.radio("Go to", ["Filter Students", "View Insights"]) 


if page == "Filter Students": 
    st.header(" Filter Eligible Students")
    st.write("Define the criteria to find suitable candidates for placement.")

    
    st.subheader("Programming Performance Criteria")
    min_problem_solved = st.slider("Minimum Problems Solved", 0, 50, 20) 
    min_assesment_completed = st.slider("Minimum Assessments Completed", 0, 10, 3)
    min_mini_project = st.slider("Minimum Mini Projects", 0, 5, 1)
    min_latest_project_score = st.slider("Minimum Latest Project Score", 0, 100, 60)
    required_certification = st.checkbox("Certification Required", value=False) 
# print("subheader")
    st.subheader("Soft Skills Criteria")
    min_communication = st.slider("Minimum Communication Score", 0, 100, 65)
    min_team_work = st.slider("Minimum Team Work Score", 0, 50, 25) 
    min_presentation = st.slider("Minimum Presentation Score", 0, 10, 5) 
    min_leadership = st.slider("Minimum Leadership Score", 0, 5, 2) 
    min_critical_thinking = st.slider("Minimum Critical Thinking Score", 0, 5, 2) 
    min_interpersonal_skill = st.slider("Minimum Interpersonal Skill Score", 0, 100, 60)

    st.subheader("Placement Readiness Criteria")
    min_mock_interview_score = st.slider("Minimum Mock Interview Score", 0, 100, 70)
    
    required_internship = st.checkbox("Internship Completed (Yes)", value=True)
    
    
    eligibility_query = f"""
        SELECT
            S.student_id,
            S.name,
            S.age,
            S.gender,
            S.course_batch,
            S.city,
            P.problem_solved,
            P.assesment_completed,
            P.Mini_project,
            P.latest_project_score,
            P.Certification,
            SS.communication,
            SS.team_work,
            SS.presentation,
            SS.leadership,
            SS.Critical_thinking,
            SS.interpersonal_skill,
            PL.mock_interview_score,
            PL.internship_complted,
            PL.Placement_status,
            PL.Company_name,
            PL.placement_package
        FROM Students S
        JOIN Programming P ON S.student_id = P.student_id
        JOIN SoftSkills SS ON S.student_id = SS.student_id
        JOIN Placements PL ON S.student_id = PL.student_id
        WHERE
            P.problem_solved >= {min_problem_solved} AND
            P.assesment_completed >= {min_assesment_completed} AND
            P.Mini_project >= {min_mini_project} AND
            P.latest_project_score >= {min_latest_project_score} AND
            SS.communication >= {min_communication} AND
            SS.team_work >= {min_team_work} AND
            SS.presentation >= {min_presentation} AND
            SS.leadership >= {min_leadership} AND
            SS.Critical_thinking >= {min_critical_thinking} AND
            SS.interpersonal_skill >= {min_interpersonal_skill} AND
            PL.mock_interview_score >= {min_mock_interview_score}
            {'AND P.Certification = "Yes"' if required_certification else ''}
            {'AND PL.internship_complted = "yes"' if required_internship else ''}
        ORDER BY PL.mock_interview_score DESC, P.latest_project_score DESC
    """

    st.markdown("---") 
    st.subheader("Eligible Candidates")

    
    eligible_students_df = db_manager.execute_query(eligibility_query)

    if not eligible_students_df.empty:
        st.write(f"Found {len(eligible_students_df)} eligible student(s) based on your criteria:")
        st.dataframe(eligible_students_df) 
        
        st.download_button(
            label="Download Eligible Students as CSV",
            data=eligible_students_df.to_csv(index=False).encode('utf-8'),
            file_name="eligible_students.csv",
            mime="text/csv",
        )
    else:
        st.info("No students found matching the specified criteria. Try adjusting the filters.")


elif page == "View Insights": 
    st.header(" Data Insights and Analytics")
    st.write("Explore key metrics and distributions from the student dataset.")

    
    insight_choice = st.selectbox("Select an Insight Query", list(SQL_QUERIES.keys()))

    if insight_choice: 
        query_to_run = SQL_QUERIES[insight_choice] 
        st.code(query_to_run, language='sql')

        insight_df = db_manager.execute_query(query_to_run) 

        if not insight_df.empty: 
            st.subheader("Query Result")
            st.dataframe(insight_df) 

            
            if "count" in insight_df.columns and "course_batch" in insight_df.columns:
                
                st.bar_chart(insight_df.set_index('course_batch')['count'])
            elif "score_range" in insight_df.columns and "num_students" in insight_df.columns:

                st.bar_chart(insight_df.set_index('score_range')['num_students'])
            elif "avg_soft_skills_score" in insight_df.columns:
                st.write("Overall Average Soft Skills Score:")
                st.metric(label="Average Score", value=f"{insight_df['avg_soft_skills_score'].iloc[0]:.2f}")
            elif "avg_package" in insight_df.columns and "course_batch" in insight_df.columns:
                st.bar_chart(insight_df.set_index('course_batch')['avg_package'])
            elif "latest_project_score" in insight_df.columns and "name" in insight_df.columns:
                 st.bar_chart(insight_df.set_index('name')['latest_project_score'])
            elif "NumberOfStudents" in insight_df.columns and "city" in insight_df.columns:
                 st.bar_chart(insight_df.set_index('city')['NumberOfStudents'])
        else:
            st.info("No data returned for this insight query.")



