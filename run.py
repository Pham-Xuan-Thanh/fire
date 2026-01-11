from common.modeling import Model
# Khởi tạo model Gemini
model = Model(
    model_name='google:gemini-2.5-flash',  # hoặc gemini-1.5-pro
    temperature=0.5,
    max_tokens=2048
)
# Sử dụng để verify claim
from eval.fire.verify_atomic_claim import verify_atomic_claim
result = verify_atomic_claim(
    atomic_claim="Paris is the capital of France",
    rater=model
)