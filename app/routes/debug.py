from fastapi import APIRouter

router = APIRouter()

@router.post("/debug/echo")
def debug_echo(body: dict):
    def reverse_strings(obj):
        if isinstance(obj, str):
            return obj[::-1]
        elif isinstance(obj, list):
            return [reverse_strings(item) for item in obj]
        elif isinstance(obj, dict):
            return {
                key: obj[key] if key == "preserve" else reverse_strings(v)
                for key, v in obj.items()
            }

        return reverse_strings(body)