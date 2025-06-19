# RUN
## Run SearXNG
```bash
docker compose up -d
```

## Generate slide
```
python -m libs.main \
			--topic "$(cat topic.txt)" \
			--audience "Small and medium businesses" \
			--duration 20 \
			--purpose "Education and persuasion" \
			--template pptx_templates/Geometric.pptx \
			--output presentation.pptx
```