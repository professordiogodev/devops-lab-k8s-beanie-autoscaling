# What to write in this folder

`k8s/base/` is a working Beanie (the result of the previous labs): five Deployments, five Services, one replica of `orders` (it keeps orders in memory, so it must stay at one).

You write, in `k8s/`:

| File | What |
|------|------|
| `hpa.yaml` | HorizontalPodAutoscalers for `gateway` and `menu` (the two stateless services in front of the load) |

and you change `base/gateway.yaml` and `base/menu.yaml`: the CPU **request** must reflect what the service really uses (measure it, do not guess).

`load/lunch-rush.yaml` is the provided load generator. It starts at 0 replicas.
