# Stateful app migration A=>B

## Mongo PoC

* See [slides](https://docs.google.com/presentation/d/1n-ecaRCtU34XAsNVBpBm6OwQyIxb-jki8AQPVUXP954/edit?usp=sharing


## [Makefile](yaml/Makefile) approach

* `10_create_volumes` creates AWS ebs volumes in right AZ
* `20_create_app_in_A` creates mongo in cluster A
* `30_enable_mongo_rs` enables replicaset for mongo
* `40_enable_svc_in_B` creates duplicated services in cluster B
* `50_prepare_svc_in_A` migrates to empty selector services in cluster A
* `60_remove_pod_A` removes pod A from client facing service
* `61_remove_pod_B` removes pod A from client facing service
* `62_scale_down` scale down pod A in cluster A
* `63_move` move pv,pvc,demployment  from A to B
* `64_scale_up`: scale up pod A in cluster B
* `65_update_endpoints_in_A` Update service endpoints in Cluster A
* `66_update_endpoints_in_B` Update service endpoints in Cluster B
