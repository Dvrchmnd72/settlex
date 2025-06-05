def chat_visibility(request):
    """
    Controls whether the chat widget should be shown based on the current path.
    """
    path = request.path

    # Paths or prefixes where chat should be disabled
    excluded_prefixes = [
        "/login/",
        "/account/login/",
        "/account/two_factor/",
        "/two_factor/",  # Catch any two_factor views
        "/password-reset/",
        "/reset/",
        "/admin/",
    ]

    show_chat = request.user.is_authenticated and not any(path.startswith(prefix) for prefix in excluded_prefixes)

    return {
        "enable_chat": show_chat
    }
