# Instructor Performance and Course Quality Evaluation on EduPro

A Power BI analytics project that evaluates instructor effectiveness, course quality, and learner satisfaction across EduPro's online learning platform — identifying top-performing and underperforming instructors, high-demand course categories, and actionable recommendations to improve platform quality. Built as part of the Unified Mentor Data Analytics program.


**Problem Statement**

EduPro offers a wide range of online courses delivered by instructors with varying levels of expertise, experience, and teaching effectiveness. Differences in instructor performance and course quality significantly impact learner satisfaction, course ratings, enrollments, and platform credibility.
The platform currently lacks clarity on:

Which instructors consistently deliver high-quality courses?
Does teaching experience translate into better-rated courses?
Are some course categories more dependent on instructor quality?
How evenly is teaching performance distributed across the platform?


**Dataset**

**Source:** EduPro Online Platform dataset (provided via Unified Mentor)
**Tables:** Teachers, Courses, Transactions, Users
**Size:** ~1,000 instructors, ~10,000 transactions
**Schema**: Star Schema — Fact_Transactions with Dim_Teachers, Dim_Courses, Dim_Users dimension tables

**Key fields used:** TeacherID, TeacherName, Expertise, YearsOfExperience, TeacherRating, CourseID, CourseName, CourseCategory, CourseLevel, CourseRating, TransactionID, Gender, Age.

** Tools Used**
Tool Purpose- Power Query, Data cleaning, type validation, relationship setupPower BI (DAX), KPI measures, calculated columns, segmentation logic, Power BI Desktop Report design, visuals, conditional formatting, Power BI Service Dashboard publishing


**Methodology**

**1. Data Modeling (Star Schema)**
A Star Schema was designed with Fact_Transactions at the center, connected to four dimension tables: Dim_Teachers, Dim_Courses, Dim_Users, and a Date table. This structure enables efficient cross-filtering across all dashboard pages.


**2. Key DAX Measures**

Custom DAX measures were built to capture platform-wide performance, including:

**Experience Impact Scor**e — measures the influence of instructor experience on course outcomes
**Rating Consistency Index** — evaluates the stability of learner feedback across courses
**Enrollment Influence Ratio** — captures the relationship between instructor quality and enrollment volume
**Average Teacher Rating and Average Course Rating** — core KPIs for instructor and course performance tracking


**3. Exploratory Data Analysis (EDA)**

Four EDA sections were developed:

Section A — Platform-wide KPI dashboard, enrollment by category, gender distribution, rating tier analysis
Section B — Instructor performance analysis: experience vs ratings, age distribution, expertise gap analysis
Section C — Course quality analysis: free vs paid ratings, category vs level matrix, gender vs course level, duration vs rating
Section D — Instructor impact analysis: top performers, low performers, teacher vs course rating comparison by expertise


**Dashboard Pages**

**EduPro - Instructor & Course Quality**— Platform KPIs, enrollment by category, teacher rating distribution, gender breakdown, slicers (course category, expertise, cousre level, course type)
**Instructor Performance analysis** — Experience vs rating trends, age distribution, expertise gap analysis
**Course Quality evaluation**— Free vs paid comparison, category × level matrix, duration vs rating scatter, Gender vs Course Leve
**Instructor Impact analysis** — Top and low performer tables, teacher vs course rating by expertise area

All pages are cross-filtered using Department, Expertise, and Course Level slicers.


**Key Insights**

The average Teacher Rating (3.13) and average Course Rating (3.10) are nearly identical, confirming that instructor quality is the primary driver of learner satisfaction on the platform.
Teacher ratings range from 1.07 to 4.97, a gap of 3.90 points, indicating substantial variation in instructional quality across the platform.
Marketing (4.3), Machine Learning (4.2), and Programming (4.0) are the highest-rated expertise areas, all significantly above the platform average of 3.13.
Design (2.3) and Web Development (2.5) are the weakest expertise areas and require immediate curriculum and instructor quality improvement.
Data Science records the highest enrollment (916 learners), reflecting strong learner demand for technology and career-oriented skills.
Free Beginner and Intermediate courses outperform their paid counterparts in learner ratings, demonstrating that content quality — not pricing — drives satisfaction.
Instructor ratings above 4.0 are predominantly found among instructors with 8 or more years of experience, confirming a positive relationship between experience and teaching effectiveness.
Kimberly Miller (Cybersecurity, rating 4.58) recorded the highest total enrollment on the platform (3,025 learners), demonstrating a strong link between instructor reputation and enrollment volume.


**How to Use**

Clone or download this repository
Open EduPro online platform.pdf in Desktop
Explore the Instructor Impact page to compare top and low performers side by side


**Repository Contents**

EduPro_Online_Platform.xlsx — Source dataset
EduPro_Research_Paper.pdf — Full EDA, methodology, and recommendations writeup
eudpro online platform.pdf- Dashboard page previews
summary for government stakeholders- eduPro.pdf — Executive summary for stakeholders


**Author**

Pawan Kumar Lakhera
Aspiring Data Analyst | Power BI · SQL · Python
#https://www.linkedin.com/in/pawan-lakhera-738429174/

Part of the Unified Mentor Data Analytics project series.
