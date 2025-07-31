import streamlit as st # Import the Streamlit library for building web apps
import pandas as pd     # Import pandas for data manipulation (especially for DataFrames)
import sqlite3          # Import sqlite3 for interacting with SQLite databases
import os               # Import os for checking file existence

# --- Configuration ---
# Define the name of our database file. This must match the name used in your Jupyter Notebook.
DB_NAME = 'placement_data.db'

# --- Database Manager Class (Using Object-Oriented Programming for good structure) ---
# This class definition is placed here so it's defined before it's used later in the script.
class DatabaseManager:
    """
    Manages the connection to our SQLite database and handles SQL query execution.
    Using a class helps organize database-related functions.
    """
    def __init__(self, db_name):
        """
        Initializes the DatabaseManager with the database file name.
        """
        self.db_name = db_name
        self.conn = None # Initialize connection as None, it will be set when connected

    @st.cache_resource # This decorator tells Streamlit to cache the database connection.
                       # It means the connection will be created only once,
                       # even if the app reruns, making it more efficient.
    def get_connection(_self):
        """
        Establishes and returns a connection to the SQLite database.
        'check_same_thread=False' is important for Streamlit to prevent threading issues.
        """
        if _self.conn is None: # If connection doesn't exist yet, create it
            try:
                _self.conn = sqlite3.connect(_self.db_name, check_same_thread=False)
                st.success(f"Successfully connected to database: {_self.db_name}")
            except sqlite3.Error as e:
                # If there's an error connecting, show an error message and stop the app
                st.error(f"Error connecting to database: {e}")
                st.stop() # Halts the Streamlit app execution
        return _self.conn # Return the established connection

    def execute_query(self, query, params=None):
        """
        Executes a given SQL query and returns the results as a pandas DataFrame.
        This function handles both SELECT queries and queries with parameters.
        """
        conn = self.get_connection() # Get the database connection
        try:
            if params: # If parameters are provided (e.g., for WHERE clauses)
                df = pd.read_sql_query(query, conn, params=params)
            else: # If no parameters are needed
                df = pd.read_sql_query(query, conn)
            return df # Return the query results as a DataFrame
        except pd.io.sql.DatabaseError as e:
            # Catch specific database errors (e.g., malformed SQL)
            st.error(f"Error executing query: {e}")
            return pd.DataFrame() # Return an empty DataFrame on error
        except Exception as e:
            # Catch any other unexpected errors
            st.error(f"An unexpected error occurred: {e}")
            return pd.DataFrame()

# --- Initialize Database Manager ---
# Before anything else, check if the database file exists.
# If not, the app can't run, so show an error and stop.
if not os.path.exists(DB_NAME):
    st.error(f"Database file '{DB_NAME}' not found. "
             f"Please run your Jupyter Notebook (`data_generation_notebook.ipynb`) first to create the database.")
    st.stop() # Stop the Streamlit application

# Create an instance of our DatabaseManager
# This line now correctly calls the DatabaseManager class which is defined above.
db_manager = DatabaseManager(DB_NAME)

# --- Updated SQL Queries for Insights (Matching your DataFrame column names) ---
# These are the 10 SQL queries required for the "Data Insights" section.
# They are stored in a dictionary for easy access.
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

# --- Streamlit Application Layout and Logic ---

# Set basic page configuration for a wide layout and title
st.set_page_config(layout="wide", page_title="Placement Eligibility App")

# Main title of the application
st.title("🎓 Placement Eligibility Streamlit Application")
st.markdown("---") # A horizontal line for separation

# Sidebar for Navigation
st.sidebar.header("Navigation") # Header for the sidebar section
# Create radio buttons in the sidebar to switch between different pages/sections
page = st.sidebar.radio("Go to", ["Filter Students", "View Insights"]) # Names changed here

# --- Logic for "Eligibility Filter" Page ---
if page == "Filter Students": # Name changed here
    st.header("🎯 Filter Eligible Students")
    st.write("Define the criteria to find suitable candidates for placement.")

    # Input fields for eligibility criteria using Streamlit widgets
    # Sliders allow users to easily select a range of values.
    st.subheader("Programming Performance Criteria")
    min_problem_solved = st.slider("Minimum Problems Solved", 0, 50, 20) # Adjusted max based on your data
    min_assesment_completed = st.slider("Minimum Assessments Completed", 0, 10, 3)
    min_mini_project = st.slider("Minimum Mini Projects", 0, 5, 1)
    min_latest_project_score = st.slider("Minimum Latest Project Score", 0, 100, 60)
    required_certification = st.checkbox("Certification Required", value=False) # Added based on your data

    st.subheader("Soft Skills Criteria")
    min_communication = st.slider("Minimum Communication Score", 0, 100, 65)
    min_team_work = st.slider("Minimum Team Work Score", 0, 50, 25) # Adjusted max based on your data
    min_presentation = st.slider("Minimum Presentation Score", 0, 10, 5) # Adjusted max based on your data
    min_leadership = st.slider("Minimum Leadership Score", 0, 5, 2) # Adjusted max based on your data
    min_critical_thinking = st.slider("Minimum Critical Thinking Score", 0, 5, 2) # Adjusted max based on your data
    min_interpersonal_skill = st.slider("Minimum Interpersonal Skill Score", 0, 100, 60)

    st.subheader("Placement Readiness Criteria")
    min_mock_interview_score = st.slider("Minimum Mock Interview Score", 0, 100, 70)
    # Checkbox for boolean criteria (internship required or not)
    required_internship = st.checkbox("Internship Completed (Yes)", value=True)
    # Note: Your placement_df does not have resume_score or aptitude_score.
    # We will remove these from the filter and query for now.
    # If you want them, you'd need to add them to your generate_placement function.

    # Build the dynamic SQL query for eligibility
    # This query joins all relevant tables and filters based on user inputs.
    # f-strings are used to easily embed Python variables (slider values) into the SQL query.
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

    st.markdown("---") # Another horizontal line
    st.subheader("Eligible Candidates")

    # Execute the dynamically built query to get eligible students
    eligible_students_df = db_manager.execute_query(eligibility_query)

    if not eligible_students_df.empty: # Check if the DataFrame is not empty
        st.write(f"Found {len(eligible_students_df)} eligible student(s) based on your criteria:")
        st.dataframe(eligible_students_df) # Display the DataFrame as an interactive table
        # Add a download button for the results
        st.download_button(
            label="Download Eligible Students as CSV",
            data=eligible_students_df.to_csv(index=False).encode('utf-8'),
            file_name="eligible_students.csv",
            mime="text/csv",
        )
    else:
        st.info("No students found matching the specified criteria. Try adjusting the filters.")

# --- Logic for "Data Insights" Page ---
elif page == "View Insights": # Name changed here
    st.header("📊 Data Insights and Analytics")
    st.write("Explore key metrics and distributions from the student dataset.")

    # Dropdown to select which insight query to run
    insight_choice = st.selectbox("Select an Insight Query", list(SQL_QUERIES.keys()))

    if insight_choice: # If an insight query is selected
        query_to_run = SQL_QUERIES[insight_choice] # Get the SQL query string
        st.code(query_to_run, language='sql') # Display the SQL query itself for transparency

        insight_df = db_manager.execute_query(query_to_run) # Execute the selected query

        if not insight_df.empty: # Check if the insight DataFrame is not empty
            st.subheader("Query Result")
            st.dataframe(insight_df) # Display the raw query result

            # --- Basic Visualization for some Insights ---
            # Streamlit offers simple charting functions.
            # We check for specific column names to decide which chart to show.
            if "count" in insight_df.columns and "course_batch" in insight_df.columns:
                # For "Students by Course Batch" insight, show a bar chart
                st.bar_chart(insight_df.set_index('course_batch')['count'])
            elif "score_range" in insight_df.columns and "num_students" in insight_df.columns:
                # For "Distribution of Mock Interview Scores", show a bar chart
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

