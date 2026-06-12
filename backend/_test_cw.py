import sys
sys.path.insert(0, '.')
from jobs.categorizer import categorize, compute_similarity, compare_overviews

jd_text = """
ABOUT THE ROLE
We are looking for a senior software engineer to join our platform team.
You will work on building scalable microservices using modern cloud technologies.
Our tech stack includes Python, Go, Kubernetes, and AWS.

RESPONSIBILITIES
Design and implement distributed systems
Write clean, testable code with proper documentation
Mentor junior engineers and conduct code reviews
Collaborate with product team to define technical requirements

QUALIFICATIONS
5+ years of professional software engineering experience
Strong knowledge of Python or Go
Experience with cloud platforms (AWS preferred)
Bachelors in Computer Science or related field

SKILLS
Python, Go, Kubernetes, Docker, AWS, PostgreSQL, Redis, REST APIs, gRPC
"""

resume_text = """
PROFESSIONAL SUMMARY
Experienced software engineer with 6 years building distributed systems.
Proficient in Python, Go, and cloud-native technologies.
Led migration of monolith to microservices on AWS EKS.

EXPERIENCE
Senior Backend Engineer at TechCorp (2020-2024)
Designed and implemented REST APIs handling 10M+ requests/day
Led migration from monolith to microservices on AWS EKS
Mentored 4 junior engineers
Reduced p99 latency by 40% through query optimization

EDUCATION
Bachelors in Computer Science

SKILLS
Python, Go, TypeScript, Kubernetes, Docker, AWS, PostgreSQL, Redis, REST, gRPC
"""

jd_cat = categorize(jd_text)
res_cat = categorize(resume_text)

print("JD overview:", jd_cat.get("overview", []))
print("Res overview:", res_cat.get("overview", []))
print()

scores = compute_similarity(jd_cat, res_cat)
print("=== Similarity Scores ===")
for k, v in scores.items():
    print(f"  {k}: {v:.4f}")

print()
matches = compare_overviews(jd_cat.get("overview", []), res_cat.get("overview", []))
print("=== Overview Pairs ===")
for m in matches:
    print(f"  sim={m['similarity']:.3f}")
    print(f"    JD:  {m['job_sentence'][:70]}")
    print(f"    RES: {m['resume_sentence'][:70]}")
print(f"  Total matched: {len(matches)}")

# Test with unequal lengths
print("\n--- Unequal length test ---")
jd_long = ["A" for _ in range(10)]
res_short = ["A" for _ in range(2)]
# Simulate: assume all sentences match perfectly (similarity ~1.0 for identical text)
from jobs.categorizer import _get_model
model = _get_model()
jd_emb = model.encode(jd_long, convert_to_numpy=True, show_progress_bar=False)
res_emb = model.encode(res_short, convert_to_numpy=True, show_progress_bar=False)
from jobs.categorizer import _greedy_matches
pairs, avg, cw = _greedy_matches(jd_emb, res_emb)
print(f"Identical texts: 10 JD vs 2 RES")
print(f"  pairs={len(pairs)}, simpleAvg={avg:.3f}, coverageWeighted={cw:.3f}")
