

from faker import Faker
import random
import pandas as pd
import sqlite3

fake = Faker()
Faker.seed(0)
random.seed(0)

indian_cities = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Bhopal", "Indore", "Patna", "Nagpur", "Kochi",
    "Thiruvananthapuram", "Surat", "Vadodara", "Ranchi", "Guwahati"
]



def generate_students(n=500):
    students = []
    for i in range(1, n + 1):
        student = {
            "student_id": i,
            "name": fake.name(),
            "age": random.randint(20, 25),
            "gender": random.choice(["Male", "Female", "Other"]),
            "email": fake.email(),
            "phone": fake.msisdn()[0:10],
            "enrollment_year": random.choice([2019, 2020, 2021, 2022]),
            "course_batch": random.choice(["Batch A", "Batch B", "Batch C"]),
            "city": random.choice(indian_cities),
            "graduation_year": random.choice([2023, 2024, 2025])
        }
        students.append(student)
    return pd.DataFrame(students)
students_df = generate_students()
print(students_df.head())

# table programming
def generate_programming(students_df):
    records = []
    for i in range(len(students_df)): # This is your for loop
        student_id = students_df.loc[i,'student_id']
        
        record = {
            "programming_id" : f"P{i+1}",
            "student_id": student_id,
            "language" : random.choice(["python", "SQL"]),
            "problem_solved" : random.randint(10,50),
            "assesment_completed" : random.randint(1,10),
            "Mini_project" : random.randint(1,5),
            "Certification": random.choice(["Yes","No"]),
            "latest_project_score": random.randint(10,100),
        }
        records.append(record) 
    return pd.DataFrame(records)
programming_df = generate_programming(students_df)
print(programming_df.head())
#soft_skill
def generate_soft_skills(students_df):
    records=[]
    for i in range(len(students_df)):
     student_id = students_df.loc[i,'student_id']
     record={
    "soft_skill_id" : f"S{i+1}",
"student_id": student_id,
 "communication" : random.randint(50,100) ,
 "team_work" :random.randint(10,50) ,
 "presentation"  :random.randint(1,10) ,
  "leadership" : random.randint(1,5),
  "Critical_thinking":random.randint(1,5),
  "interpersonal_skill": random.randint(10,100),
      }
     records.append(record)
    return pd.DataFrame(records)
#creating instances

soft_skills_df = generate_soft_skills(students_df)
print (soft_skills_df.head())


# placement_table
def generate_placement(students_df):
    records = []
    for i in range(len(students_df)):
        student_id = students_df.loc[i, 'student_id']

        Mock_score = random.randint(50, 100)
        Intership_status = random.choice(["yes", "no"])

        if Mock_score > 70 and Intership_status == "yes":
            placement_status = random.choice(["Ready", "Placed"])
        elif Mock_score > 50:
            placement_status = random.choice(["Ready", "Not Ready"])
        else:
            placement_status = "Not Ready"

        if placement_status == "Placed":
            company_name = random.choice(["TCS", "Infosys", "Wipro", "Google", "Amazon"])
            placement_package = random.randint(300000, 700000)
            interview_rounds_cleared = random.randint(1, 5)
            placement_date = fake.date_between(start_date='-1y', end_date='today')
        else:
            company_name = "N/A"
            placement_package = 0
            interview_rounds_cleared = 0
            placement_date = "N/A"

        record = {
            "placement_id": f"PL{i+1}",
            "student_id": student_id,
            "mock_interview_score": Mock_score,
            "internship_complted": Intership_status,
            "Placement_status": placement_status,
            "Company_name": company_name,
            "placement_package": placement_package,
            "interview_rounds_cleared": interview_rounds_cleared,
            "placement_date": placement_date
        }

        records.append(record)

    return pd.DataFrame(records)

# Creating instances
placement_df = generate_placement(students_df)
print (placement_df.head())

conn = sqlite3.connect("placement_eligibility.db")

students_df.to_sql("Students", conn, if_exists="replace", index=False)
programming_df.to_sql("Programming", conn, if_exists="replace", index=False)
soft_skills_df.to_sql("SoftSkills", conn, if_exists="replace", index=False)
placement_df.to_sql("Placements", conn, if_exists="replace", index=False)

print(" All tables successfully written to placement_eligibility.db!")


students_df = pd.read_sql("SELECT * FROM Students", conn)
print("\nSample Students Table:\n", students_df.head())