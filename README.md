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

## Edit slide
```
python -m libs.main \
    --edit \
    --session-path "memory.json" \
    --section-index 4 \
    --slide-index 2 \
    --edit-prompt "Show information about AI in medical-healthcare, not about marketing and sales" \
    --merge-output-path "updated_presentation.pptx"
```