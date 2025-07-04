run:
	streamlit run app.py

test-slide:
	python -m tests.test_pptx -i outputs/pptx-json/template_test.json -o test.pptx --pdf --template Bosch Weekly Report

test-genslide:
	python -m libs.agents.slide_generator.agent

test-layout:
	python -m libs.agents.slide_generator.schemas

test-create-slide:
	python -m libs.agents.slide_generator.create_presetation

activate:
	pyenv 

searxng-up:
	docker-compose up -d 
searxng-down:
	docker-compose down
run:
	python -m libs.main \
			--topic "$(cat topic.txt)" \
			--audience "Small and medium businesses" \
			--duration 20 \
			--purpose "Education and persuasion" \
			--template "presentation1.pptx" \
			--output presentation.pptx


outline:
	python -m libs.agents.outline_agent.agent

content:
	python -m libs.agents.slide_content_agent.agent

style:
	python -m libs.agents.style_agent.agent