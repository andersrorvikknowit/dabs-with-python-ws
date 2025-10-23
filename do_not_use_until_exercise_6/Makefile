DB_ENV := dev
DATABRICKS_ENV = ${DB_ENV}
PROFILE= ""
export GIT_SHORT_SHA=$(shell git rev-parse --short=8 HEAD)

.PHONY: deploy validate destroy run

validate:
	@echo "Verifying bundle... $$BUNDLE"
	cd ./bundles/$(BUNDLE) && databricks bundle validate -t $(DATABRICKS_ENV) -p $(PROFILE)

deploy: validate
	@echo "deploying bundle... $$BUNDLE"
	uv run deploy_helper.py $(BUNDLE) $(DATABRICKS_ENV) $(PROFILE) $(FLAGS)

destroy:
	@echo "deploying bundle... $$BUNDLE"
	cd ./bundles/$(BUNDLE) && databricks bundle destroy -t $(DATABRICKS_ENV) -p $(PROFILE) $(FLAGS)

run:
	@echo "Running bundle... $$BUNDLE - $$TARGET with flags: $$FLAGS"
	cd ./bundles/$(BUNDLE) && databricks bundle run $(TARGET) -t $(DATABRICKS_ENV) -p $(PROFILE) $(FLAGS)