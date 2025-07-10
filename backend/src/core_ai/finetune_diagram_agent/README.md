# Fine-tune Llama 3.1 8B for Diagram Agent (Mermaid Code Generation)

## 1. Chuẩn hóa dữ liệu
- Format: Instruction tuning (input = context + task, output = diagram code)
- File: `data/train.jsonl`, `data/val.jsonl`

## 2. Tạo dữ liệu huấn luyện
- Tạo nhiều cặp input-output đa dạng (slide content, yêu cầu diagram, mermaid code)

## 3. Chuẩn bị môi trường
- Python 3.10+
- `pip install unsloth` (hoặc clone repo Unsloth)
- Ollama đã pull model llama3.1:8b

## 4. Huấn luyện (Không chạy trực tiếp ở đây)
- Sử dụng script `finetune_unsloth.py`
- Cấu hình batch size, epochs, learning rate phù hợp

## 5. Đánh giá
- Sử dụng script `evaluate.py` để so sánh output model với ground truth
- Có thể dùng metrics: syntax validity, diagram type accuracy, BLEU/ROUGE

## 6. Quy trình tổng quát
1. Chuẩn hóa data → `data/train.jsonl`, `data/val.jsonl`
2. Chạy `finetune_unsloth.py` để huấn luyện
3. Chạy `evaluate.py` để đánh giá
4. Deploy model lên Ollama hoặc dùng local inference

---

## File structure
```
finetune_diagram_agent/
    ├── data/
    │   ├── train.jsonl
    │   ├── val.jsonl
    │   └── README.md
    ├── prepare_data.py
    ├── finetune_unsloth.py
    ├── evaluate.py
    └── README.md
```

---
