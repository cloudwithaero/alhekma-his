import frappe

no_cache = 1


def get_context(context):
    context.no_sidebar = 1
    context.no_header = 1
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context
