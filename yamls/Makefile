
BITESIZE_PATH =$(HOME)/git/github.com/pearsontechnology/bitesize
KUBECONFIG_A = $(BITESIZE_PATH)/instances/jetstack/kubeconfig-a
KUBECONFIG_B = $(BITESIZE_PATH)/instances/jetstack/kubeconfig-b


ZONES = a b c

APP_NAME = mongo

AWS_PROFILE = bitesize-nonprod
AWS_REGION = eu-west-1

.SECONDEXPANSION:

nodes: export KUBECONFIG := $(KUBECONFIG_A)
nodes:
	env | grep KUBE
	kubectl get nodes

10_create_volumes: kubectl_prepare_A pv_apply

20_create_app_in_A: kubectl_prepare_A app_apply

30_enable_mongo_rs: kubectl_prepare_A mongo_rs_enable

40_enable_svc_in_B: kubectl_prepare_A pods_ips kubectl_prepare_B svc_apply svc_patch_selector_away endpoints_update endpoints_update_a endpoints_update_b endpoints_update_c

50_prepare_svc_in_A: kubectl_prepare_A pods_ips svc_patch_selector_away endpoints_update endpoints_update_a endpoints_update_b endpoints_update_c

60_remove_pod_A: kubectl_prepare_A pods_ips endpoints_update_without_a
61_remove_pod_B: kubectl_prepare_A pods_ips kubectl_prepare_B endpoints_update_without_a
62_scale_down: kubectl_prepare_A scale_down_a
63_move: kubectl_prepare_A export_pv_pvc_deployment_a kubectl_prepare_B import
64_scale_up: kubectl_prepare_B scale_up_a
65_update_endpoints_in_A: kubectl_prepare_B pod_ip_a kubectl_prepare_A pod_ip_b pod_ip_c endpoints_update endpoints_update_a
66_update_endpoints_in_B: kubectl_prepare_A pod_ip_b pod_ip_c kubectl_prepare_B pod_ip_a endpoints_update endpoints_update_a

.ebs_volumes:
	@rm -f $@
	set -e; \
	for zone in $(ZONES); do \
		az=$(AWS_REGION)$$zone; \
		echo $$az; \
		volume_id=`aws ec2 create-volume --availability-zone $$az --volume-type gp2 --size 18 | jq -r '.VolumeId'`; \
		aws ec2 create-tags --resources $$volume_id --tags Key=Name,Value=$(APP_NAME)-$$zone; \
		aws ec2 create-tags --resources $$volume_id --tags Key=Environment,Value=jetstack; \
		echo "VOLUME_$${az}=$${volume_id}" >> .ebs_volumes; \
	done

kubectl_prepare_A:
	@echo "switching to cluster A"
	$(eval KUBECTL := kubectl --kubeconfig=${KUBECONFIG_A})

kubectl_prepare_B:
	echo "switching to cluster B"
	$(eval KUBECTL := kubectl --kubeconfig=${KUBECONFIG_B})

pv_apply: .ebs_volumes
	set -e; \
	for zone in $(ZONES); do \
		volume_id=`cat .ebs_volumes | grep VOLUME_$(AWS_REGION)$$zone | cut -d '=' -f 2`; \
		cat XX-pv.yaml.template | sed "s/%%ZONE%%/$(AWS_REGION)$${zone}/g" | sed "s/%%APP_NAME%%/$(APP_NAME)/g" | sed "s/%%VOLUME_ID%%/$${volume_id}/g"| $(KUBECTL) apply -f -; \
	done

app_apply: ns_apply svc_apply deployment_apply

ns_apply:
	$(KUBECTL) apply -f 05-$(APP_NAME)-namespace.yaml

svc_apply: ns_apply
	$(KUBECTL) apply -f 10-$(APP_NAME)-svc.yaml; \
	set -e; \
	for zone in $(ZONES); do \
		$(KUBECTL) apply -f 10-$(APP_NAME)-$$zone-svc.yaml; \
	done

svc_patch_selector_away:
	$(KUBECTL) patch svc mongo --namespace=mongo --type='json' -p='[{"op": "remove", "path": "/spec/selector"}]'
	for zone in $(ZONES); do \
		$(KUBECTL) patch svc mongo-$$zone --namespace=mongo --type='json' -p='[{"op": "remove", "path": "/spec/selector"}]'; \
	done

pvc_apply: ns_apply
	set -e; \
	for zone in $(ZONES); do \
		$(KUBECTL) apply -f 15-$(APP_NAME)-$$zone-pvc.yaml; \
	done


deployment_apply: pvc_apply
	for zone in $(ZONES); do \
		$(KUBECTL) apply -f 20-$(APP_NAME)-$$zone-deployment.yaml; \
	done

mongo_rs_enable:
	$(eval POD_MONGO_A := $(shell $(KUBECTL) get pods --namespace $(APP_NAME) -l app=$(APP_NAME),zone=$(AWS_REGION)a --output template  --template="{{(index .items 0).metadata.name}}"))
	$(KUBECTL) exec --namespace $(APP_NAME) $(POD_MONGO_A) -- mongo --eval "rs.initiate()"
	$(KUBECTL) exec --namespace $(APP_NAME) $(POD_MONGO_A) -- mongo --eval "rs.add(\"$(APP_NAME)-b\")"
	$(KUBECTL) exec --namespace $(APP_NAME) $(POD_MONGO_A) -- mongo --eval "rs.add(\"$(APP_NAME)-c\")"

pods_ips: pod_ip_a pod_ip_b pod_ip_c

pod_ip_%:
	$(eval POD_IP_$* := $(shell $(KUBECTL) get pods --namespace $(APP_NAME) -l app=$(APP_NAME),zone=$(AWS_REGION)$* --output template  --template="{{(index .items 0).status.podIP}}"))

endpoints_update:
	$(KUBECTL) patch endpoints $(APP_NAME) --namespace=$(APP_NAME) --type='json' -p='[{"op": "replace", "path": "/subsets", "value":[{"addresses":[{"ip":"$(POD_IP_a)"},{"ip":"$(POD_IP_b)"},{"ip":"$(POD_IP_c)"}],"ports":[{"port":27017,"protocol":"TCP"}]}]}]'

endpoints_update_%:
	$(KUBECTL) patch endpoints $(APP_NAME)-$* --namespace=$(APP_NAME) --type='json' -p='[{"op": "replace", "path": "/subsets", "value":[{"addresses":[{"ip":"$(POD_IP_$*)"}],"ports":[{"port":27017,"protocol":"TCP"}]}]}]'

endpoints_update_without_a:
	$(KUBECTL) patch endpoints $(APP_NAME) --namespace=$(APP_NAME) --type='json' -p='[{"op": "replace", "path": "/subsets", "value":[{"addresses":[{"ip":"$(POD_IP_b)"},{"ip":"$(POD_IP_c)"}],"ports":[{"port":27017,"protocol":"TCP"}]}]}]'

endpoints_update_without_b:
	$(KUBECTL) patch endpoints $(APP_NAME) --namespace=$(APP_NAME) --type='json' -p='[{"op": "replace", "path": "/subsets", "value":[{"addresses":[{"ip":"$(POD_IP_a)"},{"ip":"$(POD_IP_c)"}],"ports":[{"port":27017,"protocol":"TCP"}]}]}]'

endpoints_update_without_c:
	$(KUBECTL) patch endpoints $(APP_NAME) --namespace=$(APP_NAME) --type='json' -p='[{"op": "replace", "path": "/subsets", "value":[{"addresses":[{"ip":"$(POD_IP_a)"},{"ip":"$(POD_IP_b)"}],"ports":[{"port":27017,"protocol":"TCP"}]}]}]'

scale_up_%:
	$(KUBECTL) scale deployment $(APP_NAME)-$* --namespace=$(APP_NAME) --replicas=1

scale_down_%:
	$(KUBECTL) scale deployment $(APP_NAME)-$* --namespace=$(APP_NAME) --replicas=0

export_pv_pvc_deployment_%:
	$(KUBECTL) get pvc,deployment $(APP_NAME)-$* --namespace=$(APP_NAME) -o yaml > .deployment-pvc.yaml
	$(KUBECTL) delete -f .deployment-pvc.yaml
	$(KUBECTL) get pv $(APP_NAME)-$(AWS_REGION)$* --namespace=$(APP_NAME) -o yaml > .pv.yaml
	$(KUBECTL) delete -f .pv.yaml

import:
	$(KUBECTL) apply -f .deployment-pvc.yaml -f .pv.yaml
	rm -f .deployment-pvc.yaml .pv.yaml
