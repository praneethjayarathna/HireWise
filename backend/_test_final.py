import sys
sys.path.insert(0, '.')
from jobs.categorizer import categorize, compute_similarity

jd_text = """
ABOUT THE ROLE
We are looking for a senior software engineer to join our platform team.
You will work on building scalable microservices using modern cloud technologies.
"""

resume_text = """
PROFESSIONAL SUMMARY
Experienced software engineer with 6 years building distributed systems.
Proficient in Python, Go, and cloud-native technologies.
"""

cat_jd = categorize(jd_text)
cat_res = categorize(resume_text)

print("JD overview:", cat_jd.get("overview", []))
print("Res overview:", cat_res.get("overview", []))
print()

scores = compute_similarity(cat_jd, cat_res)
print("Scores:", {k: round(v, 4) for k, v in scores.items()})
