import redis
import json
import subprocess

# ==============================
# REDIS CONNECTION
# ==============================
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("🔥 Worker started...")


# ==============================
# SMART INSIGHTS ENGINE
# ==============================
def generate_insights(data):

    insights = []

    if data["performance_score"] < 50:
        insights.append("⚠️ Performance score very low — heavy optimization needed")

    if data["lcp"] > 4000:
        insights.append(f"⚠️ LCP too high ({data['lcp']:.0f}ms)")

    if data["cls"] > 0.1:
        insights.append("⚠️ Layout shifts detected")

    if data["tbt"] > 300:
        insights.append("⚠️ High Total Blocking Time")

    return insights


# ==============================
# AI EXPLANATION ENGINE 😈
# ==============================
def generate_ai_explanation(data):

    explanation = []

    if data["lcp"] > 4000:
        explanation.append(
            "Main content renders late — likely render blocking resources or heavy JS bundles."
        )

    if data["tbt"] > 300:
        explanation.append(
            "Long JavaScript execution blocks user interaction."
        )

    if data["cls"] > 0.1:
        explanation.append(
            "Layout shifts caused by images or dynamic DOM changes."
        )

    deep = data.get("deep_audits", {})

    if len(deep.get("unused_js", [])) > 0:
        explanation.append("Large unused JS increases load time.")

    if len(deep.get("unused_css", [])) > 0:
        explanation.append("Unused CSS slows rendering.")

    return explanation


# ==============================
# REGRESSION DETECTION
# ==============================
def detect_regression(url, new_result):

    history = r.lrange(f"history:{url}", -2, -1)

    if len(history) == 2:
        prev = json.loads(history[0])
        diff = new_result["performance_score"] - prev["performance_score"]

        if diff < -5:
            return f"🚨 Performance dropped by {abs(diff)} points"

    return None


# ==============================
# FIX SUGGESTIONS
# ==============================
def generate_suggestions(data):

    suggestions = []

    if data["lcp"] > 4000:
        suggestions.append({
            "issue": "Large LCP detected",
            "fix": "<img loading='lazy'> or preload hero image",
            "estimated_improvement_score": 12
        })

    if data["cls"] > 0.1:
        suggestions.append({
            "issue": "Layout shift detected",
            "fix": "Add width and height attributes",
            "estimated_improvement_score": 6
        })

    if data["tbt"] > 300:
        suggestions.append({
            "issue": "High JS blocking time",
            "fix": "Use dynamic import() / code splitting",
            "estimated_improvement_score": 10
        })

    return suggestions


# ==============================
# DEEP INTELLIGENCE
# ==============================
def generate_deep_insights(data):

    deep = data.get("deep_audits", {})
    advanced = []

    if deep.get("unused_js"):
        waste = sum(x["wastedBytes"] for x in deep["unused_js"])
        advanced.append({
            "issue": "Unused JavaScript",
            "impact": f"Reduce ~{waste//1024}KB JS"
        })

    if deep.get("unused_css"):
        waste = sum(x["wastedBytes"] for x in deep["unused_css"])
        advanced.append({
            "issue": "Unused CSS",
            "impact": f"Reduce ~{waste//1024}KB CSS"
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
# CODE FIX ENGINE
# ==============================
def generate_code_fixes(data):

    fixes = []

    if data["lcp"] > 4000:
        fixes.append({
            "issue": "High LCP",
            "html": "<img loading='lazy' />",
            "react": "const Hero = dynamic(() => import('./Hero'), { ssr:false })"
        })

    if data["cls"] > 0.1:
        fixes.append({
            "issue": "Layout shift",
            "html": "<img width='400' height='300' />"
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

    return simulated


# ==============================
# WORKER LOOP
# ==============================
while True:

    job = r.blpop("audit_queue")

    if job:

        data = json.loads(job[1])
        job_id = data["id"]
        url = data["url"]

        print("🚀 Running audit:", url)

        result = subprocess.run(
            ["node", "runAudit.js", url],
            capture_output=True,
            text=True
        )

        if not result.stdout:
            print("❌ Empty result from node")
            continue

        result_json = json.loads(result.stdout)

        # engines
        result_json["insights"] = generate_insights(result_json)
        result_json["suggestions"] = generate_suggestions(result_json)

        result_json["suggestions"].sort(
            key=lambda x: x["estimated_improvement_score"],
            reverse=True
        )

        result_json["ai_explanation"] = generate_ai_explanation(result_json)
        result_json["deep_insights"] = generate_deep_insights(result_json)
        result_json["simulation"] = simulate_after_fix(result_json, result_json["suggestions"])
        result_json["predicted_score"] = predict_score(
            result_json["performance_score"],
            result_json["suggestions"]
        )
        result_json["code_fixes"] = generate_code_fixes(result_json)

        alert = detect_regression(url, result_json)

        if alert:
            result_json["alert"] = alert

        final_result = json.dumps(result_json)

        r.set(f"result:{job_id}", final_result)
        r.rpush(f"history:{url}", final_result)

        print("✅ Saved:", job_id)
