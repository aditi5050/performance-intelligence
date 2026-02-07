import redis
import json
import subprocess

# connect redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("Worker started...")

# ==============================
# SMART INSIGHTS ENGINE
# ==============================
def generate_insights(data):

    insights = []

    if data["performance_score"] < 50:
        insights.append("⚠️ Performance score very low — heavy optimization needed")

    if data["lcp"] > 4000 and data["performance_score"] < 80:
        insights.append(
            f"⚠️ LCP too high ({data['lcp']:.0f}ms) — optimize images or reduce render blocking resources"
        )

    if data["cls"] > 0.1:
        insights.append("⚠️ Layout shifts detected — fix CLS issues")

    if data["tbt"] > 300:
        insights.append("⚠️ High Total Blocking Time — reduce heavy JS execution")

    return insights


# ==============================
# REGRESSION DETECTION
# ==============================
def detect_regression(url, new_result):

    history_key = f"history:{url}"

    history = r.lrange(history_key, -2, -1)

    if len(history) == 2:

        prev = json.loads(history[0])
        diff = new_result["performance_score"] - prev["performance_score"]

        if diff < -5:
            return f"🚨 Performance dropped by {abs(diff)} points"

    return None


# ==============================
# FIX SUGGESTION ENGINE
# ==============================
def generate_suggestions(data):

    suggestions = []

    if data["lcp"] > 4000:
        suggestions.append({
            "issue": "Large LCP detected",
            "fix": "<img loading='lazy'> or preload critical images",
            "estimated_improvement_score": 12
        })

    if data["cls"] > 0.1:
        suggestions.append({
            "issue": "Layout shift detected",
            "fix": "Add width and height attributes to images",
            "estimated_improvement_score": 6
        })

    if data["tbt"] > 300:
        suggestions.append({
            "issue": "High JS blocking time",
            "fix": "Use code splitting or dynamic import()",
            "estimated_improvement_score": 10
        })

    return suggestions


# ==============================
# DEEP INTELLIGENCE ENGINE
# ==============================
def generate_deep_insights(data):

    deep = data.get("deep_audits", {})
    advanced = []

    if len(deep.get("render_blocking", [])) > 0:
        advanced.append({
            "issue": "Render blocking resources detected",
            "fix": "Use preload or defer CSS/JS",
            "impact": "Improve LCP and FCP"
        })

    if len(deep.get("unused_js", [])) > 0:
        total_waste = sum(x["wastedBytes"] for x in deep["unused_js"])
        advanced.append({
            "issue": "Large unused JS bundles detected",
            "fix": "Dynamic imports / tree shaking",
            "impact": f"Reduce ~{total_waste//1024}KB JS"
        })

    if len(deep.get("unused_css", [])) > 0:
        total_waste = sum(x["wastedBytes"] for x in deep["unused_css"])
        advanced.append({
            "issue": "Large unused CSS detected",
            "fix": "Use PurgeCSS",
            "impact": f"Reduce ~{total_waste//1024}KB CSS"
        })

    return advanced


# ==============================
# PERFORMANCE PREDICTION
# ==============================
def predict_score(current_score, suggestions):

    improvement = sum(
        s.get("estimated_improvement_score", 0)
        for s in suggestions
    )

    return min(100, current_score + improvement)


# ==============================
# AUTO FIX ENGINE
# ==============================
def generate_code_fixes(data):

    fixes = []

    if data["lcp"] > 4000:
        fixes.append({
            "issue": "High LCP",
            "code_fix_html": "<img loading='lazy' />",
            "code_fix_react": "const Hero = dynamic(() => import('./Hero'), { ssr:false })"
        })

    if data["cls"] > 0.1:
        fixes.append({
            "issue": "Layout shift",
            "code_fix_html": "<img width='400' height='300' />"
        })

    if data["tbt"] > 300:
        fixes.append({
            "issue": "High JS blocking",
            "code_fix_js": "import('./HeavyComponent')"
        })

    return fixes


# ==============================
# SIMULATION ENGINE
# ==============================
def simulate_after_fix(data, suggestions):

    simulated = data.copy()

    for s in suggestions:

        if s["issue"] == "Large LCP detected":
            simulated["lcp"] *= 0.5

        if s["issue"] == "Layout shift detected":
            simulated["cls"] *= 0.3

        if s["issue"] == "High JS blocking time":
            simulated["tbt"] *= 0.5

    return simulated


# ==============================
# ROOT CAUSE ENGINE
# ==============================
def explain_root_cause(data):

    explanation = []

    deep = data.get("deep_audits", {})

    if data["lcp"] > 4000:

        if len(deep.get("unused_js", [])) > 0:
            explanation.append("Heavy unused JS blocking render.")

        elif len(deep.get("unused_css", [])) > 0:
            explanation.append("Large unused CSS delaying render.")

        else:
            explanation.append("Render blocking resources causing slow LCP.")

    return explanation


# ==============================
# WORKER LOOP
# ==============================
while True:

    job = r.blpop("audit_queue")

    if job:

        data = json.loads(job[1])

        job_id = data["id"]
        url = data["url"]

        print("Running audit for:", url)

        result = subprocess.run(
            ["node", "runAudit.js", url],
            capture_output=True,
            text=True
        )

        print("NODE OUTPUT:", result.stdout)

        result_json = json.loads(result.stdout)

        # engines
        result_json["insights"] = generate_insights(result_json)
        result_json["suggestions"] = generate_suggestions(result_json)

        result_json["suggestions"].sort(
            key=lambda x: x["estimated_improvement_score"],
            reverse=True
        )

        result_json["root_cause"] = explain_root_cause(result_json)
        result_json["simulation"] = simulate_after_fix(
            result_json,
            result_json["suggestions"]
        )

        result_json["predicted_score"] = predict_score(
            result_json["performance_score"],
            result_json["suggestions"]
        )

        result_json["deep_insights"] = generate_deep_insights(result_json)
        result_json["code_fixes"] = generate_code_fixes(result_json)

        alert = detect_regression(url, result_json)

        if alert:
            result_json["alert"] = alert
            print(alert)

        final_result = json.dumps(result_json)

        r.set(f"result:{job_id}", final_result)
        r.rpush(f"history:{url}", final_result)

        print("Saved result for job:", job_id)
