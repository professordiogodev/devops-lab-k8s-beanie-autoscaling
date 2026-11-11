#!/usr/bin/env python3
import json, os, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
NS = "beanie"
passed = failed = 0


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""))


def k(*a, timeout=120):
    r = subprocess.run(("kubectl",) + a, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def kj(*a):
    rc, out, _ = k(*a, "-o", "json")
    try:
        return json.loads(out) if rc == 0 else None
    except Exception:
        return None


def finish():
    print()
    print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
    sys.exit(1 if failed else 0)


def wait_for(fn, secs, step=5):
    end = time.time() + secs
    while time.time() < end:
        if fn():
            return True
        time.sleep(step)
    return False


print("kubectl context: " + k("config", "current-context")[1].strip())
print("== The autoscalers ==")
check("the metrics API answers (kubectl top works)", k("top", "pods", "-n", NS)[0] == 0, "metrics-server not ready; ./setup.sh installs it")
deps = {d["metadata"]["name"]: d for d in (kj("get", "deployments", "-n", NS) or {}).get("items", [])}
check("Beanie is running (gateway, menu, orders, payments, notifications)", {"gateway", "menu", "orders", "payments", "notifications"} <= set(deps))
hpas = {h["spec"]["scaleTargetRef"]["name"]: h for h in (kj("get", "hpa", "-n", NS) or {}).get("items", []) if h["spec"]["scaleTargetRef"]["kind"] == "Deployment"}
check("an HPA for gateway and one for menu", {"gateway", "menu"} <= set(hpas), "kubectl get hpa -n beanie")
if not {"gateway", "menu"} <= set(hpas):
    finish()
for n in ("gateway", "menu"):
    h = hpas[n]["spec"]
    cpu = next((m for m in h.get("metrics", []) if m["type"] == "Resource" and m["resource"]["name"] == "cpu"), None)
    check("%s: min 2 replicas, max between 4 and 10" % n, h.get("minReplicas", 1) >= 2 and 4 <= h["maxReplicas"] <= 10)
    check("%s: scales on CPU utilisation with a target between 40%% and 80%%" % n, bool(cpu) and cpu["resource"]["target"].get("type") == "Utilization" and 40 <= cpu["resource"]["target"].get("averageUtilization", 0) <= 80)
    sd = h.get("behavior", {}).get("scaleDown", {}).get("stabilizationWindowSeconds")
    check("%s: scale-down stabilisation window is set and at most 120 s (so you do not wait 5 minutes in this lab)" % n, sd is not None and sd <= 120)
for n in ("gateway", "menu"):
    c = deps[n]["spec"]["template"]["spec"]["containers"][0]
    req = c.get("resources", {}).get("requests", {}).get("cpu", "")
    m = int(req[:-1]) if req.endswith("m") else int(float(req or 0) * 1000)
    check("%s: CPU request between 50m and 250m (honest: the HPA percentage is a percentage of THIS number)" % n, 50 <= m <= 250, "request is %s" % (req or "missing"))
ready = wait_for(lambda: all((kj("get", "deployment", n, "-n", NS) or {}).get("status", {}).get("readyReplicas", 0) >= deps[n]["spec"]["replicas"] for n in ("gateway", "menu", "orders", "payments", "notifications")), 120)
check("everything is Ready before the rush", ready)
lr = kj("get", "deployment", "lunch-rush", "-n", NS)
check("the load generator is deployed (kubectl apply -f load/lunch-rush.yaml)", bool(lr))
if not ready or not lr:
    finish()

print("== The lunch rush ==")
k("scale", "deployment/lunch-rush", "-n", NS, "--replicas=3")
t0 = time.time()
base = {n: hpas[n]["spec"]["minReplicas"] for n in ("gateway", "menu")}
def scaled_up():
    return any((kj("get", "deployment", n, "-n", NS) or {}).get("status", {}).get("readyReplicas", 0) > base[n] for n in base)
up = wait_for(scaled_up, 300, 10)
t_up = int(time.time() - t0)
check("under load a Deployment grows beyond its minimum with new pods Ready (took %d s)" % t_up, up, "kubectl get hpa -n beanie; are requests tiny/huge? does the load reach the gateway?")
mx = {n: (kj("get", "deployment", n, "-n", NS) or {}).get("status", {}).get("replicas", 0) for n in base}
print("      replicas at peak so far: %s" % mx)
k("scale", "deployment/lunch-rush", "-n", NS, "--replicas=0")
t1 = time.time()
def back():
    return all((kj("get", "deployment", n, "-n", NS) or {}).get("spec", {}).get("replicas", 99) <= base[n] for n in base)
down = wait_for(back, 480, 10)
check("when the rush ends they shrink back to the minimum (took %d s)" % int(time.time() - t1), down, "scale-down waits for the stabilisation window; is the load really stopped?")
finish()
