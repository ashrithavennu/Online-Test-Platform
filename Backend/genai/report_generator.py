"""
EduAssess — GenAI Module
Task: Student Performance Report Generator
Uses: Anthropic Claude API (or OpenAI as fallback)

Setup:
  pip install anthropic          # for Claude
  pip install openai             # for OpenAI (optional fallback)

Set environment variable:
  Windows : set GENAI_API_KEY=your_key_here
  Linux   : export GENAI_API_KEY=your_key_here
"""

import os, json

PROVIDER = os.environ.get("GENAI_PROVIDER", "anthropic").lower()
API_KEY  = os.environ.get("GENAI_API_KEY", "")


def generate_report(student_data: dict) -> dict:
    if API_KEY:
        if PROVIDER == "anthropic":
            result = _call_anthropic(student_data)
            if result:
                return result
        result = _call_openai(student_data)
        if result:
            return result
    return _template_report(student_data)


def _call_anthropic(d):
    try:
        import anthropic
        client  = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": _build_prompt(d)}]
        )
        text = message.content[0].text
        return {"report": text, "sections": _parse_sections(text), "source": "anthropic"}
    except Exception as e:
        print(f"Anthropic error: {e}")
    return None


def _call_openai(d):
    try:
        import urllib.request
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": _build_prompt(d)}],
            "max_tokens": 800
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = json.loads(resp.read())["choices"][0]["message"]["content"]
            return {"report": text, "sections": _parse_sections(text), "source": "openai"}
    except Exception as e:
        print(f"OpenAI error: {e}")
    return None


def _build_prompt(d):
    accuracy = round(d.get("correct",0) / max(d.get("total",1),1) * 100, 1)
    return f"""You are an academic performance analysis AI for a college exam system.
Generate a professional performance report for this student.

Student : {d.get('student_name')}
Exam    : {d.get('exam_title')} ({d.get('subject')})
Score   : {d.get('score')}% | Correct: {d.get('correct')}/{d.get('total')} | Wrong: {d.get('wrong')} | Skipped: {d.get('skipped')}
Time    : {d.get('time_taken')} minutes | Accuracy: {accuracy}%

Write exactly 4 sections with these headers:
OVERALL PERFORMANCE SUMMARY
STRENGTHS
AREAS FOR IMPROVEMENT
RECOMMENDATIONS

Be specific, data-driven, and encouraging. No markdown or bullet symbols."""


def _template_report(d):
    name, exam, subject = d.get("student_name","Student"), d.get("exam_title","Exam"), d.get("subject","Subject")
    score, correct, wrong   = d.get("score",0), d.get("correct",0), d.get("wrong",0)
    skipped, total, time_taken = d.get("skipped",0), d.get("total",1), d.get("time_taken",0)
    accuracy = round(correct / max(total,1) * 100, 1)

    if score >= 75:
        o = f"{name} demonstrated excellent performance in {exam}, achieving {score}% with {correct}/{total} correct in {time_taken} minutes. This reflects strong conceptual understanding and effective time management."
        s = f"Strong command of core {subject} concepts with {accuracy}% accuracy rate. Efficient time management completing {total} questions in {time_taken} minutes. Thorough preparation reflected in {correct} correct answers."
        i = f"{wrong} incorrect answers suggest minor gaps in specific subtopics. {skipped} skipped questions indicate slight uncertainty in a few areas. Targeting these will push scores above 90%."
        r = f"Practice 2-3 advanced problems daily on LeetCode or HackerRank. Review the {wrong+skipped} missed or skipped questions to identify weak spots. Attempt timed mock exams regularly. Explore advanced topics for deeper mastery."
    elif score >= 50:
        o = f"{name} achieved a moderate score of {score}% in {exam} with {correct} correct, {wrong} wrong, and {skipped} skipped out of {total} in {time_taken} minutes. Clear potential exists with meaningful room for improvement."
        s = f"Attempted {correct+wrong} of {total} questions showing confidence to engage with material. Shows familiarity with foundational {subject} concepts at {accuracy}% accuracy. Completed the exam within the allotted time."
        i = f"{wrong} incorrect answers indicate conceptual gaps in several key topics. {skipped} skipped questions suggest areas where confidence is lacking. Focused revision is needed to bridge the gap to 75%+."
        r = f"Dedicate 45 minutes daily to revising weak {subject} topics. Solve 10+ MCQs per topic using standard textbook exercises. Re-read lecture notes for incorrectly answered chapters. Take 2 full mock tests before the next exam."
    else:
        o = f"{name} scored {score}% in {exam} with {correct} correct, {wrong} wrong, and {skipped} skipped out of {total} in {time_taken} minutes. Significant improvement is required in {subject}."
        s = f"Attempted {correct+wrong} questions showing willingness to engage with the material. Getting {correct} questions correct demonstrates some understanding of basic concepts."
        i = f"{wrong} wrong answers show that core {subject} concepts need urgent revision. {skipped} unattempted questions indicate low confidence across multiple topics. Foundational understanding must be rebuilt systematically."
        r = f"Create a structured 2-week revision plan covering all {subject} topics. Study from standard reference textbooks starting from basics. Practice 20 MCQs daily and maintain an error log. Attend doubt-clearing sessions and seek teacher guidance."

    report = f"OVERALL PERFORMANCE SUMMARY\n{o}\n\nSTRENGTHS\n{s}\n\nAREAS FOR IMPROVEMENT\n{i}\n\nRECOMMENDATIONS\n{r}"
    return {"report": report, "sections": {"overall":o,"strengths":s,"improvement":i,"recommendations":r}, "source":"template"}


def _parse_sections(text):
    sections, keywords = {}, {"OVERALL":"overall","STRENGTH":"strengths","IMPROVEMENT":"improvement","RECOMMEND":"recommendations"}
    current_key, current_lines = None, []
    for line in text.strip().split("\n"):
        matched = next((v for k,v in keywords.items() if k in line.upper()), None)
        if matched:
            if current_key: sections[current_key] = "\n".join(current_lines).strip()
            current_key, current_lines = matched, []
        else:
            current_lines.append(line)
    if current_key: sections[current_key] = "\n".join(current_lines).strip()
    return sections


if __name__ == "__main__":
    test = {"student_name":"Aarav Sharma","exam_title":"Data Structures","subject":"Computer Science",
            "score":88,"correct":26,"wrong":3,"skipped":1,"total":30,"time_taken":32}
    r = generate_report(test)
    print(f"Source: {r['source']}\n\n{r['report']}")
