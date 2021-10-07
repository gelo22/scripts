# get dashboards
kubectl --insecure-skip-tls-verify get configmap -A -l "grafana_dashboard=1" -o yaml > dashboards.yaml

# get rules
kubectl --insecure-skip-tls-verify -n cattle-monitoring-system exec -it prometheus-rancher-monitoring-prometheus-0 -- wget 127.0.0.1:9090/api/v1/rules -O - -q > rules.json

# get metrics
kubectl --insecure-skip-tls-verify -n cattle-monitoring-system exec -it prometheus-rancher-monitoring-prometheus-0 -- wget '127.0.0.1:9090/federate?match[]={job=~".*"}' -O - -q > metrics.txt

grep -o -E 'job="[a-z\-]+"' metrics.txt | sort | uniq -c | sort -hk1

# generate regex for jobs
./get_relabelings.py > out
