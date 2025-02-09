def htmx(request):
    return {"htmx": request.headers.get("HX-Request") is not None}
