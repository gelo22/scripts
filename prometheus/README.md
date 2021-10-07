# get dashboards
kubectl --insecure-skip-tls-verify get configmap -A -l "grafana_dashboard=1" -o yaml > dashboards.yaml

# get rules
kubectl --insecure-skip-tls-verify -n cattle-monitoring-system exec -it prometheus-rancher-monitoring-prometheus-0 -- wget 127.0.0.1:9090/api/v1/rules -O - -q > rules.json

# get metrics
kubectl --insecure-skip-tls-verify -n cattle-monitoring-system exec -it prometheus-rancher-monitoring-prometheus-0 -- wget '127.0.0.1:9090/federate?match[]={job=~".*"}' -O - -q > metrics.txt

grep -o -E 'job="[a-z\-]+"' metrics.txt | sort | uniq -c | sort -hk1

# generate regex for jobs
./get_relabelings.py > out

# Examples

~~~~
kubectl --insecure-skip-tls-verify edit servicemonitor -n default rancher-monitoring-apiserver
    metricRelabelings:
      - sourceLabels: [ __name__ ]
        regex: '^workqueue_depth$|^aggregator_unavailable_apiservice$|^apiserver_client_certificate_expiration_seconds_count$|^workqueue_adds_total$|^apiserver_request_duration_seconds_count$|^apiserver_request_duration_seconds_bucket$|^workqueue_queue_duration_seconds_bucket$|^process_resident_memory_bytes$|^kubernetes_build_info$|^apiserver_request_duration_seconds_sum$|^apiserver_client_certificate_expiration_seconds_bucket$|^apiserver_request_total$'
        action: keep


kubectl --insecure-skip-tls-verify edit servicemonitor -n kube-system rancher-monitoring-kubelet
    metricRelabelings:
      - sourceLabels: [ __name__ ]
        regex: '^kubelet_pleg_relist_duration_seconds_count$|^kubelet_pleg_relist_duration_seconds_bucket$|^kubelet_pleg_relist_interval_seconds_bucket$|^container_network_receive_packets_total$|^kubelet_runtime_operations_errors_total$|^storage_operation_duration_seconds_count$|^container_cpu_cfs_throttled_periods_total$|^kubelet_pod_start_duration_seconds_count$|^container_memory_usage_bytes$|^kubelet_node_name$|^kubelet_node_config_error$|^go_goroutines$|^volume_manager_total_volumes$|^machine_cpu_cores$|^kubelet_runtime_operations_duration_seconds_bucket$|^storage_operation_duration_seconds_bucket$|^container_network_transmit_bytes_total$|^container_memory_working_set_bytes$|^container_network_transmit_packets_total$|^container_network_receive_bytes_total$|^rest_client_request_duration_seconds_bucket$|^storage_operation_errors_total$|^container_memory_swap$|^container_network_receive_packets_dropped_total$|^container_cpu_cfs_periods_total$|^container_memory_cache$|^container_cpu_usage_seconds_total$|^kubelet_pod_worker_duration_seconds_bucket$|^container_memory_rss$|^scrape_error$|^kubelet_pod_worker_duration_seconds_count$|^container_network_transmit_packets_dropped_total$|^kubelet_runtime_operations_total$'
        action: keep


kubectl --insecure-skip-tls-verify edit servicemonitor -n cattle-monitoring-system rancher-monitoring-kube-state-metrics
    metricRelabelings:
      - sourceLabels: [ __name__ ]
        regex: '^kube_daemonset_status_desired_number_scheduled$|^kube_replicaset_owner$|^kube_deployment_status_replicas$|^kube_statefulset_status_replicas$|^kube_pod_container_status_restarts_total$|^kube_pod_owner$|^kube_node_status_capacity$|^kube_node_status_allocatable_cpu_cores$|^kube_statefulset_replicas$|^kube_pod_container_status_waiting_reason$|^kube_node_status_allocatable_memory_bytes$|^kube_statefulset_metadata_generation$|^kube_job_status_succeeded$|^kube_pod_container_resource_limits_memory_bytes$|^kube_daemonset_status_current_number_scheduled$|^kube_statefulset_status_replicas_ready$|^kube_node_status_allocatable$|^kube_statefulset_status_replicas_current$|^kube_deployment_status_replicas_available$|^kube_deployment_spec_replicas$|^kube_job_spec_completions$|^kube_daemonset_status_number_misscheduled$|^kube_node_status_condition$|^kube_pod_container_resource_limits$|^kube_pod_info$|^kube_deployment_status_observed_generation$|^kube_pod_container_resource_limits_cpu_cores$|^kube_pod_container_resource_requests_cpu_cores$|^kube_pod_status_phase$|^kube_deployment_metadata_generation$|^kube_node_status_capacity_pods$|^kube_pod_container_resource_requests$|^kube_pod_container_resource_requests_memory_bytes$|^kube_statefulset_status_current_revision$|^kube_statefulset_status_observed_generation$|^kube_persistentvolume_status_phase$|^kube_pod_container_status_waiting$|^kube_daemonset_status_number_ready$'
        action: keep


kubectl --insecure-skip-tls-verify edit servicemonitor -n ingress-nginx ingress-nginx-controller
    metricRelabelings:
      - sourceLabels: [ __name__ ]
        regex: '^nginx_ingress_controller_nginx_process_connections$|^nginx_ingress_controller_requests$|^nginx_ingress_controller_response_size_sum$|^nginx_ingress_controller_nginx_process_cpu_seconds_total$|^nginx_ingress_controller_request_duration_seconds_bucket$|^nginx_ingress_controller_ssl_expire_time_seconds$|^nginx_ingress_controller_config_last_reload_successful$|^nginx_ingress_controller_nginx_process_resident_memory_bytes$|^nginx_ingress_controller_request_size_sum$|^nginx_ingress_controller_config_hash$|^nginx_ingress_controller_success$|^nginx_ingress_controller_config_last_reload_successful_timestamp_seconds$|^process_start_time_seconds$'
        action: keep


kubectl --insecure-skip-tls-verify edit servicemonitor -n cattle-monitoring-system    rancher-monitoring-node-exporter
    metricRelabelings:
      - sourceLabels: [ __name__ ]
        regex: '^node_memory_Slab_bytes$|^node_disk_read_bytes_total$|^node_memory_Cached_bytes$|^node_nf_conntrack_entries$|^node_filesystem_files_free$|^node_filesystem_readonly$|^node_timex_offset_seconds$|^node_disk_io_time_weighted_seconds_total$|^node_load15$|^node_textfile_scrape_error$|^node_netstat_TcpExt_TCPSynRetrans$|^node_network_receive_bytes_total$|^node_memory_MemAvailable_bytes$|^node_disk_io_time_seconds_total$|^node_load5$|^node_exporter_build_info$|^node_memory_Buffers_bytes$|^node_nf_conntrack_entries_limit$|^node_filesystem_free_bytes$|^node_vmstat_pgmajfault$|^node_cpu_seconds_total$|^node_netstat_Tcp_RetransSegs$|^node_netstat_Tcp_OutSegs$|^node_network_transmit_bytes_total$|^node_disk_written_bytes_total$|^node_memory_MemTotal_bytes$|^node_timex_sync_status$|^node_network_receive_drop_total$|^node_network_receive_errs_total$|^node_filesystem_avail_bytes$|^node_network_transmit_errs_total$|^node_filesystem_files$|^node_load1$|^node_network_transmit_drop_total$|^node_memory_MemFree_bytes$|^node_filesystem_size_bytes$'
        action: keep
~~~~
