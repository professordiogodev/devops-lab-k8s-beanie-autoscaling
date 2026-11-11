# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `k8s/` with your Deployments, Services and HPA
- [ ] `notes.md` with your commands and what you saw (optional)

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste `kubectl top pods` at rest. How did you choose the CPU request for the gateway? What does an HPA percentage mean, a percentage of what?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Paste your HPA manifest. Why `minReplicas` of 2? What happens if the request is missing from the Deployment?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. Run the lunch rush and paste `kubectl get hpa -w` over time. How many seconds passed between the load starting and the first new pod, and between the new pod being created and being Ready? Which one can you shorten and how?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Stop the load and watch it shrink. Why does it take minutes? What is the stabilization window protecting you from?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. The HPA scales on CPU. Name a Beanie service where CPU would be the wrong signal and say which signal you would scale on.

**Your answer:**

<!-- replace this line with your answer -->

### Q6. What is the difference between the HPA and the cluster autoscaler? What happens when the HPA wants 10 pods and the nodes are full?

**Your answer:**

<!-- replace this line with your answer -->

### Q7. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q8. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
